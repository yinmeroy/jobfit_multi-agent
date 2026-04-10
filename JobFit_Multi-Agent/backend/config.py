"""
JobFit Multi-Agent System - 配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'jobfit-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB最大文件大小
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
    
    # LLM API配置
    LLM_API_URL = os.getenv('LLM_API_URL', 'http://localhost:11434/api/chat')
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'qwen2.5:7b')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    
    # OCR配置（用于图片简历）
    OCR_ENABLED = os.getenv('OCR_ENABLED', 'True').lower() == 'true'
    
    # Tesseract OCR 引擎路径配置
    # Windows: r'D:\Program Files\Tesseract-OCR\tesseract.exe'
    # Linux/Docker: '/usr/bin/tesseract'
    # Mac: '/usr/local/bin/tesseract'
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', 'tesseract')  # 默认使用系统PATH查找
    
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
