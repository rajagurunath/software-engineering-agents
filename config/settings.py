from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # Slack Configuration
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_app_token: str = Field(..., env="SLACK_APP_TOKEN")
    slack_signing_secret: str = Field(..., env="SLACK_SIGNING_SECRET")

    # Architect Bot Configuration
    slack_architect_bot_token: str = Field(..., env="SLACK_ARCHITECT_BOT_TOKEN")
    slack_architect_app_token: str = Field(..., env="SLACK_ARCHITECT_APP_TOKEN")
    slack_architect_signing_secret: str = Field(..., env="SLACK_ARCHITECT_SIGNING_SECRET")
    
    # Developer Bot Configuration
    slack_developer_bot_token: str = Field(..., env="SLACK_DEVELOPER_BOT_TOKEN")
    slack_developer_app_token: str = Field(..., env="SLACK_DEVELOPER_APP_TOKEN")
    slack_developer_signing_secret: str = Field(..., env="SLACK_DEVELOPER_SIGNING_SECRET")
    
    # Data Analyst Bot Configuration
    slack_data_analyst_bot_token: str = Field(..., env="SLACK_DATA_ANALYST_BOT_TOKEN")
    slack_data_analyst_app_token: str = Field(..., env="SLACK_DATA_ANALYST_APP_TOKEN")
    slack_data_analyst_signing_secret: str = Field(..., env="SLACK_DATA_ANALYST_SIGNING_SECRET")
    
    # Sentry Bot Configuration
    slack_sentry_bot_token: str = Field(..., env="SLACK_SENTRY_BOT_TOKEN")
    slack_sentry_app_token: str = Field(..., env="SLACK_SENTRY_APP_TOKEN")
    slack_sentry_signing_secret: str = Field(..., env="SLACK_SENTRY_SIGNING_SECRET")

    sql_bot_url: str = Field(..., env="SQL_BOT_URL")
    
    # GitHub Configuration
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_org: str = Field(..., env="GITHUB_ORG")
    
    # Linear Configuration
    linear_api_key: str = Field(..., env="LINEAR_API_KEY")
    
    # LLM Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    iointelligence_api_key: str = Field(..., env="IOINTELLIGENCE_API_KEY")
    openai_base_url: str = Field("https://api.openai.com/v1", env="OPENAI_BASE_URL")
    io_model:str = Field("deepseek-ai/DeepSeek-R1-0528", env="IO_MODEL")
    
    # Sandbox Configuration
    sandbox_base_path: str = "/tmp/sandbox"
    max_concurrent_sandboxes: int = 5
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    slack_port: int = Field(5000, env="SLACK_PORT")

    # Channels
    approvals_channel: str = Field("#approvals", env="APPROVALS_CHANNEL")

    # Feature Flags
    skip_approvals: bool = Field(False, env="SKIP_APPROVALS")
    skip_clarifications: bool = Field(True, env="SKIP_CLARIFICATIONS")
    share_plan_to_slack: bool = Field(True, env="SHARE_PLAN_TO_SLACK")
    opik_endpoint: str = Field("http://localhost:8123/trace", env="OPIK_ENDPOINT")

    # Rag configuration
    rag_base_url: str = Field("https://api.intelligence-dev.io.solutions/api/r2r/v3", env="RAG_BASE_URL")
    superset_api_url: str = Field("http://localhost:8088", env="SUPERSET_API_URL")
    preset_api_url: str = Field("http://localhost:8088", env="PRESET_API_URL")
    preset_secret: str = Field("preset_api_key", env="PRESET_SECRET")
    preset_name: str = Field("preset", env="PRESET_NAME")
    qdrant_url: str = Field("http://localhost:6333", env="QDRANT_URL")
    qdrant_collection_name: str = Field("io_net_docs", env="QDRANT_COLLECTION_NAME")
    qdrant_embedding_model_name: str = Field("sentence-transformers/all-mpnet-base-v2", env="QDRANT_EMBEDDING_MODEL_NAME")
    qdrant_top_k: int = Field(5, env="QDRANT_TOP_K")

    # Sentry Configuration
    sentry_auth_token: str = Field(..., env="SENTRY_AUTH_TOKEN")
    sentry_org_slug: str = Field(..., env="SENTRY_ORG_SLUG")
    sentry_project_slug: str = Field(..., env="SENTRY_PROJECT_SLUG")

    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))

settings = Settings()
