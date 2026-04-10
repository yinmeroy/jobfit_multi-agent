"""
文件解析工具 - 支持PDF/DOCX/TXT/JPG/PNG格式
"""
import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
import chardet
from .ocr_handler import OCRHandler


class FileParser:
    """文件解析器"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析PDF文件"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """解析DOCX文件"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"DOCX解析失败: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """解析TXT文件(自动检测编码)"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"TXT解析失败: {str(e)}")
    
    @staticmethod
    def parse_image(file_path: str) -> str:
        """解析图片文件(JPG/PNG)，使用OCR提取文字"""
        try:
            ocr_handler = OCRHandler()
            text = ocr_handler.extract_text_from_image(file_path)
            
            if not text or len(text.strip()) == 0:
                raise Exception("OCR识别未提取到有效文本，请确保图片清晰且包含可读文字")
            
            return text
        except Exception as e:
            raise Exception(f"图片OCR解析失败: {str(e)}")
    
    @staticmethod
    def parse_file(file_path: str, file_extension: str) -> str:
        """
        根据文件扩展名选择合适的解析器
        
        Args:
            file_path: 文件路径
            file_extension: 文件扩展名(不含点，如 'pdf', 'jpg')
            
        Returns:
            解析后的文本内容
        """
        ext_lower = file_extension.lower()
        
        if ext_lower == 'pdf':
            return FileParser.parse_pdf(file_path)
        elif ext_lower in ['docx', 'doc']:
            return FileParser.parse_docx(file_path)
        elif ext_lower == 'txt':
            return FileParser.parse_txt(file_path)
        elif ext_lower in ['jpg', 'jpeg', 'png']:
            return FileParser.parse_image(file_path)
        else:
            raise Exception(f"不支持的文件格式: {file_extension}")
