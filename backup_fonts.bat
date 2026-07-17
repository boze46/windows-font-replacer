@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul

for %%I in ("%~dp0.") do set "ROOT=%%~fI"

set "WINDOWS_FONTS=C:\Windows\Fonts"
set "OVERWRITE=0"
set "DRY_RUN=0"

set /a TOTAL_COPIED=0
set /a TOTAL_SKIPPED=0
set /a TOTAL_MISSING=0
set /a TOTAL_FAILED=0

:parse_args
if "%~1"=="" goto after_args

if /I "%~1"=="--windows-fonts" (
    if "%~2"=="" (
        echo [失败] --windows-fonts 需要目录参数。
        exit /b 2
    )
    set "WINDOWS_FONTS=%~2"
    shift
    shift
    goto parse_args
)

if /I "%~1"=="--overwrite" (
    set "OVERWRITE=1"
    shift
    goto parse_args
)

if /I "%~1"=="--dry-run" (
    set "DRY_RUN=1"
    shift
    goto parse_args
)

if /I "%~1"=="--help" goto usage
if /I "%~1"=="-h" goto usage

echo [失败] 未知参数: %~1
echo.
goto usage

:after_args
net session >nul 2>nul
if errorlevel 1 (
    echo [提示] 当前不是管理员权限。备份通常可正常读取字体；如遇权限不足，请用管理员终端重新运行。
)

if not exist "%WINDOWS_FONTS%\" (
    echo [失败] Windows 字体目录不存在或不可访问: %WINDOWS_FONTS%
    exit /b 2
)

call :backup_group "zh" "zh-font"
call :backup_group "en" "en-font"

echo.
echo 汇总: 复制 %TOTAL_COPIED%, 跳过 %TOTAL_SKIPPED%, 缺失 %TOTAL_MISSING%, 失败 %TOTAL_FAILED%

if not "%TOTAL_MISSING%"=="0" exit /b 1
if not "%TOTAL_FAILED%"=="0" exit /b 1
exit /b 0

:backup_group
set "GROUP=%~1"
set "REPLACE_DIR_NAME=%~2"
set "REPLACE_DIR=%ROOT%\%REPLACE_DIR_NAME%"
set "BACKUP_DIR=%ROOT%\backup\%GROUP%"
set /a GROUP_FILES=0

echo.
echo == 备份 %GROUP%: %REPLACE_DIR_NAME% ==

if not exist "%REPLACE_DIR%\" (
    echo [失败] 缺少目录: %REPLACE_DIR%
    set /a TOTAL_FAILED+=1
    exit /b 0
)

for %%F in ("%REPLACE_DIR%\*") do (
    if exist "%%~fF" if not exist "%%~fF\" if /I not "%%~nxF"==".gitkeep" (
        set /a GROUP_FILES+=1
        call :backup_file "%%~nxF"
    )
)

if "%GROUP_FILES%"=="0" (
    echo [跳过] 目录为空: %REPLACE_DIR%
)

exit /b 0

:backup_file
set "FONT_NAME=%~1"
set "SOURCE=%WINDOWS_FONTS%\%FONT_NAME%"
set "TARGET=%BACKUP_DIR%\%FONT_NAME%"

if not exist "%SOURCE%" (
    echo [缺失] %WINDOWS_FONTS%\%FONT_NAME%
    set /a TOTAL_MISSING+=1
    exit /b 0
)

if exist "%TARGET%" if not "%OVERWRITE%"=="1" (
    echo [跳过] 已存在备份: %TARGET%
    set /a TOTAL_SKIPPED+=1
    exit /b 0
)

if "%DRY_RUN%"=="1" (
    if exist "%TARGET%" (
        echo [预览] 覆盖: %SOURCE% -^> %TARGET%
    ) else (
        echo [预览] 复制: %SOURCE% -^> %TARGET%
    )
    set /a TOTAL_COPIED+=1
    exit /b 0
)

if not exist "%BACKUP_DIR%\" mkdir "%BACKUP_DIR%" >nul 2>nul
if errorlevel 1 (
    echo [失败] 无法创建备份目录: %BACKUP_DIR%
    set /a TOTAL_FAILED+=1
    exit /b 0
)

copy /Y "%SOURCE%" "%TARGET%" >nul 2>nul
if errorlevel 1 (
    echo [失败] 无法复制: %SOURCE% -^> %TARGET%
    set /a TOTAL_FAILED+=1
    exit /b 0
)

echo [完成] %FONT_NAME% -^> %TARGET%
set /a TOTAL_COPIED+=1
exit /b 0

:usage
echo 用法: %~nx0 [--windows-fonts 目录] [--overwrite] [--dry-run]
echo.
echo 按 zh-font/en-font 中的同名字体，从 C:\Windows\Fonts 备份到 backup\zh/en。
echo.
echo   --windows-fonts  指定 Windows 字体目录，默认 C:\Windows\Fonts
echo   --overwrite      覆盖 backup 目录中已存在的同名备份
echo   --dry-run        只打印将要执行的复制操作，不写入文件
exit /b 2
