/**
 * JobFit API接口封装
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000 // 120秒超时，因为LLM调用可能较慢
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('API Request:', config.method.toUpperCase(), config.url)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default {
  /**
   * 上传简历文件
   */
  uploadResume(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 上传JD文本
   */
  uploadJD(jdText, sessionId = null) {
    return api.post('/upload/jd', {
      jd_text: jdText,
      session_id: sessionId
    })
  },

  /**
   * 匹配简历与JD
   */
  matchResumeJD(sessionId) {
    return api.post('/match', {
      session_id: sessionId
    })
  },

  /**
   * 生成面试问题
   */
  generateInterviewQuestions(sessionId, numQuestions = 5) {
    return api.post('/interview/generate', {
      session_id: sessionId,
      num_questions: numQuestions
    })
  },

  /**
   * 提交面试回答
   */
  submitAnswer(sessionId, questionIndex, answer) {
    return api.post('/interview/answer', {
      session_id: sessionId,
      question_index: questionIndex,
      answer: answer
    })
  },

  /**
   * 获取综合评价
   */
  evaluate(sessionId) {
    return api.post('/evaluate', {
      session_id: sessionId
    })
  },

  /**
   * 获取会话状态
   */
  getSessionStatus(sessionId) {
    return api.get(`/session/${sessionId}`)
  }
}
