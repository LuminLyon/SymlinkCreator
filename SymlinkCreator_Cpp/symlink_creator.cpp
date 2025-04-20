#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif

// 这些定义必须在包含Windows头文件之前
#include <windows.h>
#include <shlobj.h>
#include <commctrl.h>
#include <string>
#include <fstream>
#include <filesystem>
#include <codecvt>
#include <locale>

#pragma comment(lib, "comctl32.lib")
#pragma comment(linker, "/manifestdependency:\"type='win32' name='Microsoft.Windows.Common-Controls' version='6.0.0.0' processorArchitecture='*' publicKeyToken='6595b64144ccf1df' language='*'\"")

// 全局变量
HINSTANCE g_hInstance = NULL;
const wchar_t* APP_NAME = L"软链接创建工具";
const wchar_t* MENU_NAME_FILE = L"创建软链接";
const wchar_t* MENU_NAME_DIR = L"创建软链接";
const wchar_t* MENU_NAME_BACKGROUND = L"创建软链接到此处";

// 函数声明
bool IsRunAsAdmin();
bool RegisterContextMenu();
bool UnregisterContextMenu();
bool CreateSymlink(const std::wstring& source, const std::wstring& target);
bool TestSymlink(HWND hwnd);
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);

// 将std::wstring转换为std::string
std::string WideToUtf8(const std::wstring& wstr) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
    return converter.to_bytes(wstr);
}

// 将std::string转换为std::wstring
std::wstring Utf8ToWide(const std::string& str) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
    return converter.from_bytes(str);
}

// 检查是否以管理员身份运行
bool IsRunAsAdmin() {
    BOOL isAdmin = FALSE;
    SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;
    PSID adminGroup = NULL;
    
    // 创建管理员组的SID
    if (AllocateAndInitializeSid(&ntAuthority, 2, SECURITY_BUILTIN_DOMAIN_RID,
                               DOMAIN_ALIAS_RID_ADMINS, 0, 0, 0, 0, 0, 0, &adminGroup)) {
        // 检查当前用户是否属于管理员组
        if (!CheckTokenMembership(NULL, adminGroup, &isAdmin)) {
            isAdmin = FALSE;
        }
        FreeSid(adminGroup);
    }
    
    return (isAdmin != FALSE);
}

// 重启为管理员权限
void RestartAsAdmin(HWND hwnd) {
    wchar_t szPath[MAX_PATH];
    GetModuleFileNameW(NULL, szPath, MAX_PATH);
    
    SHELLEXECUTEINFOW sei = {0};
    sei.cbSize = sizeof(SHELLEXECUTEINFOW);
    sei.lpVerb = L"runas";
    sei.lpFile = szPath;
    sei.hwnd = hwnd;
    sei.nShow = SW_NORMAL;
    
    if (!ShellExecuteExW(&sei)) {
        MessageBoxW(hwnd, L"无法以管理员身份启动程序。", APP_NAME, MB_ICONERROR);
    }
}

