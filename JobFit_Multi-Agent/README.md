# JobFit Multi-Agent - 智能简历优化与面试模拟系统

一个基于多智能体协作的简历优化和面试模拟系统，采用 Flask 后端 + Vue 前端架构。系统包含4个智能体协同工作，提供从简历解析、岗位匹配、模拟面试到综合评价的全流程服务。

## ✨ 核心功能

### 🤖 四大智能体

1. **JD 解析 Agent**
   - 自动提取岗位要求与技能
   - 识别必需技能和加分技能
   - 结构化输出职位信息

2. **简历匹配 Agent**
   - 对比简历经历与岗位要求
   - 标注技能短板和优势
   - 给出匹配度评分（0-100）

3. **模拟面试 Agent**
   - 基于JD和简历自动生成面试题
   - 支持多轮追问机制
   - 针对性考察薄弱环节

4. **评价 Agent**
   - 综合打分并给出修改建议
   - 提供简历优化方案
   - 制定面试准备行动计划


### 📄 简历多格式支持

| 格式 | 说明 | 依赖 |
|------|------|------|
| **PDF** | 标准文本PDF | PyPDF2（已内置） |
| **DOCX** | Word文档 | python-docx（已内置） |
| **TXT** | 纯文本文件 | 自动编码检测（已内置） |
| **JPG/PNG** | 图片简历（扫描件/截图） | **需要安装 Tesseract OCR** |

**⚠️ 重要提示**: 
- 上传 JPG/PNG 格式前，**必须安装 Tesseract OCR 引擎**
- Windows 用户需在 `.env` 文件中配置 `TESSERACT_PATH` 为实际安装路径
- Docker 环境已内置 Tesseract，无需额外配置

### 🔄 完整工作流程

```
上传简历 → 输入JD → 匹配分析 → 模拟面试 → 综合评价
```

## 🛠️ 技术栈

### 后端
- **框架**: Flask 2.3.3
- **LLM集成**: OpenAI兼容API（支持Ollama本地模型）
- **文档解析**: PyPDF2、python-docx、chardet
- **OCR识别**: pytesseract、Pillow
- **跨域支持**: flask-cors

### 前端
- **框架**: Vue 3.3+
- **构建工具**: Vite 4.4+
- **HTTP客户端**: Axios
- **路由**: Vue Router 4.2+

## 📁 项目结构

```
JobFit_Multi-Agent/
├── backend/                    # 后端代码
│   ├── agents/                # 智能体模块
│   │   ├── jd_parser.py       # JD解析智能体
│   │   ├── resume_matcher.py  # 简历匹配智能体
│   │   ├── interview_simulator.py  # 模拟面试智能体
│   │   └── evaluator.py       # 评价智能体
│   ├── utils/                 # 工具模块
│   │   ├── llm_client.py      # LLM客户端
│   │   ├── file_parser.py     # 文件解析器
│   │   └── ocr_handler.py     # OCR处理器
│   ├── uploads/               # 上传文件存储
│   ├── config.py              # 配置文件
│   ├── app.py                 # Flask应用入口
│   ├── requirements.txt       # Python依赖
│   └── .env                   # 环境变量
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── api/
│   │   │   ├── jobfit.js      # API接口封装
│   │   │   └── index.js       # API统一导出
│   │   ├── views/
│   │   │   └── HomeView.vue   # 主页面
│   │   ├── router/
│   │   │   └── index.js       # 路由配置
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── index.html             # HTML模板
│   ├── package.json           # Node依赖
│   └── vite.config.js         # Vite配置
├── docker-compose.yml         # Docker编排文件
├── Dockerfile.backend         # 后端Dockerfile
├── Dockerfile.frontend        # 前端Dockerfile
└── README.md                  # 项目说明
```

---

## 🚀 本地部署（推荐）

### 前置要求

#### 1. 基础环境
- **Python 3.8+**
- **Node.js 16+**

#### 2. LLM 服务（二选一）

**方案A: Ollama 本地模型（推荐，免费）**
- 下载安装：https://ollama.ai
- 拉取模型：`ollama pull qwen2.5:7b`
- 启动服务：`ollama serve`

**方案B: 云端 API（付费）**
- OpenAI、DeepSeek、阿里云通义千问等
- 需获取 API Key

