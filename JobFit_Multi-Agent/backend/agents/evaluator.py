"""
评价智能体 - 综合评估并给出优化建议
"""
import json
from utils.llm_client import LLMClient

class EvaluatorAgent:
    """评价智能体，负责综合打分并提供简历优化建议"""
    
    def __init__(self, llm_client=None):
        """
        初始化评价智能体
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or LLMClient()
    
    def evaluate_and_suggest(self, resume_text, jd_info, match_result, interview_results=None):
        """
        综合评价并给出建议
        
        Args:
            resume_text: 简历文本
            jd_info: JD信息
            match_result: 匹配结果
            interview_results: 面试结果（可选）
            
        Returns:
            dict: 综合评价结果
                {
                    "overall_score": 综合评分(0-100),
                    "resume_optimization": {
                        "format_suggestions": [格式建议],
                        "content_suggestions": [内容建议],
                        "keywords_to_add": [建议添加的关键词]
                    },
                    "interview_preparation": {
                        "key_topics": [需要重点准备的 topic],
                        "weak_areas": [薄弱领域],
                        "preparation_tips": [准备建议]
                    },
                    "action_plan": [行动计划列表]
                }
        """
        jd_formatted = json.dumps(jd_info, ensure_ascii=False, indent=2)
        match_formatted = json.dumps(match_result, ensure_ascii=False, indent=2)
        
        interview_context = ""
        if interview_results:
            interview_context = f"\n\n面试表现：\n{json.dumps(interview_results, ensure_ascii=False, indent=2)}"
        
        prompt = f"""
你是一位资深的职业发展顾问和简历优化专家。请基于以下信息，为候选人提供全面的评估和优化建议。

职位描述：
{jd_formatted}

简历内容：
{resume_text}

匹配分析结果：
{match_formatted}
{interview_context}

请以JSON格式返回综合评价和建议：
{{
    "overall_score": 78,
    "resume_optimization": {{
        "format_suggestions": ["建议1", "建议2"],
        "content_suggestions": ["建议1", "建议2"],
        "keywords_to_add": ["关键词1", "关键词2"]
    }},
    "interview_preparation": {{
        "key_topics": ["主题1", "主题2"],
        "weak_areas": ["薄弱点1", "薄弱点2"],
        "preparation_tips": ["技巧1", "技巧2"]
    }},
    "action_plan": ["步骤1", "步骤2", "步骤3"]
}}

要求：
1. overall_score是综合评分（0-100），考虑匹配度、简历质量、面试表现等
2. resume_optimization针对简历本身提出具体改进建议
3. interview_preparation针对面试准备给出指导
4. action_plan是按优先级排序的 actionable 行动步骤
5. 所有建议要具体、可操作、有针对性

注意：只返回JSON格式，不要包含其他文字。
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(messages)
            result = self.llm_client.extract_json(response)
            return result
        except Exception as e:
            raise Exception(f"综合评价失败: {str(e)}")