// 注册右键菜单
bool RegisterContextMenu() {
    HKEY hKey;
    DWORD dwDisp;
    wchar_t szPath[MAX_PATH];
    GetModuleFileNameW(NULL, szPath, MAX_PATH);
    
    // 在文件上的右键菜单
    if (RegCreateKeyExW(HKEY_CLASSES_ROOT, L"*\\shell\\创建软链接", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisp) == ERROR_SUCCESS) {
        RegSetValueExW(hKey, L"HasLUAShield", 0, REG_SZ, (BYTE*)L"", 2);
        RegCloseKey(hKey);
        
        if (RegCreateKeyExW(HKEY_CLASSES_ROOT, L"*\\shell\\创建软链接\\command", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisp) == ERROR_SUCCESS) {
            std::wstring command = L"powershell.exe -Command \"Start-Process -FilePath \\\"" + std::wstring(szPath) + L"\\\" -ArgumentList \\\"file\\\",\\\"%1\\\" -Verb RunAs\"";
            RegSetValueExW(hKey, L"", 0, REG_SZ, (BYTE*)command.c_str(), (DWORD)((command.length() + 1) * sizeof(wchar_t)));
            RegCloseKey(hKey);
        }
    }
    
    // 在目录上的右键菜单
    if (RegCreateKeyExW(HKEY_CLASSES_ROOT, L"Directory\\shell\\创建软链接", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisp) == ERROR_SUCCESS) {
        RegSetValueExW(hKey, L"HasLUAShield", 0, REG_SZ, (BYTE*)L"", 2);
        RegCloseKey(hKey);
        
        if (RegCreateKeyExW(HKEY_CLASSES_ROOT, L"Directory\\shell\\创建软链接\\command", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisp) == ERROR_SUCCESS) {
            std::wstring command = L"powershell.exe -Command \"Start-Process -FilePath \\\"" + std::wstring(szPath) + L"\\\" -ArgumentList \\\"dir\\\",\\\"%1\\\" -Verb RunAs\"";
            RegSetValueExW(hKey, L"", 0, REG_SZ, (BYTE*)command.c_str(), (DWORD)((command.length() + 1) * sizeof(wchar_t)));
            RegCloseKey(hKey);
        }
    }
    
    // 在目录背景上的右键菜单
    if (RegCreateKeyExW(HKEY_CLASSES_ROOT, L"Directory\\Background\\shell\\创建软链接到此处", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisp) == ERROR_SUCCESS) {
        RegSetValueExW(hKey, L"HasLUAShield", 0, REG_SZ, (BYTE*)L"", 2);
        RegCloseKey(hKey);
        
        if (RegCreateKeyExW(HKEY_CLASSES_ROOT, L"Directory\\Background\\shell\\创建软链接到此处\\command", 0, NULL, 0, KEY_WRITE, NULL, &hKey, &dwDisp) == ERROR_SUCCESS) {
            std::wstring command = L"powershell.exe -Command \"Start-Process -FilePath \\\"" + std::wstring(szPath) + L"\\\" -ArgumentList \\\"target\\\",\\\"%V\\\" -Verb RunAs\"";
            RegSetValueExW(hKey, L"", 0, REG_SZ, (BYTE*)command.c_str(), (DWORD)((command.length() + 1) * sizeof(wchar_t)));
            RegCloseKey(hKey);
        }
    }
    
    return true;
}

// 卸载右键菜单
bool UnregisterContextMenu() {
    // 删除文件右键菜单
    RegDeleteKeyW(HKEY_CLASSES_ROOT, L"*\\shell\\创建软链接\\command");
    RegDeleteKeyW(HKEY_CLASSES_ROOT, L"*\\shell\\创建软链接");
    
    // 删除目录右键菜单
    RegDeleteKeyW(HKEY_CLASSES_ROOT, L"Directory\\shell\\创建软链接\\command");
    RegDeleteKeyW(HKEY_CLASSES_ROOT, L"Directory\\shell\\创建软链接");
    
    // 删除目录背景右键菜单
    RegDeleteKeyW(HKEY_CLASSES_ROOT, L"Directory\\Background\\shell\\创建软链接到此处\\command");
    RegDeleteKeyW(HKEY_CLASSES_ROOT, L"Directory\\Background\\shell\\创建软链接到此处");
    
    return true;
}

// 创建软链接
bool CreateSymlink(const std::wstring& source, const std::wstring& target) {
    bool isDirectory = std::filesystem::is_directory(source);
    
    DWORD dwFlags = isDirectory ? SYMBOLIC_LINK_FLAG_DIRECTORY : 0;
    
    // 在Windows 10创造者更新以后需要添加此标志以便于在开发者模式下不需要管理员权限
    dwFlags |= SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE;
    
    if (CreateSymbolicLinkW(target.c_str(), source.c_str(), dwFlags)) {
        return true;
    }
    
    // 如果带SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE失败，尝试不带此标志
    if (GetLastError() == ERROR_INVALID_PARAMETER) {
        dwFlags = isDirectory ? SYMBOLIC_LINK_FLAG_DIRECTORY : 0;
        return CreateSymbolicLinkW(target.c_str(), source.c_str(), dwFlags) != 0;
    }
    
    return false;
}

