import os
import sys
import winreg
import ctypes
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QLabel, QWidget, QMessageBox, QTextEdit, QHBoxLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 要搜索的所有可能注册路径
ROOT_KEYS = {
    winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
    winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
    winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
    winreg.HKEY_USERS: "HKEY_USERS"
}

# 要搜索的关键词
SEARCH_TERMS = ['软链接', '符号链接', '创建软链接', '创建链接', 'symlink', 'link']

class RegistrySearcher(QThread):
    found_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    
    def __init__(self, search_terms):
        super().__init__()
        self.search_terms = [term.lower() for term in search_terms]
        self.found_items = []
        self.item_count = 0
    
    def run(self):
        """执行全面的注册表扫描"""
        self.progress_signal.emit("开始深度扫描注册表，查找相关的右键菜单项...\n")
        self.progress_signal.emit("提示: 扫描可能需要几分钟时间，请耐心等待...\n")
        
        # 扫描所有根键
        for root_key, root_name in ROOT_KEYS.items():
            self.progress_signal.emit(f"正在扫描 {root_name}...")
            
            if root_key == winreg.HKEY_CLASSES_ROOT:
                # 扫描文件和目录相关的右键菜单
                self.scan_key(root_key, "*\\shell")
                self.scan_key(root_key, "Directory\\shell")
                self.scan_key(root_key, "Directory\\Background\\shell")
                self.scan_key(root_key, "Drive\\shell")
                self.scan_key(root_key, "Folder\\shell")
                
                # 扫描shellex菜单处理程序
                self.scan_key(root_key, "*\\shellex\\ContextMenuHandlers")
                self.scan_key(root_key, "Directory\\shellex\\ContextMenuHandlers")
                self.scan_key(root_key, "Folder\\shellex\\ContextMenuHandlers")
                
                # 对HKCR进行更深入的扫描
                self.scan_file_types(root_key)
            
            elif root_key == winreg.HKEY_CURRENT_USER:
                # 扫描用户级别的文件和目录相关右键菜单
                self.scan_key(root_key, "Software\\Classes\\*\\shell")
                self.scan_key(root_key, "Software\\Classes\\Directory\\shell")
                self.scan_key(root_key, "Software\\Classes\\Directory\\Background\\shell")
                
                # 扫描用户级别的shellex菜单处理程序
                self.scan_key(root_key, "Software\\Classes\\*\\shellex\\ContextMenuHandlers")
                self.scan_key(root_key, "Software\\Classes\\Directory\\shellex\\ContextMenuHandlers")
                
                # 额外扫描Windows资源管理器上下文菜单处理程序
                self.scan_key(root_key, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ContextMenuHandlers")
            
            elif root_key == winreg.HKEY_LOCAL_MACHINE:
                # 扫描系统级别的文件和目录相关右键菜单
                self.scan_key(root_key, "SOFTWARE\\Classes\\*\\shell")
                self.scan_key(root_key, "SOFTWARE\\Classes\\Directory\\shell")
                self.scan_key(root_key, "SOFTWARE\\Classes\\Directory\\Background\\shell")
                
                # 扫描系统级别的shellex菜单处理程序
                self.scan_key(root_key, "SOFTWARE\\Classes\\*\\shellex\\ContextMenuHandlers")
                self.scan_key(root_key, "SOFTWARE\\Classes\\Directory\\shellex\\ContextMenuHandlers")
                
                # 扫描CLSID (可能包含右键菜单处理程序)
                self.scan_key(root_key, "SOFTWARE\\Classes\\CLSID")
        
        self.progress_signal.emit(f"\n扫描完成，共找到 {self.item_count} 个相关菜单项。")
        self.finished_signal.emit(self.item_count)
    
    def scan_file_types(self, root_key):
        """扫描文件类型关联的右键菜单"""
        try:
            i = 0
            with winreg.OpenKey(root_key, "") as key:
                while True:
                    try:
                        file_type = winreg.EnumKey(key, i)
                        
                        # 检查该文件类型是否有shell子键
                        self.scan_key(root_key, f"{file_type}\\shell")
                        self.scan_key(root_key, f"{file_type}\\shellex\\ContextMenuHandlers")
                        
                        i += 1
                    except WindowsError:
                        break
        except Exception as e:
            self.progress_signal.emit(f"扫描文件类型时出错: {e}")
    
    def scan_key(self, root_key, path):
        """扫描指定注册表路径下的菜单项"""
        try:
            with winreg.OpenKey(root_key, path) as key:
                # 枚举该键下的所有子键
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        
                        # 检查子键名是否包含搜索关键词
                        for term in self.search_terms:
                            if term.lower() in subkey_name.lower():
                                full_path = f"{path}\\{subkey_name}"
                                self.add_menu_item(root_key, full_path)
                                
                                # 检查该项是否有command子键
                                try:
                                    cmd_path = f"{full_path}\\command"
                                    with winreg.OpenKey(root_key, cmd_path):
                                        self.add_menu_item(root_key, cmd_path)
                                except:
                                    pass
                                
                                break
                        
                        # 检查命令值中是否包含关键词
                        try:
                            cmd_path = f"{path}\\{subkey_name}\\command"
                            with winreg.OpenKey(root_key, cmd_path) as cmd_key:
                                try:
                                    cmd_value, _ = winreg.QueryValueEx(cmd_key, "")
                                    if isinstance(cmd_value, str):
                                        for term in self.search_terms:
                                            if term.lower() in cmd_value.lower():
                                                self.add_menu_item(root_key, f"{path}\\{subkey_name}")
                                                self.add_menu_item(root_key, cmd_path)
                                                break
                                except:
                                    pass
                        except:
                            pass
                        
                        i += 1
                    except WindowsError:
                        break
        except:
            pass
    
    def add_menu_item(self, hkey, path):
        """添加菜单项到结果列表"""
        root_name = ROOT_KEYS.get(hkey, str(hkey))
        
        # 创建项目
        item = {
            'hkey': hkey,
            'path': path,
            'display': f"{root_name}\\{path}"
        }
        
        # 尝试获取默认值
        try:
            with winreg.OpenKey(hkey, path) as key:
                value, _ = winreg.QueryValueEx(key, "")
                if value:
                    item['default_value'] = value
        except:
            pass
        
        # 添加到列表并发出信号
        self.found_items.append(item)
        self.found_signal.emit(item)
        self.item_count += 1

class RegistryCleaner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.found_items = []
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("软链接右键菜单专项清理工具")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("软链接右键菜单专项清理工具")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title)
        
        # 说明
        desc = QLabel('本工具会深度扫描注册表中所有与"软链接"、"创建链接"等相关的右键菜单项，并允许您清除它们。')
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        # 按钮栏
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("开始扫描")
        self.scan_btn.setFont(QFont("Microsoft YaHei", 10))
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_btn)
        
        self.clean_btn = QPushButton("清理所有项")
        self.clean_btn.setFont(QFont("Microsoft YaHei", 10))
        self.clean_btn.setMinimumHeight(40)
        self.clean_btn.clicked.connect(self.clean_registry)
        self.clean_btn.setEnabled(False)
        button_layout.addWidget(self.clean_btn)
        
        self.restart_btn = QPushButton("重启资源管理器")
        self.restart_btn.setFont(QFont("Microsoft YaHei", 10))
        self.restart_btn.setMinimumHeight(40)
        self.restart_btn.clicked.connect(self.restart_explorer)
        button_layout.addWidget(self.restart_btn)
        
        layout.addLayout(button_layout)
        
        # 日志区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_area)
        
        self.log("欢迎使用软链接右键菜单专项清理工具")
        self.log("此工具将帮助您找到并清理所有与\"创建软链接\"相关的右键菜单项")
        self.log("注意：此操作需要管理员权限，请确保以管理员身份运行本程序")
        self.log("-----------------------------------------------------")
    
    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def restart_as_admin(self):
        """以管理员权限重启程序"""
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    
    def start_scan(self):
        """开始扫描注册表"""
        if not self.is_admin():
            reply = QMessageBox.question(self, '需要管理员权限', 
                                        '扫描注册表需要管理员权限，是否以管理员身份重启程序？',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.restart_as_admin()
            return
        
        # 清空之前的结果
        self.log_area.clear()
        self.found_items = []
        self.clean_btn.setEnabled(False)
        
        self.log("开始深度扫描注册表中与「软链接」相关的菜单项...")
        
        # 创建并启动搜索线程
        self.searcher = RegistrySearcher(SEARCH_TERMS)
        self.searcher.found_signal.connect(self.on_item_found)
        self.searcher.progress_signal.connect(self.log)
        self.searcher.finished_signal.connect(self.on_scan_finished)
        self.searcher.start()
        
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("正在扫描...")
    
    def on_item_found(self, item):
        """处理找到的项目"""
        self.found_items.append(item)
        self.log(f"找到: {item['display']}")
        if 'default_value' in item:
            self.log(f"  > 默认值: {item['default_value']}")
    
    def on_scan_finished(self, count):
        """扫描完成的处理"""
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("重新扫描")
        
        if count > 0:
            self.clean_btn.setEnabled(True)
            self.log(f"\n扫描完成，共发现 {count} 个相关菜单项。点击\"清理所有项\"删除它们。")
        else:
            self.log("\n扫描完成，未发现相关菜单项。")
    
    def clean_registry(self):
        """清理找到的注册表项"""
        if not self.found_items:
            return
        
        reply = QMessageBox.question(self, '确认清理', 
                                    f'确定要删除找到的 {len(self.found_items)} 个注册表项吗？\n此操作不可恢复。',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        self.log("\n开始清理注册表项...")
        
        # 按路径深度排序，先删除深层路径
        self.found_items.sort(key=lambda x: x['path'].count('\\'), reverse=True)
        
        # 按照"由内而外"的顺序删除
        success_count = 0
        error_count = 0
        
        for item in self.found_items:
            # 检查是否有command子键，如果有则先删除command子键
            if "\\command" not in item['path'] and self.has_command_subkey(item['hkey'], item['path']):
                command_path = f"{item['path']}\\command"
                try:
                    winreg.DeleteKey(item['hkey'], command_path)
                    self.log(f"已删除: {ROOT_KEYS.get(item['hkey'])}\\{command_path}")
                    success_count += 1
                except Exception as e:
                    self.log(f"删除失败: {ROOT_KEYS.get(item['hkey'])}\\{command_path} - {str(e)}")
                    error_count += 1
            
            # 删除项本身
            try:
                winreg.DeleteKey(item['hkey'], item['path'])
                self.log(f"已删除: {item['display']}")
                success_count += 1
            except Exception as e:
                self.log(f"删除失败: {item['display']} - {str(e)}")
                error_count += 1
        
        if success_count > 0:
            self.log(f"\n清理完成! 成功删除 {success_count} 项，失败 {error_count} 项。")
            self.log("请点击\"重启资源管理器\"按钮使更改生效，或重启计算机。")
            
            # 清空列表并禁用清理按钮
            self.found_items = []
            self.clean_btn.setEnabled(False)
        else:
            self.log("\n清理失败，未能删除任何项。请尝试重启计算机后再试。")
    
    def has_command_subkey(self, hkey, path):
        """检查是否有command子键"""
        try:
            command_path = f"{path}\\command"
            with winreg.OpenKey(hkey, command_path):
                return True
        except:
            return False
    
    def restart_explorer(self):
        """重启资源管理器以使更改立即生效"""
        try:
            self.log("\n正在重启资源管理器...")
            # 结束资源管理器进程
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 重新启动资源管理器
            subprocess.Popen("explorer.exe")
            
            self.log("资源管理器已重启，更改应已生效。")
            self.log("如果右键菜单项仍然存在，请尝试重启电脑。")
        except Exception as e:
            self.log(f"重启资源管理器失败: {str(e)}")
            self.log("请手动重启电脑以使更改生效。")
    
    def log(self, message):
        """添加日志信息"""
        self.log_area.append(message)
        # 滚动到底部
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

def main():
    app = QApplication(sys.argv)
    window = RegistryCleaner()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # 检查是否以管理员身份运行
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    else:
        main() 