from r2r import R2RClient
from config.settings import settings


client = R2RClient(
    base_url=settings.rag_base_url,
)

client.users.create("me@email.com", "my_password")
