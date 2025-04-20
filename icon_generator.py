import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """创建一个简单的图标"""
    # 创建一个512x512的图像，RGBA模式（带透明度）
    img = Image.new('RGBA', (512, 512), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    draw.ellipse((20, 20, 492, 492), fill=(30, 144, 255, 255))
    
    # 绘制链接符号
    # 左环
    draw.ellipse((100, 196, 250, 346), outline=(255, 255, 255, 255), width=30)
    # 右环
    draw.ellipse((262, 196, 412, 346), outline=(255, 255, 255, 255), width=30)
    
    # 保存为PNG
    img.save('icon.png')
    
    # 尝试转换为ICO格式
    try:
        img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("图标创建成功！")
    except Exception as e:
        print(f"创建ICO格式图标失败: {e}")
        print("尝试安装pillow库...")
        import subprocess
        import sys
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pillow'], check=True)
        img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("图标创建成功！")

if __name__ == "__main__":
    create_icon() 