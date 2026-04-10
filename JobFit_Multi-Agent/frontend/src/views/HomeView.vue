<template>
  <div class="home-container">
    <!-- 头部 -->
    <el-header class="header">
      <h1>🎯 JobFit - 多智能体简历优化与面试模拟系统</h1>
    </el-header>

    <el-main class="main-content">
      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps">
        <el-step title="上传文件" description="上传简历和JD" />
        <el-step title="解析JD" description="提取岗位要求" />
        <el-step title="简历匹配" description="分析匹配度" />
        <el-step title="模拟面试" description="生成面试题" />
        <el-step title="综合评价" description="获取建议" />
      </el-steps>

      <!-- 步骤1: 上传文件 -->
      <el-card v-show="currentStep === 0" class="step-card">
        <template #header>
          <div class="card-header">
            <span>📄 上传简历与职位描述</span>
          </div>
        </template>

        <el-form label-width="120px">
          <el-form-item label="上传简历">
            <el-upload
              drag
              :auto-upload="false"
              :on-change="handleResumeChange"
              :limit="1"
              accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、DOCX、TXT、JPG、PNG 格式，最大16MB
                </div>
              </template>
            </el-upload>
            <div v-if="resumeFile" class="file-info">
              <el-tag type="success">已选择: {{ resumeFile.name }}</el-tag>
            </div>
          </el-form-item>

          <el-form-item label="职位描述(JD)">
            <el-input
              v-model="jdText"
              type="textarea"
              :rows="10"
              placeholder="请粘贴完整的职位描述文本..."
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleUpload" :loading="uploading" size="large">
              开始分析
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 步骤2: JD解析结果 -->
      <el-card v-show="currentStep === 1" class="step-card">
        <template #header>
          <div class="card-header">
            <span>📋 JD解析结果</span>
            <el-button type="primary" @click="goToStep(0)" size="small">返回</el-button>
          </div>
        </template>

        <div v-if="jdInfo.job_title" class="jd-result">
          <h3>岗位名称: {{ jdInfo.job_title }}</h3>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="经验要求">{{ jdInfo.experience_years || '未明确' }}</el-descriptions-item>
            <el-descriptions-item label="学历要求">{{ jdInfo.education || '未明确' }}</el-descriptions-item>
          </el-descriptions>

          <h4>必需技能:</h4>
          <el-tag v-for="skill in jdInfo.required_skills" :key="skill" class="skill-tag">
            {{ skill }}
          </el-tag>

          <h4>加分技能:</h4>
          <el-tag v-for="skill in jdInfo.preferred_skills" :key="skill" type="warning" class="skill-tag">
            {{ skill }}
          </el-tag>

          <h4>岗位职责:</h4>
          <ul>
            <li v-for="resp in jdInfo.responsibilities" :key="resp">{{ resp }}</li>
          </ul>

          <h4>任职要求:</h4>
          <ul>
            <li v-for="req in jdInfo.requirements" :key="req">{{ req }}</li>
          </ul>
        </div>

        <el-divider />

        <el-button type="primary" @click="handleMatch" :loading="matching" size="large">
          下一步: 简历匹配分析
        </el-button>
      </el-card>

      <!-- 步骤3: 简历匹配结果 -->
      <el-card v-show="currentStep === 2" class="step-card">
        <template #header>
          <div class="card-header">
            <span>🎯 简历匹配分析</span>
            <el-button type="primary" @click="goToStep(1)" size="small">返回</el-button>
          </div>
        </template>

        <div v-if="matchResult.match_score !== undefined" class="match-result">
          <div class="score-display">
            <el-progress
              type="dashboard"
              :percentage="matchResult.match_score"
              :color="getScoreColor(matchResult.match_score)"
            >
              <template #default="{ percentage }">
                <span class="percentage-value">{{ percentage }}%</span>
                <span class="percentage-label">匹配度</span>
              </template>
            </el-progress>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <h4>✅ 已匹配技能:</h4>
              <el-tag v-for="skill in matchResult.matched_skills" :key="skill" type="success" class="skill-tag">
                {{ skill }}
              </el-tag>
            </el-col>
            <el-col :span="12">
              <h4>❌ 缺失技能:</h4>
              <el-tag v-for="skill in matchResult.missing_skills" :key="skill" type="danger" class="skill-tag">
                {{ skill }}
              </el-tag>
            </el-col>
          </el-row>

          <h4>💪 优势:</h4>
          <ul>
            <li v-for="strength in matchResult.strengths" :key="strength">{{ strength }}</li>
          </ul>

          <h4>⚠️ 短板:</h4>
          <ul>
            <li v-for="weakness in matchResult.weaknesses" :key="weakness">{{ weakness }}</li>
          </ul>

          <h4>💡 改进建议:</h4>
          <ul>
            <li v-for="suggestion in matchResult.suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </div>

        <el-divider />

        <el-button type="primary" @click="handleGenerateInterview" :loading="generating" size="large">
          下一步: 生成面试问题
        </el-button>
      </el-card>

      <!-- 步骤4: 模拟面试 -->
      <el-card v-show="currentStep === 3" class="step-card">
        <template #header>
          <div class="card-header">
            <span>🎤 模拟面试</span>
            <el-button type="primary" @click="goToStep(2)" size="small">返回</el-button>
          </div>
        </template>

        <div v-if="interviewQuestions.length > 0">
          <h3>面试问题 ({{ currentQuestionIndex + 1 }}/{{ interviewQuestions.length }})</h3>
          
          <!-- 当前问题卡片 -->
          <el-card class="question-card" shadow="hover">
            <h4>{{ currentQuestion.question }}</h4>
            <el-tag :type="getDifficultyType(currentQuestion.difficulty)">
              {{ currentQuestion.difficulty }}
            </el-tag>
            <el-tag type="info">{{ currentQuestion.type }}</el-tag>
            <p class="focus-area">考察重点: {{ currentQuestion.focus_area }}</p>
          </el-card>

          <!-- 对话历史区域 -->
          <div v-if="currentDialogueHistory && currentDialogueHistory.length > 0" class="dialogue-history">
            <h4>💬 对话记录</h4>
            <div 
              v-for="(message, idx) in currentDialogueHistory" 
              :key="idx"
              :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
            >
              <div class="message-role">
                {{ message.role === 'user' ? '👤 你' : '🎤 面试官' }}
              </div>
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>

          <!-- 回答输入框 -->
          <el-input
            v-model="currentAnswer"
            type="textarea"
            :rows="6"
            :placeholder="hasFollowUp ? '请回答追问...' : '请输入你的回答...'"
            class="answer-input"
          />

          <!-- 操作按钮组 -->
          <div class="button-group">
            <el-button @click="prevQuestion" :disabled="currentQuestionIndex === 0">
              上一题
            </el-button>
            <el-button 
              type="primary" 
              @click="submitAnswer" 
              :loading="submitting"
              :disabled="!currentAnswer.trim()"
            >
              {{ hasFollowUp ? '回答追问' : '提交回答' }}
            </el-button>
            <el-button @click="nextQuestion" :disabled="currentQuestionIndex === interviewQuestions.length - 1">
              下一题
            </el-button>
          </div>

          <!-- 评估反馈卡片 -->
          <el-card v-if="currentFeedback && !hasFollowUp" class="feedback-card" shadow="never">
            <h4>📊 本轮评估</h4>
            <el-progress 
              :percentage="currentFeedback.score * 10" 
              :color="getScoreColor(currentFeedback.score * 10)"
              :format="format => `${currentFeedback.score}/10分`" 
            />
            <p><strong>评价:</strong> {{ currentFeedback.feedback }}</p>
            <p><strong>改进建议:</strong> {{ currentFeedback.improvement_suggestion }}</p>
            <el-alert 
              v-if="currentFeedback.follow_up_question" 
              title="收到追问,请继续回答" 
              type="warning" 
              :closable="false"
              show-icon
            />
          </el-card>
        </div>

        <el-divider />

        <el-button type="primary" @click="handleEvaluate" :loading="evaluating" size="large">
          下一步: 查看综合评价
        </el-button>
      </el-card>

      <!-- 步骤5: 综合评价 -->
      <el-card v-show="currentStep === 4" class="step-card">
        <template #header>
          <div class="card-header">
            <span>📈 综合评价与建议</span>
            <el-button type="primary" @click="goToStep(3)" size="small">返回</el-button>
          </div>
        </template>

        <div v-if="evaluationResult.overall_score !== undefined" class="evaluation-result">
          <div class="overall-score">
            <h3>综合评分</h3>
            <el-progress
              type="dashboard"
              :percentage="evaluationResult.overall_score"
              :color="getScoreColor(evaluationResult.overall_score)"
            >
              <template #default="{ percentage }">
                <span class="percentage-value">{{ percentage }}</span>
                <span class="percentage-label">总分</span>
              </template>
            </el-progress>
          </div>

          <el-tabs>
            <el-tab-pane label="简历优化建议">
              <h4>📝 格式建议:</h4>
              <ul>
                <li v-for="suggestion in evaluationResult.resume_optimization.format_suggestions" :key="suggestion">
                  {{ suggestion }}
                </li>
              </ul>

              <h4>📄 内容建议:</h4>
              <ul>
                <li v-for="suggestion in evaluationResult.resume_optimization.content_suggestions" :key="suggestion">
                  {{ suggestion }}
                </li>
              </ul>

              <h4>🔑 建议添加的关键词:</h4>
              <el-tag v-for="keyword in evaluationResult.resume_optimization.keywords_to_add" :key="keyword" type="success" class="skill-tag">
                {{ keyword }}
              </el-tag>
            </el-tab-pane>

            <el-tab-pane label="面试准备建议">
              <h4>🎯 重点准备主题:</h4>
              <ul>
                <li v-for="topic in evaluationResult.interview_preparation.key_topics" :key="topic">
                  {{ topic }}
                </li>
              </ul>

              <h4>⚠️ 薄弱领域:</h4>
              <ul>
                <li v-for="area in evaluationResult.interview_preparation.weak_areas" :key="area">
                  {{ area }}
                </li>
              </ul>

              <h4>💡 准备技巧:</h4>
              <ul>
                <li v-for="tip in evaluationResult.interview_preparation.preparation_tips" :key="tip">
                  {{ tip }}
                </li>
              </ul>
            </el-tab-pane>

            <el-tab-pane label="行动计划">
              <h4>🚀 行动步骤 (按优先级排序):</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="(action, index) in evaluationResult.action_plan"
                  :key="index"
                  :timestamp="`步骤 ${index + 1}`"
                  placement="top"
                >
                  <el-card>
                    <p>{{ action }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
          </el-tabs>
        </div>

        <el-divider />

        <el-button type="success" @click="restart" size="large">
          🔄 重新开始
        </el-button>
      </el-card>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadFiles, parseJD, matchResume, generateInterview, submitInterviewAnswer, evaluate } from '../api'

