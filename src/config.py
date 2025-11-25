"""Configuration management for the agentic BOP workflow."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    model_name_openai: str = os.getenv("MODEL_NAME_OPENAI", "gpt-4o")
    model_name_anthropic: str = os.getenv("MODEL_NAME_ANTHROPIC", "claude-3-5-sonnet-20241022")
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))
    
    def validate(self) -> None:
        """Validate that required settings are present."""
        if not self.openai_api_key and not self.anthropic_api_key:
            raise ValueError(
                "At least one API key must be set: OPENAI_API_KEY or ANTHROPIC_API_KEY"
            )


settings = Settings()
