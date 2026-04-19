from pathlib import Path

from pydantic_settings import BaseSettings

# Overrides em runtime (frontend pode sobrescrever via POST /settings).
# Prevalecem sobre os valores do .env enquanto o processo estiver rodando.
_overrides: dict = {}


def set_llm_override(**kwargs) -> None:
    for key, value in kwargs.items():
        if value is not None:
            _overrides[key] = value


class Settings(BaseSettings):
    # ── LLM ──────────────────────────────────────────────────────────────────
    # Todos lidos do .env. Os valores aqui são defaults caso não estejam no .env.
    # Troque em runtime via POST /api/v1/settings (sem reiniciar).
    llm_provider: str = "openai"  # openai | ollama | gemini | claude
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096

    openai_api_key: str = ""
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434/v1"

    # ── Embeddings ───────────────────────────────────────────────────────────
    embed_model: str = "BAAI/bge-small-en-v1.5"
    embed_dim: int = 384

    # ── Vector store ─────────────────────────────────────────────────────────
    vector_store: str = "qdrant"
    persist_dir: Path = Path("./data/index")  # usado só pelo FAISS
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # ── Ingestion ────────────────────────────────────────────────────────────
    chunk_size: int = 512
    chunk_overlap: int = 64
    upload_dir: Path = Path("./data/uploads")
    max_upload_files: int = 20

    # ── API ──────────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: str = "http://localhost:8000/api/v1"
    debug: bool = False

    # ── Langfuse (lidos do .env — deixe em branco para desabilitar) ───────────
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # ── Helpers que respeitam overrides de runtime ────────────────────────────
    def get_provider(self) -> str:
        return _overrides.get("llm_provider", self.llm_provider)

    def get_llm_model(self) -> str:
        return _overrides.get("llm_model", self.llm_model)

    def get_active_api_key(self) -> str:
        provider = self.get_provider()
        if provider == "openai":
            return _overrides.get("openai_api_key", self.openai_api_key)

        if provider == "gemini":
            return _overrides.get("gemini_api_key", self.gemini_api_key)

        if provider == "claude":
            return _overrides.get("anthropic_api_key", self.anthropic_api_key)
        return ""  # ollama não precisa de chave

    def get_ollama_base_url(self) -> str:
        return _overrides.get("ollama_base_url", self.ollama_base_url)

    def is_llm_configured(self) -> bool:
        provider = self.get_provider()

        if not self.get_llm_model():
            return False

        if provider == "ollama":
            return True  # base_url tem default, nunca precisa de chave
        return bool(self.get_active_api_key())


settings = Settings()
