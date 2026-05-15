"""LLM 模型常量配置：集中管理所有模型 ID，方便查找和切换"""


class MiMoModels:
    """小米 MiMo 模型"""
    FLASH = "mimo-v2-flash"          # 轻量快速版
    OMNI = "mimo-v2-omni"            # 多模态版
    PRO = "mimo-v2-pro"              # 专业版
    V25 = "mimo-v2.5"                # v2.5 标准版
    V25_PRO = "mimo-v2.5-pro"        # v2.5 专业版（推荐）
    V25_TTS = "mimo-v2.5-tts"        # 语音合成版
    V25_TTS_CLONE = "mimo-v2.5-tts-voiceclone"   # 语音克隆版
    V25_TTS_DESIGN = "mimo-v2.5-tts-voicedesign"  # 语音设计版

    # 默认模型（推荐使用）
    DEFAULT = V25_PRO


class DeepSeekModels:
    """DeepSeek 模型"""
    CHAT = "deepseek-chat"
    CODER = "deepseek-coder"
    REASONER = "deepseek-reasoner"

    DEFAULT = CHAT


class OpenAIModels:
    """OpenAI 模型"""
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    GPT4_TURBO = "gpt-4-turbo"
    O1 = "o1"
    O3_MINI = "o3-mini"

    DEFAULT = GPT4O


class EmbeddingModels:
    """Embedding 模型"""
    BGE_LARGE_ZH = "BAAI/bge-large-zh-v1.5"    # 中文效果好，1024 维
    BGE_M3 = "BAAI/bge-m3"                      # 多语言，支持混合检索
    GTE_QWEN2 = "Alibaba-NLP/gte-Qwen2-7B-instruct"  # 高精度

    DEFAULT = BGE_LARGE_ZH


# 向量维度映射
EMBEDDING_DIMENSIONS = {
    EmbeddingModels.BGE_LARGE_ZH: 1024,
    EmbeddingModels.BGE_M3: 1024,
    EmbeddingModels.GTE_QWEN2: 3584,
}
