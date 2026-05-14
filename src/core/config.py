from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_debug: bool = True

    # LLM Provider: mimo / deepseek / openai
    llm_provider: str = "mimo"

    # MiMo API
    mimo_api_key: str = ""
    mimo_base_url: str = "https://api.mimo.com/v1"

    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # OpenAI Compatible API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    # Embedding
    embedding_model_path: str = "BAAI/bge-large-zh-v1.5"

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "harmonyos_docs"

    # CSDN
    csdn_cookie: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