// 状态管理
const currentStep = ref(0)
const uploading = ref(false)
const matching = ref(false)
const generating = ref(false)
const submitting = ref(false)
const evaluating = ref(false)

const resumeFile = ref(null)
const jdText = ref('')
const sessionId = ref('')

const jdInfo = ref({})
const matchResult = ref({})
const interviewQuestions = ref([])
const currentQuestionIndex = ref(0)
const currentAnswer = ref('')
const currentFeedback = ref(null)
const evaluationResult = ref({})

// 追问对话历史 - 每个问题维护一个对话列表
const followUpDialogues = ref({})

// 计算属性
const currentQuestion = computed(() => {
  return interviewQuestions.value[currentQuestionIndex.value] || {}
})

const currentDialogueHistory = computed(() => {
  return followUpDialogues.value[currentQuestionIndex.value] || []
})

const hasFollowUp = computed(() => {
  const history = currentDialogueHistory.value
  if (!history || history.length === 0) return false
  const lastMessage = history[history.length - 1]
  return lastMessage.role === 'assistant' && lastMessage.hasFollowUp
})

// 方法
const handleResumeChange = (file) => {
  resumeFile.value = file.raw
}

const handleUpload = async () => {
  if (!resumeFile.value && !jdText.value) {
    ElMessage.warning('请至少上传简历或提供JD文本')
    return
  }

  uploading.value = true
  try {
    // 步骤1: 如果有简历文件,先上传简历
    if (resumeFile.value) {
      console.log('开始上传简历文件:', resumeFile.value.name)
      const resumeResult = await uploadFiles(resumeFile.value)
      sessionId.value = resumeResult.session_id
      console.log('简历上传成功, session_id:', sessionId.value)
    }
    
    // 步骤2: 如果有JD文本,调用解析接口
    if (jdText.value) {
      console.log('开始解析JD文本')
      const jdResult = await parseJD(jdText.value, sessionId.value || undefined)
      jdInfo.value = jdResult.jd_info
      
      // 如果之前没有上传简历,使用JD接口返回的session_id
      if (!sessionId.value) {
        sessionId.value = jdResult.session_id
      }
      
      console.log('JD解析成功, jdInfo:', jdInfo.value)
      currentStep.value =1
      ElMessage.success('JD解析成功')
    } else if (resumeFile.value) {
      // 只上传了简历,没有JD
      currentStep.value = 1
      ElMessage.success('简历上传成功,请填写JD文本')
    }
  } catch (error) {
    console.error('===== 上传错误详细信息 =====')
    console.error('错误对象:', error)
    console.error('错误响应:', error.response)
    console.error('错误数据:', error.response?.data)
    console.error('错误状态:', error.response?.status)
    console.error('================================')
    
    const errorMsg = error.response?.data?.error || error.message || '上传失败'
    ElMessage.error(errorMsg)
  } finally {
    uploading.value = false
  }
}

