@echo off
echo 使用GCC编译Windows符号链接创建工具...

REM 编译资源文件（可选，如果有windres工具）
if exist symlink_creator.rc (
    windres symlink_creator.rc -O coff -o symlink_creator.res
    echo 编译资源文件完成
)

REM 编译C++源代码
g++ symlink_creator.cpp -o SymlinkCreator.exe -DUNICODE -D_UNICODE -std=c++17 -mwindows -luser32 -lshell32 -lole32 -lcomctl32 -ladvapi32

if %ERRORLEVEL% NEQ 0 (
    echo 编译源代码失败
    exit /b 1
)

echo 编译完成！生成的可执行文件: SymlinkCreator.exe
echo.
echo 提示: 如果需要管理员权限来创建符号链接，请右键点击SymlinkCreator.exe并选择"以管理员身份运行"。 