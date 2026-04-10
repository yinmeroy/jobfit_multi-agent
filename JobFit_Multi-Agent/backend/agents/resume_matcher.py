"""
简历匹配智能体 - 对比简历与JD，评估匹配度
"""
import json
from utils.llm_client import LLMClient

class ResumeMatcherAgent:
    """简历匹配智能体，负责分析简历与JD的匹配程度"""
    
    def __init__(self, llm_client=None):
        """
        初始化简历匹配智能体
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or LLMClient()
    
    def match_resume_with_jd(self, resume_text, jd_info):
        """
        匹配简历与JD
        
        Args:
            resume_text: 简历文本内容
            jd_info: JD解析后的信息字典
            
        Returns:
            dict: 匹配结果
                {
                    "match_score": 匹配分数(0-100),
                    "matched_skills": [已匹配的技能],
                    "missing_skills": [缺失的技能],
                    "strengths": [优势列表],
                    "weaknesses": [短板列表],
                    "suggestions": [改进建议]
                }
        """
        jd_formatted = json.dumps(jd_info, ensure_ascii=False, indent=2)
        
        prompt = f"""
你是一个专业的简历评估专家。请对比以下简历和职位要求，给出详细的匹配分析。

职位描述信息：
{jd_formatted}

简历内容：
{resume_text}

请以JSON格式返回评估结果：
{{
    "match_score": 85,
    "matched_skills": ["技能1", "技能2"],
    "missing_skills": ["技能3", "技能4"],
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["短板1", "短板2"],
    "suggestions": ["建议1", "建议2"]
}}

评分标准：
- 90-100: 非常匹配，几乎完全符合要求
- 75-89: 较为匹配，基本满足要求
- 60-74: 一般匹配，部分符合但有明显差距
- 40-59: 匹配度较低，存在较多不足
- 0-39: 不匹配，差距较大

注意：
1. 只返回JSON格式，不要包含其他文字
2. matched_skills是简历中具备且JD要求的技能
3. missing_skills是JD要求但简历中未体现的技能
4. strengths和weaknesses要具体明确
5. suggestions要有针对性，可操作
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(messages)
            result = self.llm_client.extract_json(response)
            return result
        except Exception as e:
            raise Exception(f"简历匹配失败: {str(e)}")