// const handleParseJD = async () => {
//   if (!jdText.value) {
//     ElMessage.warning('请输入JD文本')
//     return
//   }

//   uploading.value = true
//   try {
//     const result = await parseJD(sessionId.value, jdText.value)
//     jdInfo.value = result.jd_info
//     currentStep.value = 1
//     ElMessage.success('JD解析成功')
//   } catch (error) {
//     ElMessage.error(error.message)
//   } finally {
//     uploading.value = false
//   }
// }

const handleMatch = async () => {
  matching.value = true
  try {
    const result = await matchResume(sessionId.value)
    matchResult.value = result.match_result
    currentStep.value = 2
    ElMessage.success('简历匹配分析完成')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    matching.value = false
  }
}

const handleGenerateInterview = async () => {
  generating.value = true
  try {
    const result = await generateInterview(sessionId.value, 5)
    interviewQuestions.value = result.questions
    currentQuestionIndex.value = 0
    currentAnswer.value = ''
    currentFeedback.value = null
    currentStep.value = 3
    ElMessage.success('面试问题生成成功,请开始回答')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    generating.value = false
  }
}

const submitAnswer = async () => {
  if (!currentAnswer.value.trim()) {
    ElMessage.warning('请输入回答')
    return
  }

  submitting.value = true
  try {
    const result = await submitInterviewAnswer(
      sessionId.value,
      currentQuestionIndex.value,
      currentAnswer.value
    )
    
    const feedback = result.result
    currentFeedback.value = feedback

    // 初始化当前问题的对话历史数组
    if (!followUpDialogues.value[currentQuestionIndex.value]) {
      followUpDialogues.value[currentQuestionIndex.value] = []
    }

    // 添加用户回答到历史
    followUpDialogues.value[currentQuestionIndex.value].push({
      role: 'user',
      content: currentAnswer.value
    })

    // 构建面试官反馈内容
    let assistantContent = `评分: ${feedback.score}/10\n评价: ${feedback.feedback}\n建议: ${feedback.improvement_suggestion}`
    if (feedback.follow_up_question) {
      assistantContent += `\n\n追问: ${feedback.follow_up_question}`
    }

    // 添加面试官反馈到历史
    followUpDialogues.value[currentQuestionIndex.value].push({
      role: 'assistant',
      content: assistantContent,
      hasFollowUp: !!feedback.follow_up_question
    })

    // 清空输入框以便输入追问回答或下一题
    currentAnswer.value = ''
    
    ElMessage.success('回答评估完成')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    submitting.value = false
  }
}

