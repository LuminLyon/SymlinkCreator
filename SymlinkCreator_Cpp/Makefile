# Windows Symlink Creator Makefile
# 使用Visual Studio的cl.exe编译器

# 编译器设置
CC = cl
CFLAGS = /O2 /W4 /EHsc /std:c++17 /D_UNICODE /DUNICODE /utf-8
LDFLAGS = /link user32.lib shell32.lib ole32.lib comctl32.lib advapi32.lib

# 目标文件
TARGET = SymlinkCreator.exe

# 源文件
SRC = symlink_creator.cpp
RC = symlink_creator.rc

# 默认目标
all: $(TARGET)

# 构建目标
$(TARGET): $(SRC) $(RC)
	$(CC) $(CFLAGS) $(SRC) /Fe$@ $(LDFLAGS)
	
# 构建资源文件
resource:
	rc symlink_creator.rc
	
# 清理
clean:
	del /F $(TARGET) *.obj

# Visual Studio环境设置
setup:
	@echo "设置Visual Studio环境..."
	@echo "请运行vcvarsall.bat x86以设置环境变量后再运行此Makefile"
	@echo "例如: C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat x86" 