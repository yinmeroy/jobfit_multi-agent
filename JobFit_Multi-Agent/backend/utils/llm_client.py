"""
LLM客户端 - 用于调用大语言模型API
支持OpenAI兼容的API接口
"""
import requests
import json
from config import Config

class LLMClient:
    """LLM客户端类，封装与大语言模型的交互"""
    
    def __init__(self, api_url=None, api_key=None, model=None):
        """
        初始化LLM客户端
        
        Args:
            api_url: API地址
            api_key: API密钥
            model: 模型名称
        """
        self.api_url = api_url or Config.LLM_API_URL
        self.api_key = api_key or Config.LLM_API_KEY
        self.model = model or Config.LLM_MODEL
        self.temperature = Config.LLM_TEMPERATURE
    
    def chat(self, messages, temperature=None):
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            
        Returns:
            str: 模型返回的回答
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
    
    def extract_json(self, text):
        """
        从文本中提取JSON对象或数组
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            dict or list: 解析后的JSON对象或数组
        """
        try:
            # 尝试直接解析
            return json.loads(text)
        except:
            # 尝试提取JSON部分 - 支持对象{}和数组[]
            # 先找对象
            start_obj = text.find('{')
            end_obj = text.rfind('}') + 1
            
            # 再找数组
            start_arr = text.find('[')
            end_arr = text.rfind(']') + 1
            
            # 选择先出现的那个
            candidates = []
            if start_obj != -1 and end_obj > start_obj:
                candidates.append((start_obj, end_obj))
            if start_arr != -1 and end_arr > start_arr:
                candidates.append((start_arr, end_arr))
            
            if not candidates:
                raise ValueError("无法从文本中提取JSON")
            
            # 选择起始位置最靠前的
            candidates.sort(key=lambda x: x[0])
            start, end = candidates[0]
            
            json_str = text[start:end]
            return json.loads(json_str)