const handleEvaluate = async () => {
  evaluating.value = true
  try {
    const result = await evaluate(sessionId.value)
    evaluationResult.value = result.evaluation
    currentStep.value = 4
    ElMessage.success('综合评价完成')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    evaluating.value = false
  }
}

const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    currentAnswer.value = ''
    // 恢复上一个问题的最新反馈状态，如果有的话
    const history = followUpDialogues.value[currentQuestionIndex.value]
    if (history && history.length > 0) {
       // 简单的逻辑：如果有历史记录，我们可能想看到最后一条反馈
       // 但由于 currentFeedback 主要用于控制 UI 显示逻辑，
       // 这里可以选择不恢复或者恢复最后一条 assistant 消息作为反馈参考
       // 为简化，保持 currentFeedback 为 null 或根据需求恢复
       // 在新设计中，主要依赖 dialogueHistory 显示，currentFeedback 用于底部总结卡片
       currentFeedback.value = null 
    } else {
       currentFeedback.value = null
    }
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < interviewQuestions.value.length - 1) {
    currentQuestionIndex.value++
    currentAnswer.value = ''
    currentFeedback.value = null
  }
}

const goToStep = (step) => {
  currentStep.value = step
  // 切换大步数时重置临时反馈状态，但保留对话历史以便回顾
  currentFeedback.value = null
  currentAnswer.value = ''
}

