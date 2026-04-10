"""
模拟面试智能体 - 基于JD和简历生成面试题并进行追问
"""
from utils.llm_client import LLMClient
import json


class InterviewSimulatorAgent:
    """模拟面试智能体，负责生成面试问题和进行多轮对话"""
    
    def __init__(self, llm_client=None):
        """
        初始化模拟面试智能体
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or LLMClient()
    
    def generate_questions(self, resume_text, jd_info, match_result, num_questions=5):
        """
        基于JD和简历生成面试问题
        
        Args:
            resume_text: 简历文本内容
            jd_info: JD解析后的信息字典
            match_result: 匹配结果
            num_questions: 生成的问题数量
            
        Returns:
            list: 面试问题列表
        """
        jd_formatted = json.dumps(jd_info, ensure_ascii=False, indent=2)
        match_formatted = json.dumps(match_result, ensure_ascii=False, indent=2)
        
        prompt = f"""
你是一位经验丰富的技术面试官。请根据以下职位描述、候选人简历和匹配分析结果，生成{num_questions}个有针对性的面试问题。

职位描述：
{jd_formatted}

候选人简历：
{resume_text}

匹配分析：
{match_formatted}

要求：
1. 问题要涵盖技术能力、项目经验、软技能等方面
2. 重点关注候选人缺失的技能和薄弱环节
3. 包含基础题、进阶题和挑战题
4. 问题难度要与岗位要求匹配
5. 针对候选人的实际经历提问

请以JSON数组格式返回问题列表：
[
    {{
        "question": "问题内容",
        "difficulty": "easy/medium/hard",
        "type": "技术/项目/软技能/行为",
        "focus_area": "考察重点说明"
    }}
]


注意：只返回JSON数组，不要包含其他文字。
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(messages)
            questions = self.llm_client.extract_json(response)
            
            # 确保返回的是列表
            if isinstance(questions, list):
                return questions
            else:
                raise Exception("返回的问题格式不正确")
        
        except Exception as e:
            raise Exception(f"生成面试问题失败: {str(e)}")
    
    def evaluate_answer(self, question, answer, jd_info):
        """
        评估候选人的回答并生成反馈
        
        Args:
            question: 面试问题
            answer: 候选人回答
            jd_info: JD信息
            
        Returns:
            dict: 包含评分、反馈、改进建议和可能的追问
                {
                    "score": 0-10的评分,
                    "feedback": "评价内容",
                    "improvement_suggestion": "改进建议",
                    "follow_up_question": "追问问题(可选)"
                }
        """
        jd_formatted = json.dumps(jd_info, ensure_ascii=False, indent=2)
        
        prompt = f"""
作为一位专业的技术面试官,请评估候选人对以下问题的回答。

原问题: {question}
候选人回答: {answer}

岗位要求:
{jd_formatted}

请从以下几个方面进行评估:
1. 回答的完整性和准确性
2. 与岗位要求的匹配度
3. 体现的技术深度和实践经验

请以JSON格式返回评估结果:
{{
    "score": 7,
    "feedback": "对回答的整体评价",
    "improvement_suggestion": "具体的改进建议",
    "follow_up_question": "如果需要深入考察,生成一个追问问题;如果回答已经很完善,则为空字符串"
}}

评分标准:
- 9-10分: 回答非常完整、深入,超出预期
- 7-8分: 回答良好,基本符合要求
- 5-6分: 回答一般,有明显不足
- 3-4分: 回答较差,需要大幅改进
- 1-2分: 回答很差,几乎无价值

注意: 只返回JSON对象,不要包含其他文字。
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(messages)
            result = self.llm_client.extract_json(response)
            
            # 确保返回的是字典且包含必要字段
            if isinstance(result, dict):
                # 设置默认值
                result.setdefault('score', 5)
                result.setdefault('feedback', '评估完成')
                result.setdefault('improvement_suggestion', '建议继续完善')
                result.setdefault('follow_up_question', '')
                
                # 确保追问是字符串
                if not isinstance(result['follow_up_question'], str):
                    result['follow_up_question'] = ''
                
                return result
            else:
                raise Exception("返回的评估结果格式不正确")
        
        except Exception as e:
            # 如果出错,返回默认评估
            return {
                'score': 5,
                'feedback': f'评估过程中出现错误: {str(e)}',
                'improvement_suggestion': '请重新尝试',
                'follow_up_question': ''
            }
    
    def generate_follow_up(self, question, answer, jd_info):
        """
        根据回答生成追问问题
        
        Args:
            question: 原问题
            answer: 候选人回答
            jd_info: JD信息
            
        Returns:
            str: 追问问题，如果不需要追问则返回空字符串
        """
        jd_formatted = json.dumps(jd_info, ensure_ascii=False, indent=2)
        
        prompt = f"""
作为面试官，请评估候选人对以下问题的回答，并决定是否需要追问。

原问题：{question}
候选人回答：{answer}

岗位要求：
{jd_formatted}

请判断：
1. 如果回答不够深入或完整，生成一个追问问题
2. 如果回答已经很好，返回空字符串

要求：
- 追问要具体，针对回答中的模糊点或关键点
- 追问要有深度，考察候选人的真实水平
- 如果需要追问，直接返回追问问题文本
- 如果不需要追问，返回空字符串 ""

注意：只返回追问问题文本或空字符串，不要包含其他文字。
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(messages)
            follow_up = response.strip()
            
            # 如果返回的是空或很短的内容，认为不需要追问
            if len(follow_up) < 5:
                return ""
            
            return follow_up
        
        except Exception as e:
            # 如果出错，返回空字符串表示不追问
            return ""
