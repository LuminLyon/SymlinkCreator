import os
import sys
import subprocess
import shutil

def clean_build():
    """清理之前的构建文件"""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    if os.path.exists('symlink_creator.spec'):
        os.remove('symlink_creator.spec')

def build_exe():
    """使用PyInstaller构建可执行文件"""
    try:
        # 确保安装了必要的依赖
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller', 'pyqt5'], check=True)
        
        # 使用PyInstaller构建
        cmd = [
            'pyinstaller',
            '--noconfirm',
            '--onefile',
            '--windowed',
            '--name', 'SymlinkCreator',
            '--add-data', 'icon.ico;.',
            '--icon', 'icon.ico',
            'symlink_creator.py'
        ]
        subprocess.run(cmd, check=True)
        
        print("构建成功！可执行文件位于 dist/SymlinkCreator.exe")
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
    except Exception as e:
        print(f"出现错误: {e}")

if __name__ == "__main__":
    clean_build()
    build_exe() 