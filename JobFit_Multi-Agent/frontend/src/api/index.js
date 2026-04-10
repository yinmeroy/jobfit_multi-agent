/**
 * API统一导出
 */
import jobfitApi from './jobfit'

// 导出与HomeView.vue中导入名称一致的函数
export const uploadFiles = jobfitApi.uploadResume.bind(jobfitApi)
export const parseJD = jobfitApi.uploadJD.bind(jobfitApi)
export const matchResume = jobfitApi.matchResumeJD.bind(jobfitApi)
export const generateInterview = jobfitApi.generateInterviewQuestions.bind(jobfitApi)
export const submitInterviewAnswer = jobfitApi.submitAnswer.bind(jobfitApi)
export const evaluate = jobfitApi.evaluate.bind(jobfitApi)
export const getSessionStatus = jobfitApi.getSessionStatus.bind(jobfitApi)

export default jobfitApi
