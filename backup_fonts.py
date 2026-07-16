from __future__ import annotations

import argparse
import ctypes
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WINDOWS_FONTS = Path(r"C:\Windows\Fonts")
GROUPS = {
    "zh": "replace-font-zh",
    "en": "replace-font-en",
}


@dataclass(frozen=True)
class BackupResult:
    copied: int = 0
    skipped: int = 0
    missing: int = 0
    failed: int = 0

    def add(self, **changes: int) -> "BackupResult":
        values = {
            "copied": self.copied,
            "skipped": self.skipped,
            "missing": self.missing,
            "failed": self.failed,
        }
        for key, value in changes.items():
            values[key] += value
        return BackupResult(**values)


def is_windows_admin() -> bool:
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def build_font_index(windows_fonts: Path) -> dict[str, Path]:
    return {
        item.name.casefold(): item
        for item in windows_fonts.iterdir()
        if item.is_file()
    }


def backup_group(
    *,
    root: Path,
    windows_fonts: Path,
    font_index: dict[str, Path],
    group: str,
    replace_dir_name: str,
    overwrite: bool,
    dry_run: bool,
) -> BackupResult:
    replace_dir = root / replace_dir_name
    backup_dir = root / "backup" / group
    result = BackupResult()

    if not replace_dir.is_dir():
        print(f"[失败] 缺少目录: {replace_dir}")
        return result.add(failed=1)

    replace_fonts = sorted(item for item in replace_dir.iterdir() if item.is_file())
    if not replace_fonts:
        print(f"[跳过] 目录为空: {replace_dir}")
        return result

    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    for replace_font in replace_fonts:
        source = font_index.get(replace_font.name.casefold())
        target = backup_dir / replace_font.name

        if source is None:
            print(f"[缺失] {windows_fonts}\\{replace_font.name}")
            result = result.add(missing=1)
            continue

        if target.exists() and not overwrite:
            print(f"[跳过] 已存在备份: {target}")
            result = result.add(skipped=1)
            continue

        if dry_run:
            action = "覆盖" if target.exists() else "复制"
            print(f"[预览] {action}: {source} -> {target}")
            result = result.add(copied=1)
            continue

        try:
            shutil.copy2(source, target)
        except PermissionError:
            print(f"[失败] 权限不足，无法读取或写入: {source} -> {target}")
            result = result.add(failed=1)
        except OSError as exc:
            print(f"[失败] {source} -> {target}: {exc}")
            result = result.add(failed=1)
        else:
            print(f"[完成] {source.name} -> {target}")
            result = result.add(copied=1)

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按 replace-font-zh/en 中的同名字体，从 C:\\Windows\\Fonts 备份到 backup\\zh/en。"
    )
    parser.add_argument(
        "--windows-fonts",
        type=Path,
        default=DEFAULT_WINDOWS_FONTS,
        help="Windows 字体目录，默认 C:\\Windows\\Fonts。",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖 backup 目录中已存在的同名备份。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要执行的复制操作，不写入文件。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    windows_fonts = args.windows_fonts

    if sys.platform == "win32" and not is_windows_admin():
        print("[提示] 当前不是管理员权限。备份通常可正常读取字体；如遇权限不足，请用管理员终端重新运行。")

    if not windows_fonts.is_dir():
        print(f"[失败] Windows 字体目录不存在或不可访问: {windows_fonts}")
        return 2

    try:
        font_index = build_font_index(windows_fonts)
    except PermissionError:
        print(f"[失败] 权限不足，无法读取字体目录: {windows_fonts}")
        return 2
    except OSError as exc:
        print(f"[失败] 无法读取字体目录 {windows_fonts}: {exc}")
        return 2

    total = BackupResult()
    for group, replace_dir_name in GROUPS.items():
        print(f"\n== 备份 {group}: {replace_dir_name} ==")
        result = backup_group(
            root=root,
            windows_fonts=windows_fonts,
            font_index=font_index,
            group=group,
            replace_dir_name=replace_dir_name,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        total = total.add(
            copied=result.copied,
            skipped=result.skipped,
            missing=result.missing,
            failed=result.failed,
        )

    print(
        "\n汇总: "
        f"复制 {total.copied}, "
        f"跳过 {total.skipped}, "
        f"缺失 {total.missing}, "
        f"失败 {total.failed}"
    )
    return 1 if total.missing or total.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
