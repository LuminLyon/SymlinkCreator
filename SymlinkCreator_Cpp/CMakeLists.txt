cmake_minimum_required(VERSION 3.10)

# 设置项目名称和语言
project(SymlinkCreator VERSION 1.0.0 LANGUAGES CXX)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 强制使用Unicode版本的Win32 API
add_definitions(-DUNICODE -D_UNICODE)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# 添加资源文件
set(RESOURCE_FILES
    symlink_creator.rc
)

# 添加可执行文件
add_executable(SymlinkCreator WIN32 symlink_creator.cpp ${RESOURCE_FILES})

# 定义UNICODE版本
target_compile_definitions(SymlinkCreator PRIVATE 
    UNICODE
    _UNICODE
)

# 添加Windows资源文件
#add_custom_command(
#    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/symlink_creator.rc.obj
#    COMMAND rc.exe /fo ${CMAKE_CURRENT_BINARY_DIR}/symlink_creator.rc.obj ${CMAKE_CURRENT_SOURCE_DIR}/symlink_creator.rc
#    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/symlink_creator.rc
#)
#target_sources(SymlinkCreator PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/symlink_creator.rc.obj)

# 链接必要的库
target_link_libraries(SymlinkCreator PRIVATE 
    comctl32.lib
    ole32.lib    # CoInitialize等函数
    shell32.lib  # SHBrowseForFolder等函数
)

# 指定资源文件编译选项
if(MSVC)
    target_compile_options(SymlinkCreator PRIVATE 
        /W4     # 警告级别
        /O2     # 优化级别
        /Ot     # 使用快速代码优化
        /GL     # 整个程序优化
        /utf-8  # 使用UTF-8源代码
    )
    
    # 链接选项
    set_target_properties(SymlinkCreator PROPERTIES
        LINK_FLAGS "/MANIFEST:NO /LTCG /SUBSYSTEM:WINDOWS"
    )
endif()

# 安装配置
install(TARGETS SymlinkCreator DESTINATION bin)

# 打印完成消息
message(STATUS "SymlinkCreator CMake配置完成") 