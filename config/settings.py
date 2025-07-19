from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Slack Configuration
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_app_token: str = Field(..., env="SLACK_APP_TOKEN")
    slack_signing_secret: str = Field(..., env="SLACK_APP_TOKEN")

    # slack_sql_bot_token: str = Field(..., env="SLACK_SQL_BOT_TOKEN")
    # slack_sql_app_token: str = Field(..., env="SLACK_SQL_APP_TOKEN")
    # slack_sql_signing_secret: str = Field(..., env="SLACK_SQL_SIGNING_SECRET")

    sql_bot_url: str = Field(..., env="SQL_BOT_URL")
    
    # GitHub Configuration
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_org: str = Field(..., env="GITHUB_ORG")
    
    # Linear Configuration
    linear_api_key: str = Field(..., env="LINEAR_API_KEY")
    
    # LLM Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
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
    rag_base_url: str = Field("https://api.intelligence.io.solutions", env="RAG_BASE_URL")
    
    class Config:
        env_file = ".env"

settings = Settings()