// 测试软链接创建功能
bool TestSymlink(HWND hwnd) {
    // 选择源文件
    wchar_t szFileName[MAX_PATH] = {0};
    
    OPENFILENAMEW ofn = {0};
    ofn.lStructSize = sizeof(OPENFILENAMEW);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = L"所有文件\0*.*\0";
    ofn.lpstrFile = szFileName;
    ofn.nMaxFile = MAX_PATH;
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
    
    if (!GetOpenFileNameW(&ofn)) {
        return false;
    }
    
    // 选择目标文件夹
    wchar_t szFolderPath[MAX_PATH] = {0};
    
    BROWSEINFOW bi = {0};
    bi.hwndOwner = hwnd;
    bi.lpszTitle = L"选择软链接保存位置";
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE;
    
    LPITEMIDLIST pidl = SHBrowseForFolderW(&bi);
    if (pidl == NULL) {
        return false;
    }
    
    SHGetPathFromIDListW(pidl, szFolderPath);
    CoTaskMemFree(pidl);
    
    // 构建目标路径
    std::filesystem::path sourcePath(szFileName);
    std::wstring targetPath = std::wstring(szFolderPath) + L"\\" + sourcePath.filename().wstring();
    
    // 创建软链接
    if (CreateSymlink(szFileName, targetPath)) {
        MessageBoxW(hwnd, (L"软链接创建成功！\n" + targetPath + L" -> " + std::wstring(szFileName)).c_str(), APP_NAME, MB_ICONINFORMATION);
        return true;
    } else {
        wchar_t szError[256];
        FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM, NULL, GetLastError(), 0, szError, 255, NULL);
        MessageBoxW(hwnd, (L"创建软链接失败: " + std::wstring(szError)).c_str(), APP_NAME, MB_ICONERROR);
        return false;
    }
}

// 处理命令行
bool HandleCommandLine(int argc, wchar_t* argv[]) {
    if (argc < 3) {
        return false;
    }
    
    std::wstring action = argv[1];
    std::wstring path = argv[2];
    
    if (action == L"file" || action == L"dir") {
        // 用户选择了一个文件/文件夹，要求创建软链接
        wchar_t szFolderPath[MAX_PATH] = {0};
        
        BROWSEINFOW bi = {0};
        bi.lpszTitle = L"选择软链接保存位置";
        bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE;
        
        LPITEMIDLIST pidl = SHBrowseForFolderW(&bi);
        if (pidl == NULL) {
            return false;
        }
        
        SHGetPathFromIDListW(pidl, szFolderPath);
        CoTaskMemFree(pidl);
        
        // 构建目标路径
        std::filesystem::path sourcePath(path);
        std::wstring targetPath = std::wstring(szFolderPath) + L"\\" + sourcePath.filename().wstring();
        
        // 创建软链接
        if (CreateSymlink(path, targetPath)) {
            MessageBoxW(NULL, (L"软链接创建成功！\n" + targetPath + L" -> " + path).c_str(), APP_NAME, MB_ICONINFORMATION);
            return true;
        } else {
            wchar_t szError[256];
            FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM, NULL, GetLastError(), 0, szError, 255, NULL);
            MessageBoxW(NULL, (L"创建软链接失败: " + std::wstring(szError)).c_str(), APP_NAME, MB_ICONERROR);
            return false;
        }
    } else if (action == L"target") {
        // 用户选择了一个目标文件夹，要求创建软链接到该文件夹
        wchar_t szFileName[MAX_PATH] = {0};
        
        OPENFILENAMEW ofn = {0};
        ofn.lStructSize = sizeof(OPENFILENAMEW);
        ofn.lpstrFilter = L"所有文件\0*.*\0";
        ofn.lpstrFile = szFileName;
        ofn.nMaxFile = MAX_PATH;
        ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
        
        if (!GetOpenFileNameW(&ofn)) {
            return false;
        }
        
        // 构建目标路径
        std::filesystem::path sourcePath(szFileName);
        std::wstring targetPath = path + L"\\" + sourcePath.filename().wstring();
        
        // 创建软链接
        if (CreateSymlink(szFileName, targetPath)) {
            MessageBoxW(NULL, (L"软链接创建成功！\n" + targetPath + L" -> " + std::wstring(szFileName)).c_str(), APP_NAME, MB_ICONINFORMATION);
            return true;
        } else {
            wchar_t szError[256];
            FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM, NULL, GetLastError(), 0, szError, 255, NULL);
            MessageBoxW(NULL, (L"创建软链接失败: " + std::wstring(szError)).c_str(), APP_NAME, MB_ICONERROR);
            return false;
        }
    }
    
    return false;
}

