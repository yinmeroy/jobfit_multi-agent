"""
OCR处理工具 - 用于识别图片中的文字
支持JPG/PNG格式的图片简历
"""
from PIL import Image
import pytesseract
import subprocess
from config import Config


class OCRHandler:
    """OCR处理器，用于从图片中提取文本"""
    
    def __init__(self):
        """初始化OCR处理器"""
        self.enabled = Config.OCR_ENABLED
        # 配置 Tesseract 路径（支持自定义路径）
        if Config.TESSERACT_PATH and Config.TESSERACT_PATH != 'tesseract':
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
    
    def extract_text_from_image(self, image_path):
        """
        从图片中提取文字
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: 提取的文本内容
        """
        if not self.enabled:
            raise Exception("OCR功能未启用")
        
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 使用pytesseract进行OCR识别
            # lang='chi_sim+eng' 支持中文和英文
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            return text.strip()
        
        except Exception as e:
            error_msg = str(e)
            # 提供更友好的错误提示
            if 'tesseract is not installed' in error_msg.lower() or 'not found' in error_msg.lower():
                raise Exception(
                    f"OCR识别失败: Tesseract未找到。\n"
                    f"请检查配置：\n"
                    f"1. 已安装Tesseract OCR引擎\n"
                    f"2. 在.env文件中设置TESSERACT_PATH为正确路径\n"
                    f"   Windows示例: TESSERACT_PATH=D:\\Program Files\\Tesseract-OCR\\tesseract.exe\n"
                    f"   Linux/Docker示例: TESSERACT_PATH=/usr/bin/tesseract\n"
                    f"当前配置: {Config.TESSERACT_PATH}"
                )
            else:
                raise Exception(f"OCR识别失败: {error_msg}")
    
    def is_image_file(self, filename):
        """
        判断是否为图片文件
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否为图片文件
        """
        image_extensions = {'.jpg', '.jpeg', '.png'}
        ext = filename.lower()[filename.lower().rfind('.'):]
        return ext in image_extensions
