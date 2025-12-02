"""Configuration management for the Financial Education Quiz Engine."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: str = "openai"
    model: str = Field(default_factory=lambda: os.getenv("DEFAULT_LLM_MODEL", "gpt-4-turbo-preview"))
    temperature: float = 0.7
    max_tokens: int = 2000

class MCPConfig(BaseModel):
    """MCP Server configuration."""
    base_url: str = Field(default_factory=lambda: os.getenv("MCP_SERVER_URL", "http://localhost:8000"))
    timeout: int = 30
    endpoints: Dict[str, str] = {}

class EmbeddingsConfig(BaseModel):
    """Embeddings configuration."""
    model: str = "all-MiniLM-L6-v2"
    dimension: int = 384

class VectorStoreConfig(BaseModel):
    """Vector store configuration."""
    type: str = "faiss"
    index_path: str = "./data/vector_store/education.index"
    metadata_path: str = "./data/vector_store/metadata.pkl"
    top_k: int = 5

class GamificationConfig(BaseModel):
    """Gamification settings."""
    points_per_correct: int = 10
    points_per_quiz: int = 50
    levels: list = []
    badges: list = []

class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from YAML file and environment variables."""
        self.config_path = config_path or os.path.join(
            Path(__file__).parent.parent, "config.yaml"
        )
        self._config_data = self._load_config()
        
        # Initialize configuration models
        self.llm = LLMConfig(**self._config_data.get("llm", {}))
        self.embeddings = EmbeddingsConfig(**self._config_data.get("embeddings", {}))
        self.mcp = MCPConfig(**self._config_data.get("mcp", {}))
        self.vector_store = VectorStoreConfig(**self._config_data.get("vector_store", {}))
        self.gamification = GamificationConfig(**self._config_data.get("gamification", {}))
        
        # Additional settings
        self.age_groups = self._config_data.get("age_groups", [])
        self.financial_concepts = self._config_data.get("financial_concepts", [])
        self.app_settings = self._config_data.get("app", {})
        
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}. Using defaults.")
            return {}
    
    def get_age_group(self, age: int) -> Optional[Dict[str, Any]]:
        """Get age group configuration for a given age."""
        for group in self.age_groups:
            if group["min_age"] <= age <= group["max_age"]:
                return group
        return None
    
    def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get financial concept by ID."""
        for concept in self.financial_concepts:
            if concept["id"] == concept_id:
                return concept
        return None
    
    def get_level_for_points(self, points: int) -> Dict[str, Any]:
        """Determine user level based on points."""
        for level in self.gamification.levels:
            if level["min_points"] <= points <= level["max_points"]:
                return level
        return self.gamification.levels[-1]  # Return highest level if points exceed

# Global configuration instance
config = Config()