// 主窗口过程
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE:
            if (!IsRunAsAdmin()) {
                MessageBoxW(hwnd, L"警告：没有管理员权限，创建符号链接可能会失败。", APP_NAME, MB_ICONWARNING);
            }
            break;
            
        case WM_COMMAND:
            switch (LOWORD(wParam)) {
                case 1:  // 创建软链接
                    TestSymlink(hwnd);
                    break;
                case 2:  // 注册右键菜单
                    if (RegisterContextMenu()) {
                        MessageBoxW(hwnd, L"右键菜单注册成功！", APP_NAME, MB_ICONINFORMATION);
                    } else {
                        MessageBoxW(hwnd, L"右键菜单注册失败！", APP_NAME, MB_ICONERROR);
                    }
                    break;
                case 3:  // 卸载右键菜单
                    if (UnregisterContextMenu()) {
                        MessageBoxW(hwnd, L"右键菜单卸载成功！", APP_NAME, MB_ICONINFORMATION);
                    } else {
                        MessageBoxW(hwnd, L"右键菜单卸载失败！", APP_NAME, MB_ICONERROR);
                    }
                    break;
                case 4:  // 退出
                    DestroyWindow(hwnd);
                    break;
            }
            break;
            
        case WM_CLOSE:
            DestroyWindow(hwnd);
            break;
            
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
            
        default:
            return DefWindowProcW(hwnd, msg, wParam, lParam);
    }
    return 0;
}

// 添加WinMain函数以解决GCC链接问题
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // 只需简单地调用wWinMain，将参数转换为Unicode版本
    LPWSTR wszCmdLine = GetCommandLineW();
    return wWinMain(hInstance, hPrevInstance, wszCmdLine, nCmdShow);
}

// 原始wWinMain函数入口点
int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nCmdShow) {
    g_hInstance = hInstance;
    
    // 尝试解析命令行
    int argc = 0;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (argv != NULL && argc > 1) {
        if (HandleCommandLine(argc, argv)) {
            LocalFree(argv);
            return 0;
        }
        LocalFree(argv);
    }
    
    // 注册窗口类
    WNDCLASSEXW wc = {0};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hIcon = LoadIconW(NULL, IDI_APPLICATION);
    wc.hCursor = LoadCursorW(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = L"SymlinkCreatorClass";
    wc.hIconSm = LoadIconW(NULL, IDI_APPLICATION);
    
    if (!RegisterClassExW(&wc)) {
        MessageBoxW(NULL, L"窗口注册失败！", APP_NAME, MB_ICONERROR);
        return 0;
    }
    
    // 创建窗口
    HWND hwnd = CreateWindowExW(
        0,
        L"SymlinkCreatorClass",
        APP_NAME,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 400, 300,
        NULL, NULL, hInstance, NULL
    );
    
    if (hwnd == NULL) {
        MessageBoxW(NULL, L"窗口创建失败！", APP_NAME, MB_ICONERROR);
        return 0;
    }
    
    // 创建按钮
    CreateWindowExW(0, L"BUTTON", L"创建软链接", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
                  20, 20, 150, 30, hwnd, (HMENU)1, hInstance, NULL);
                  
    CreateWindowExW(0, L"BUTTON", L"注册右键菜单", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
                  200, 20, 150, 30, hwnd, (HMENU)2, hInstance, NULL);
                  
    CreateWindowExW(0, L"BUTTON", L"卸载右键菜单", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
                  20, 70, 150, 30, hwnd, (HMENU)3, hInstance, NULL);
                  
    CreateWindowExW(0, L"BUTTON", L"退出", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
                  200, 70, 150, 30, hwnd, (HMENU)4, hInstance, NULL);
    
    // 显示窗口
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);
    
    // 消息循环
    MSG msg;
    while (GetMessageW(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    
    return (int)msg.wParam;
} 