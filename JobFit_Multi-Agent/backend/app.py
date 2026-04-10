"""
JobFit Multi-Agent System - Flask后端应用
提供简历优化和面试模拟的API接口
"""
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from utils.file_parser import FileParser
from agents.jd_parser import JDParserAgent
from agents.resume_matcher import ResumeMatcherAgent
from agents.interview_simulator import InterviewSimulatorAgent
from agents.evaluator import EvaluatorAgent


def create_app():
    """创建Flask应用"""
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app)
    
    # 初始化组件
    file_parser = FileParser()
    jd_parser = JDParserAgent()
    resume_matcher = ResumeMatcherAgent()
    interview_simulator = InterviewSimulatorAgent()
    evaluator = EvaluatorAgent()
    
    # 存储会话数据（生产环境应使用数据库）
    sessions = {}
    
    @app.route('/api/upload/resume', methods=['POST'])
    def upload_resume():
        """上传简历文件"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': '没有文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            # 检查文件扩展名（使用标准库方法确保健壮性）
            filename = file.filename
            _, ext = os.path.splitext(filename)
            ext = ext.lstrip('.').lower()  # 移除点号并转小写
            
            if ext not in Config.ALLOWED_EXTENSIONS:
                return jsonify({'error': f'不支持的文件格式: {ext}'}), 400
            
            # 生成唯一文件名并保存
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # 解析文件内容（传入扩展名而不是完整文件名）
            text_content = file_parser.parse_file(file_path, ext)
            
            # 存储到会话
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'resume_text': text_content,
                'resume_filename': filename,
                'jd_info': None,
                'match_result': None,
                'interview_questions': [],
                'interview_answers': []
            }
            
            return jsonify({
                'session_id': session_id,
                'filename': filename,
                'text_preview': text_content[:500] + '...' if len(text_content) > 500 else text_content
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload/jd', methods=['POST'])
    def upload_jd():
        """上传JD文本"""
        try:
            data = request.get_json()
            jd_text = data.get('jd_text', '')
            
            if not jd_text:
                return jsonify({'error': 'JD文本不能为空'}), 400
            
            # 解析JD
            jd_info = jd_parser.parse_jd(jd_text)
            
            # 获取或创建会话
            session_id = data.get('session_id')
            if session_id and session_id in sessions:
                sessions[session_id]['jd_info'] = jd_info
            else:
                session_id = str(uuid.uuid4())
                sessions[session_id] = {
                    'resume_text': '',
                    'resume_filename': '',
                    'jd_info': jd_info,
                    'match_result': None,
                    'interview_questions': [],
                    'interview_answers': []
                }
            
            return jsonify({
                'session_id': session_id,
                'jd_info': jd_info
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/match', methods=['POST'])
    def match_resume_jd():
        """匹配简历与JD"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            
            if not session_id or session_id not in sessions:
                return jsonify({'error': '无效的会话ID'}), 400
            
            session = sessions[session_id]
            
            if not session['resume_text']:
                return jsonify({'error': '请先上传简历'}), 400
            
            if not session['jd_info']:
                return jsonify({'error': '请先上传JD'}), 400
            
            # 执行匹配
            match_result = resume_matcher.match_resume_with_jd(
                session['resume_text'],
                session['jd_info']
            )
            
            session['match_result'] = match_result
            
            return jsonify({
                'match_result': match_result
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/interview/generate', methods=['POST'])
    def generate_interview_questions():
        """生成面试问题"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            num_questions = data.get('num_questions', 5)
            
            if not session_id or session_id not in sessions:
                return jsonify({'error': '无效的会话ID'}), 400
            
            session = sessions[session_id]
            
            if not session['resume_text'] or not session['jd_info']:
                return jsonify({'error': '请先上传简历和JD'}), 400
            
            if not session['match_result']:
                return jsonify({'error': '请先进行匹配分析'}), 400
            
            # 生成面试问题
            questions = interview_simulator.generate_questions(
                session['resume_text'],
                session['jd_info'],
                session['match_result'],
                num_questions
            )
            
            session['interview_questions'] = questions
            session['interview_answers'] = [''] * len(questions)
            
            return jsonify({
                'questions': questions
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/interview/answer', methods=['POST'])
    def submit_interview_answer():
        """提交面试回答"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            question_index = data.get('question_index')
            answer = data.get('answer', '')
            
            if not session_id or session_id not in sessions:
                return jsonify({'error': '无效的会话ID'}), 400
            
            session = sessions[session_id]
            
            if question_index is None or question_index >= len(session['interview_questions']):
                return jsonify({'error': '无效的问题索引'}), 400
            
            # 获取当前问题
            current_question = session['interview_questions'][question_index]
            question_text = current_question if isinstance(current_question, str) else current_question.get('question', '')
            
            # 评估回答(包含评分、反馈和可能的追问)
            evaluation_result = interview_simulator.evaluate_answer(
                question_text,
                answer,
                session['jd_info']
            )
            
            # 保存回答
            session['interview_answers'][question_index] = answer
            
            # 如果有追问,保存到会话中
            if evaluation_result.get('follow_up_question'):
                # 初始化追问历史
                if 'follow_up_history' not in session:
                    session['follow_up_history'] = {}
                
                # 记录当前问题的追问
                if question_index not in session['follow_up_history']:
                    session['follow_up_history'][question_index] = []
                
                session['follow_up_history'][question_index].append({
                    'original_question': question_text,
                    'answer': answer,
                    'follow_up': evaluation_result['follow_up_question'],
                    'score': evaluation_result['score']
                })
            
            return jsonify({
                'result': evaluation_result
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/evaluate', methods=['POST'])
    def evaluate():
        """综合评价"""
        try:
            data = request.get_json()
            session_id = data.get('session_id')
            
            if not session_id or session_id not in sessions:
                return jsonify({'error': '无效的会话ID'}), 400
            
            session = sessions[session_id]
            
            if not session['resume_text'] or not session['jd_info']:
                return jsonify({'error': '请先上传简历和JD'}), 400
            
            if not session['match_result']:
                return jsonify({'error': '请先进行匹配分析'}), 400
            
            # 准备面试结果
            interview_results = None
            if session['interview_questions']:
                interview_results = {
                    'questions': session['interview_questions'],
                    'answers': session['interview_answers']
                }
            
            # 执行综合评价
            evaluation = evaluator.evaluate_and_suggest(
                session['resume_text'],
                session['jd_info'],
                session['match_result'],
                interview_results
            )
            
            return jsonify({
                'evaluation': evaluation
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/session/<session_id>', methods=['GET'])
    def get_session(session_id):
        """获取会话状态"""
        if session_id not in sessions:
            return jsonify({'error': '会话不存在'}), 404
        
        session = sessions[session_id]
        return jsonify({
            'has_resume': bool(session['resume_text']),
            'has_jd': bool(session['jd_info']),
            'has_match_result': bool(session['match_result']),
            'interview_questions_count': len(session['interview_questions']),
            'jd_info': session['jd_info']
        })
    
    # 前端路由 - 所有其他路由返回前端页面
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
