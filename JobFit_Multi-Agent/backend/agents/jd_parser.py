"""
JD解析智能体 - 从职位描述中提取关键信息
"""
from utils.llm_client import LLMClient
import json

class JDParserAgent:
    """JD解析智能体，负责提取岗位要求、技能列表等信息"""
    
    def __init__(self, llm_client=None):
        """
        初始化JD解析智能体
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or LLMClient()
    
    def parse_jd(self, jd_text):
        """
        解析职位描述文本
        
        Args:
            jd_text: 职位描述文本
            
        Returns:
            dict: 包含岗位信息的字典
                {
                    "job_title": 岗位名称,
                    "required_skills": [技能列表],
                    "preferred_skills": [加分技能列表],
                    "experience_years": 经验要求,
                    "education": 学历要求,
                    "responsibilities": [职责列表],
                    "requirements": [要求列表]
                }
        """
        prompt = f"""
你是一个专业的JD（职位描述）分析专家。请分析以下职位描述，并提取关键信息。

职位描述：
{jd_text}

请以JSON格式返回以下信息：
{{
    "job_title": "岗位名称",
    "required_skills": ["必需技能1", "必需技能2", ...],
    "preferred_skills": ["加分技能1", "加分技能2", ...],
    "experience_years": "经验要求（如：3-5年）",
    "education": "学历要求（如：本科及以上）",
    "responsibilities": ["职责1", "职责2", ...],
    "requirements": ["要求1", "要求2", ...]
}}

注意：
1. 只返回JSON格式，不要包含其他文字
2. 如果某项信息在JD中未提及，用空字符串或空数组表示
3. 技能要具体明确，避免模糊描述
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(messages)
            result = self.llm_client.extract_json(response)
            return result
        except Exception as e:
            raise Exception(f"JD解析失败: {str(e)}")
