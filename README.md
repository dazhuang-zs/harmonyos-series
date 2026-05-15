# HarmonyOS 开发助手（基于 MiMo）

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![MiMo API](https://img.shields.io/badge/MiMo-API-orange.svg)](https://xiaomimimo.com)

一个由 MiMo 大语言模型驱动的 HarmonyOS 开发助手，提供 RAG 文档问答、ArkTS 代码生成、错误诊断、Android→ArkTS 代码迁移以及 CSDN 文章自动发布功能。

## 📦 项目状态

**当前版本**: MVP（里程碑 1）

**进度**:
- [x] 项目立项书
- [x] M0: 项目骨架 & LLM 抽象层（第 1 周）
- [x] M1: RAG 文档问答（第 2-4 周）
- [x] M2: 代码生成（第 5-6 周）
- [x] M3: 错误诊断（第 7-8 周）
- [x] M4: 代码迁移（第 9-10 周）
- [x] M5: CSDN 集成 + Web UI（第 11-12 周）
- [ ] 文档爬取 & 知识库构建
- [ ] 部署 & 上线

---

## 🎯 核心功能

### 1. 基于 RAG 的文档问答

查询华为官方文档和高质量 CSDN 文章，返回准确答案。

**示例**:
```
问：ArkTS 中的 @State 和 @Prop 有什么区别？
答：[MiMo 生成的详细解释，含代码示例...]
```

### 2. ArkTS 代码生成

根据自然语言描述生成可运行的 ArkTS/ArkUI 代码。

**示例**:
```
输入："创建一个带有添加、删除和本地存储功能的 HarmonyOS 待办事项应用"
输出：完整的 DevEco Studio 项目及 .ets 文件
```

### 3. 错误诊断

粘贴编译错误，自动定位原因并提供修复方案。

**示例**:
```
输入："Cannot find module '@ohos/net'..."
输出：[带代码示例的分步修复指南...]
```

### 4. Android → ArkTS 代码迁移

将 Android Java/Kotlin 代码转换为等效的 ArkTS 实现。

**示例**:
```
输入：Android Retrofit API 调用代码
输出：等效的 ArkTS HTTP 请求实现
```

### 5. CSDN 文章自动发布

将问答对和代码示例转换为技术文章，自动发布到 CSDN 草稿。

**示例**:
```
输入：问答对 + 代码示例
输出：发布到 CSDN 草稿（ID: 161090553）
```

---

## 🛠️ 技术栈

| 层级 | 技术选型 | 选择理由 |
|------|------------|--------|
| 后端 | Python 3.11 + FastAPI | 快速开发、生态丰富 |
| 大模型 | MiMo API（正在申请每月 16B Credits 最大额度方案），带支持 DeepSeek/OpenAI 兼容接口的抽象层 | 项目核心驱动 |
| RAG | LangChain + Milvus | 工业级向量检索 |
| 嵌入模型 | BGE-Large-ZH（本地部署） | 中文效果优秀的开源 Embedding 模型，本地部署零成本 |
| 前端 | Next.js 14 + TypeScript | 现代 Web 开发体验 |
| 数据爬取 | Playwright（SPA 渲染）+ BeautifulSoup + Scrapy | 华为文档站为 SPA，需无头浏览器渲染后提取 |
| CSDN 发布 | CSDN Markdown API | 自动发布技术文章 |
| 部署 | Docker + K8s | 可扩展部署 |

---

## 📊 MiMo API 使用场景

> 此部分将直接用于小米 MiMo 激励计划申请表。

### 场景 1: RAG 文档问答

- **输入**: 用户问题（例如："ArkTS 中的 @State 和 @Prop 有什么区别？"）
- **处理流程**: BGE-Large-ZH 向量化 → Milvus 向量检索 → MiMo Chat API 生成答案
- **Token 消耗**: 每次问答约 2000-5000 Token

### 场景 2: ArkTS 代码生成

- **输入**: 自然语言需求（例如："创建一个 HarmonyOS 待办事项应用"）
- **处理流程**: MiMo 生成代码框架 → 单元测试 → 完整的 DevEco Studio 项目
- **Token 消耗**: 每次生成约 5000-10000 Token

### 场景 3: 错误诊断

- **输入**: 编译错误信息
- **处理流程**: MiMo 分析错误 → 检索相似案例 → 生成修复指南
- **Token 消耗**: 每次诊断约 3000-6000 Token

### 场景 4: Android → ArkTS 代码迁移

- **输入**: Android Java/Kotlin 代码
- **处理流程**: MiMo 理解逻辑 → 生成 ArkTS 实现 → 标注迁移说明
- **Token 消耗**: 每 100 行代码约 8000-15000 Token

### 场景 5: CSDN 文章生成

- **输入**: 问答对 + 代码示例
- **处理流程**: MiMo 组织成文章大纲 → 生成完整 Markdown → 通过 CSDN API 发布
- **Token 消耗**: 每篇文章约 4000-8000 Token

### 预计月度 Token 消耗

| 场景 | 日均调用 | 每次调用 Token | 日均消耗 | 月度消耗 |
|----------|-------------|-------------|------------|---------------|
| RAG 文档问答 | 50 | 3500 | 175,000 | 5,250,000 |
| 代码生成 | 20 | 7500 | 150,000 | 4,500,000 |
| 错误诊断 | 30 | 4500 | 135,000 | 4,050,000 |
| 代码迁移 | 10 | 11500 | 115,000 | 3,450,000 |
| 文章生成 | 5 | 6000 | 30,000 | 900,000 |
| **总计** | - | - | **605,000** | **18,150,000** |

> **申请理由**: 月度消耗约 18M Token。如果 1 Credit ≈ 1 Token，那么**每月 16B Credits 最大额度方案**可以支持约 89 个月的使用。实际 Credit 与 Token 的换算比例取决于 MiMo 的定价模型 — 在最终申请前请核实。

---

## 📚 RAG 数据来源

本项目 RAG 系统的知识库由以下数据源构建：

### 主要数据源

| 来源 | 类型 | 获取方式 | 内容 |
|------|------|---------|------|
| [华为开发者文档](https://developer.huawei.com/consumer/cn/doc/) | 官方文档 | Playwright 爬取（SPA 渲染） | ArkTS 语言指南、API 参考、开发指南 |
| [OpenHarmony 仓库](https://gitee.com/openharmony) | 开源项目 | Gitee API / Git Clone | 源码文档、设计文档、API 注释 |
| [CSDN 鸿蒙专栏](https://blog.csdn.net/) | 社区文章 | CSDN API / 爬虫 | 实战教程、踩坑经验 |
| [华为开发者论坛](https://developer.huawei.com/consumer/cn/forum/) | Q&A | 爬虫 | 真实问题与解决方案 |

### 数据获取流程

```
1. 收集 URL 列表（sitemap / 手动整理 / 爬虫发现）
       ↓
2. Playwright 渲染 SPA 页面 → 提取正文 HTML
       ↓
3. BeautifulSoup 解析 → 转为结构化 Markdown
       ↓
4. 按文档标题层级分块（每个 h2/h3 作为一个 chunk）
       ↓
5. BGE-Large-ZH 向量化 → 存入 Milvus
```

### 分块策略

- **按语义切分**：以文档标题（h2/h3）为边界，每个 chunk 包含完整的代码示例和说明
- **保留上下文**：每个 chunk 附带父级标题作为 context（如 `组件 > Button > 属性`）
- **代码块完整**：不拆分代码示例，保证代码的可读性和完整性

### M1 阶段数据目标

- 手动整理 **50-100 篇** 核心文档 URL（ArkTS 语言、常用组件、数据管理等高频主题）
- 构建初始知识库，跑通 RAG 流程
- 后续扩展到自动化爬取 + 增量更新

---

## 🚀 快速开始

### 前置要求

- Python 3.11+
- MiMo API Key（通过 https://100t.xiaomimimo.com 申请）
- 嵌入模型：BGE-Large-ZH（本地部署）
- Milvus（向量存储）
- CSDN 账号（用于自动发布）

### 安装

```bash
git clone https://github.com/dazhuang-zs/harmonyos-series.git
cd harmonyos-series
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 并填写：
# - MIMO_API_KEY=your_mimo_api_key
# - MILVUS_HOST=localhost
# - MILVUS_PORT=19530
# - CSDN_COOKIE=your_csdn_cookie
```

### 运行

```bash
uvicorn src.main:app --reload
```

访问 http://localhost:8000/docs 查看 Swagger UI。

---

## 📂 项目结构

```
harmonyos-mimo-assistant/
├── README.md                    # 项目文档
├── docs/
│   └── project_proposal_zh.md   # 项目立项书
├── src/
│   ├── rag/                     # RAG 模块（文档问答）
│   ├── codegen/                 # 代码生成模块
│   ├── diagnose/                # 错误诊断模块
│   ├── migrate/                 # Android → ArkTS 代码迁移模块
│   ├── publish/                 # CSDN 发布模块
│   └── main.py                  # FastAPI 入口
├── tests/                       # 单元测试
├── scripts/                     # 辅助脚本（爬虫、数据处理）
├── requirements.txt
└── .env.example
```

---

## 📅 开发计划

| 里程碑 | 时间线 | 交付物 |
|-----------|-----------|--------------|
| **M0: 项目初始化 + MiMo 申请** | 第 1 周 | 立项书、MiMo 申请表 |
| **M1: MVP - RAG 文档问答** | 第 2-4 周 | 文档爬取脚本、向量数据库、问答 API |
| **M2: 代码生成** | 第 5-6 周 | ArkTS 代码生成 API、VS Code 插件原型 |
| **M3: 错误诊断** | 第 7-8 周 | 错误诊断 API、Web UI |
| **M4: 代码迁移** | 第 9-10 周 | Android → ArkTS 转换工具 |
| **M5: CSDN 集成** | 第 11-12 周 | 自动发布流程、完整演示 |

---

## 🤝 贡献

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. Fork 此仓库
2. 创建你的功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交你的更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 发起 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE)。

---

## 📮 联系方式

- **项目维护者**: xiaoyuer
- **GitHub Issues**: https://github.com/dazhuang-zs/harmonyos-mimo-assistant/issues
- **CSDN 文章**: https://blog.csdn.net/weixin_43726381
- **MiMo 申请**: https://100t.xiaomimimo.com

---

## 🙏 致谢

- 华为 HarmonyOS 团队提供官方文档
- 小米 MiMo 团队提供 100T Token 激励计划
- CSDN 提供 Markdown API
- LangChain 和 Milvus 开源社区
