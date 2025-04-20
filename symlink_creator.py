import os
import sys
import winreg
import ctypes
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QLabel, QWidget, QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize

class SymlinkCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("软链接创建工具")
        self.setFixedSize(400, 300)
        self.initUI()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("Windows 软链接右键菜单工具")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title)
        
        # 安装按钮
        self.install_btn = QPushButton("安装右键菜单")
        self.install_btn.setFont(QFont("Microsoft YaHei", 11))
        self.install_btn.setMinimumHeight(40)
        self.install_btn.clicked.connect(self.install_context_menu)
        layout.addWidget(self.install_btn)
        
        # 卸载按钮
        self.uninstall_btn = QPushButton("卸载右键菜单")
        self.uninstall_btn.setFont(QFont("Microsoft YaHei", 11))
        self.uninstall_btn.setMinimumHeight(40)
        self.uninstall_btn.clicked.connect(self.uninstall_context_menu)
        layout.addWidget(self.uninstall_btn)
        
        # 测试按钮
        self.test_btn = QPushButton("测试创建软链接")
        self.test_btn.setFont(QFont("Microsoft YaHei", 11))
        self.test_btn.setMinimumHeight(40)
        self.test_btn.clicked.connect(self.test_symlink)
        layout.addWidget(self.test_btn)
    
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
    
    def install_context_menu(self):
        """安装右键菜单"""
        if not self.is_admin():
            reply = QMessageBox.question(self, '需要管理员权限', 
                                        '安装右键菜单需要管理员权限，是否以管理员身份重启程序？',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.restart_as_admin()
            return
        
        # 获取程序的完整路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            exe_path = sys.executable
        else:
            # 如果是脚本
            exe_path = os.path.abspath(sys.argv[0])
        
        try:
            # 为文件添加右键菜单
            key_path = r'*\\shell\\创建软链接'
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
            # 设置runas属性显示UAC盾牌图标
            winreg.SetValueEx(key, 'HasLUAShield', 0, winreg.REG_SZ, '')
            command_key = winreg.CreateKey(key, 'command')
            # 使用PowerShell的Start-Process代替，以请求管理员权限
            ps_cmd = f'powershell.exe -Command "Start-Process -FilePath \'{exe_path}\' -ArgumentList \'file\',\'%1\' -Verb RunAs"'
            winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, ps_cmd)
            winreg.CloseKey(command_key)
            winreg.CloseKey(key)
            
            # 为目录添加右键菜单
            key_path = r'Directory\\shell\\创建软链接'
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
            # 设置runas属性显示UAC盾牌图标
            winreg.SetValueEx(key, 'HasLUAShield', 0, winreg.REG_SZ, '')
            command_key = winreg.CreateKey(key, 'command')
            # 使用PowerShell的Start-Process代替，以请求管理员权限
            ps_cmd = f'powershell.exe -Command "Start-Process -FilePath \'{exe_path}\' -ArgumentList \'dir\',\'%1\' -Verb RunAs"'
            winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, ps_cmd)
            winreg.CloseKey(command_key)
            winreg.CloseKey(key)
            
            # 为目录背景添加右键菜单
            key_path = r'Directory\\Background\\shell\\创建软链接到此处'
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
            # 设置runas属性显示UAC盾牌图标
            winreg.SetValueEx(key, 'HasLUAShield', 0, winreg.REG_SZ, '')
            command_key = winreg.CreateKey(key, 'command')
            # 使用PowerShell的Start-Process代替，以请求管理员权限
            ps_cmd = f'powershell.exe -Command "Start-Process -FilePath \'{exe_path}\' -ArgumentList \'target\',\'%V\' -Verb RunAs"'
            winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, ps_cmd)
            winreg.CloseKey(command_key)
            winreg.CloseKey(key)
            
            QMessageBox.information(self, "成功", "右键菜单安装成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"安装右键菜单失败: {e}")
    
    def uninstall_context_menu(self):
        """卸载右键菜单"""
        if not self.is_admin():
            reply = QMessageBox.question(self, '需要管理员权限', 
                                        '卸载右键菜单需要管理员权限，是否以管理员身份重启程序？',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.restart_as_admin()
            return
        
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'*\\shell\\创建软链接\\command')
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'*\\shell\\创建软链接')
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Directory\\shell\\创建软链接\\command')
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Directory\\shell\\创建软链接')
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Directory\\Background\\shell\\创建软链接到此处\\command')
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Directory\\Background\\shell\\创建软链接到此处')
            QMessageBox.information(self, "成功", "右键菜单卸载成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"卸载右键菜单失败: {e}")
    
    def test_symlink(self):
        """测试创建软链接功能"""
        if not self.is_admin():
            QMessageBox.warning(self, "警告", "创建软链接需要管理员权限，请以管理员身份运行程序。")
            return
        
        # 选择源文件/文件夹
        source_path = QFileDialog.getOpenFileName(self, "选择源文件")[0]
        if not source_path:
            return
        
        # 选择目标路径
        target_dir = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if not target_dir:
            return
        
        # 构建目标路径
        target_path = os.path.join(target_dir, os.path.basename(source_path))
        
        # 创建软链接
        try:
            self.create_symlink(source_path, target_path)
            QMessageBox.information(self, "成功", f"软链接创建成功！\n{target_path} -> {source_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建软链接失败: {e}")
    
    def create_symlink(self, source, target):
        """创建软链接"""
        is_dir = os.path.isdir(source)
        try:
            if is_dir:
                # 对于目录使用/D参数
                cmd = f'cmd.exe /c mklink /D "{target}" "{source}"'
            else:
                # 对于文件不使用/D参数
                cmd = f'cmd.exe /c mklink "{target}" "{source}"'
            
            # 使用shell=True并传递完整的命令字符串
            subprocess.run(cmd, shell=True, check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise Exception(f"创建软链接失败: {e.stderr.decode('gbk') if e.stderr else str(e)}")


def handle_command_line():
    """处理命令行参数，用于右键菜单调用"""
    if len(sys.argv) >= 3:
        action = sys.argv[1]
        path = sys.argv[2]
        
        app = QApplication(sys.argv)
        
        if action in ('file', 'dir'):
            # 用户选择了一个文件/文件夹，要求创建软链接
            target_dir = QFileDialog.getExistingDirectory(None, "选择软链接保存位置")
            if not target_dir:
                return
            
            target_path = os.path.join(target_dir, os.path.basename(path))
            
            try:
                is_dir = os.path.isdir(path)
                if is_dir:
                    cmd = f'cmd.exe /c mklink /D "{target_path}" "{path}"'
                else:
                    cmd = f'cmd.exe /c mklink "{target_path}" "{path}"'
                
                subprocess.run(cmd, shell=True, check=True, 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                QMessageBox.information(None, "成功", f"软链接创建成功！\n{target_path} -> {path}")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(None, "错误", f"创建软链接失败: {e.stderr.decode('gbk') if e.stderr else str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "错误", f"创建软链接失败: {e}")
        
        elif action == 'target':
            # 用户在目录背景点击右键，要求创建软链接到此处
            source_path = QFileDialog.getOpenFileName(None, "选择要创建软链接的源文件/文件夹")[0]
            if not source_path:
                return
            
            target_path = os.path.join(path, os.path.basename(source_path))
            
            try:
                is_dir = os.path.isdir(source_path)
                if is_dir:
                    cmd = f'cmd.exe /c mklink /D "{target_path}" "{source_path}"'
                else:
                    cmd = f'cmd.exe /c mklink "{target_path}" "{source_path}"'
                
                subprocess.run(cmd, shell=True, check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                QMessageBox.information(None, "成功", f"软链接创建成功！\n{target_path} -> {source_path}")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(None, "错误", f"创建软链接失败: {e.stderr.decode('gbk') if e.stderr else str(e)}")
            except Exception as e:
                QMessageBox.critical(None, "错误", f"创建软链接失败: {e}")
        
        sys.exit(0)


if __name__ == "__main__":
    # 首先检查是否有命令行参数（来自右键菜单）
    if len(sys.argv) > 1:
        handle_command_line()
    
    # 启动主界面
    app = QApplication(sys.argv)
    window = SymlinkCreator()
    window.show()
    sys.exit(app.exec_()) 