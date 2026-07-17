一个简单的脚本，用于替换 Windows 的字体。

字体来源：[更纱黑体](https://github.com/be5invis/Sarasa-Gothic) - [大佬修改版](https://bbs.pcbeta.com/viewthread-1960120-1-4.html) - [大佬原贴的AI整理版本](./字体替换文章整理.md)

工具来源：[字体替换工具](https://www.fishlee.net/soft/sysfontreplacer/)

使用前，在 `en-font` 和 `zh-font` 下放置替换的英文和中文字体。

运行 `backup_fonts.bat`，备份与替换字体同名的系统字体。

```bat
backup_fonts.bat
```

可选参数：

- `--dry-run`：只预览将要备份的字体，不写入文件。
- `--overwrite`：覆盖 `backup` 目录中已存在的同名备份。
- `--windows-fonts 目录`：指定 Windows 字体目录，默认 `C:\Windows\Fonts`。

备份规则：

- `zh-font` 中的同名字体会备份到 `backup\zh`。
- `en-font` 中的同名字体会备份到 `backup\en`。

使用 `字体替换工具`。
