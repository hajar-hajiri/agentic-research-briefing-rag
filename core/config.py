from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    llm_provider: str = Field(default="none", alias="LLM_PROVIDER")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")

    top_k: int = Field(default=12, alias="TOP_K")
    bm25_k: int = Field(default=30, alias="BM25_K")
    dense_k: int = Field(default=30, alias="DENSE_K")
    rerank: bool = Field(default=True, alias="RERANK")

    data_raw_pdfs: str = Field(default="data/raw/pdfs", alias="DATA_RAW_PDFS")
    data_raw_pages: str = Field(default="data/raw/pages", alias="DATA_RAW_PAGES")
    data_runs: str = Field(default="data/runs", alias="DATA_RUNS")

    min_distinct_sources: int = Field(default=2, alias="MIN_DISTINCT_SOURCES")
    max_citations: int = Field(default=8, alias="MAX_CITATIONS")

    class Config:
        env_file = ".env"
        extra = "ignore"