#### 3. Tesseract OCR（可选，用于图片简历）

**Windows**:
- 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
- 安装时勾选中文语言包（Chinese Simplified）
- 记录安装路径（如 `F:\rj\Tesseract-OCR`）

**验证安装**:
```bash
tesseract --version
```

---

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd JobFit_Multi-Agent
```

#### 2. 后端配置

##### 2.1 创建虚拟环境

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

##### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

##### 2.3 配置环境变量

复制配置文件：
```bash
cp .env.example .env
```

编辑 `backend/.env` 文件：

```env
# Flask配置
SECRET_KEY=jobfit-secret-key-2024
DEBUG=True

# ========== LLM API配置（三选一）==========

# 方案1: Ollama本地模型（推荐，免费）
LLM_API_URL=http://localhost:11434/api/chat
LLM_API_KEY=
LLM_MODEL=qwen2.5:7b

# 方案2: OpenAI云端API（需要API密钥）
# LLM_API_URL=https://api.openai.com/v1/chat/completions
# LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# LLM_MODEL=gpt-4o


LLM_TEMPERATURE=0.7

# ========== OCR配置 ==========
OCR_ENABLED=True

# Tesseract OCR 路径（Windows用户必填）
# Windows示例: TESSERACT_PATH=F:\\rj\\Tesseract-OCR\\tesseract.exe

```

**⚠️ 重要提示**:
- Windows 用户如果使用图片上传功能，**必须配置 `TESSERACT_PATH`**
- 路径中的反斜杠需要使用双反斜杠转义（`\\`）
- 配置后需重启后端服务才能生效

#### 3. 前端配置

```bash
cd ../frontend

# 安装依赖
npm install
```

---

### 启动服务

打开**两个终端窗口**：

**终端1 - 启动后端**:
```bash
cd backend
python app.py
```

**终端2 - 启动前端**:
```bash
cd frontend
npm run dev
```

### 访问应用

- 🌐 **前端界面**: http://localhost:3000
- 🔧 **后端API**: http://localhost:5000

---
---


## 🐳 Docker 部署

### 前置要求

- **Docker Desktop** (Windows/Mac) 或 **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **Ollama** 在宿主机运行（用于 LLM）

### 快速启动

```bash
# 1. 构建并启动所有服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 配置说明

**连接宿主机 Ollama**：
- Docker Compose 已配置 `LLM_API_URL=http://host.docker.internal:11434/api/chat`
- Windows: `host.docker.internal` 自动解析到宿主机
**Tesseract OCR**：
- Dockerfile 已内置 Tesseract 引擎和中文语言包
- 无需额外配置，开箱即用

### 数据持久化

上传的文件存储在 `backend/uploads/` 目录，已通过 volume 挂载到宿主机，容器重启后数据不丢失。

### 访问应用

- 🌐 **前端**: http://localhost:3000
- 🔧 **后端API**: http://localhost:5000

---

## ❓ 常见问题

### 1. 上传图片显示"不支持的格式"

**原因**: 未安装或未配置 Tesseract OCR

**解决方案**:
- 安装 Tesseract（见前置要求第3节）
- Windows 用户在 `.env` 中配置 `TESSERACT_PATH`
- 重启后端服务

### 2. API 调用失败

**检查项**:
- 确认 LLM 服务是否正常运行
- 检查 `.env` 中的 `LLM_API_URL` 是否正确
- 如使用云端 API，确认 `LLM_API_KEY` 有效且有余额

### 3. 前端无法连接后端

**检查项**:
- 确认后端服务已启动（http://localhost:5000）
- 检查浏览器控制台是否有 CORS 错误
- 确认防火墙未阻止 5000 端口

### 4. Docker 容器无法启动

**检查项**:
- 确认 Docker Desktop 正在运行
- 检查端口 3000 和 5000 是否被占用
- 查看日志：`docker-compose logs`

---

## 🙏 致谢

感谢以下开源项目的支持：
- **Flask** - 轻量级Web框架
- **Vue.js** - 渐进式JavaScript框架
- **Element Plus** - 优秀的UI组件库
- **Ollama** - 本地LLM运行平台
- **PyPDF2** - PDF解析库
- **python-docx** - Word文档处理
- **pytesseract** - OCR识别引擎
- **Vite** - 下一代前端构建工具