const restart = () => {
  currentStep.value = 0
  resumeFile.value = null
  jdText.value = ''
  sessionId.value = ''
  jdInfo.value = {}
  matchResult.value = {}
  interviewQuestions.value = []
  currentQuestionIndex.value = 0
  currentAnswer.value = ''
  currentFeedback.value = null
  evaluationResult.value = {}
  followUpDialogues.value = {} // 重置追问历史
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getDifficultyType = (difficulty) => {
  const map = {
    '简单': 'success',
    '中等': 'warning',
    '困难': 'danger'
  }
  return map[difficulty] || 'info'
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  text-align: center;
  padding: 40px 20px;
  color: white;
}

.header h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.header p {
  font-size: 16px;
  opacity: 0.9;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.steps {
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
}

.step-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
}

.file-info {
  margin-top: 10px;
}

.skill-tag {
  margin: 5px;
}

.jd-result h3,
.jd-result h4,
.match-result h4,
.evaluation-result h4 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.jd-result ul,
.match-result ul {
  padding-left: 20px;
}

.jd-result li,
.match-result li {
  margin: 5px 0;
  line-height: 1.6;
}

.score-display {
  text-align: center;
  margin: 30px 0;
}

.percentage-value {
  display: block;
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}

.percentage-label {
  display: block;
  font-size: 14px;
  color: #909399;
}

.question-card {
  margin: 20px 0;
  background: #f5f7fa;
}

.question-card h4 {
  margin-bottom: 10px;
  color: #303133;
}

.question-card .el-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.focus-area {
  margin-top: 10px;
  color: #606266;
  font-style: italic;
}

.answer-input {
  margin: 20px 0;
}

.button-group {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
}

.dialogue-history {
  margin: 20px 0;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.dialogue-history h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.message-role {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.message-content {
  padding: 10px 15px;
  border-radius: 8px;
  line-height: 1.6;
  white-space: pre-wrap;
  max-width: 90%;
}

.user-message {
  align-items: flex-end;
}

.user-message .message-content {
  background-color: #ecf5ff;
  color: #409eff;
  border-top-right-radius: 0;
}

.assistant-message {
  align-items: flex-start;
}

.assistant-message .message-content {
  background-color: #f4f4f5;
  color: #303133;
  border-top-left-radius: 0;
}

.feedback-card {
  margin-top: 20px;
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
}

.feedback-card h4 {
  margin-bottom: 15px;
  color: #303133;
}

.feedback-card p {
  margin: 10px 0;
  line-height: 1.6;
}

.overall-score {
  text-align: center;
  margin: 30px 0;
}

.overall-score h3 {
  margin-bottom: 20px;
  color: #303133;
}

.evaluation-result ul {
  padding-left: 20px;
}

.evaluation-result li {
  margin: 8px 0;
  line-height: 1.6;
}
</style>
