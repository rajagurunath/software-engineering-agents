import vanna
from vanna.base import VannaBase
from vanna.qdrant import Qdrant_VectorStore
# from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI



class IOIntelligence(VannaBase):
  def __init__(self, config={}):
      
    self.llm = ChatOpenAI(
        model= config.get("model"),
        temperature=config.get("temperature"),
        # max_tokens=config.get("max_tokens"),
        timeout=config.get("timeout"),
        # max_retries=config.get("max_retries"),
        api_key=config.get("api_key"),
        base_url=config.get("base_url"),
    )
  def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

  def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

  def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}

  def generate_sql(self, question: str, **kwargs) -> str:
        # Use the super generate_sql
        print("generate_sql:",question)
        question += " Note: Very important generate sql with fully qualified table_names i.e {schema_name}.{table_name} example block_rewards.blocks Always follow this one"
        sql = super().generate_sql(question, **kwargs)
        print(sql)
        # Replace "\_" with "_"
        sql = sql.replace("\\_", "_")

        return sql
  # @observe()
  def submit_prompt(self, prompt, **kwargs) -> str:
      # ai_msg = self.llm.invoke(prompt,config={"callbacks": [langfuse_handler]})
      ai_msg = self.llm.invoke(prompt)
      return ai_msg.content

  def generate_query_explanation(self, sql: str):
      my_prompt = [
            self.system_message("""You are a helpful assistant which prepares json document with sqlexplanation and schema 
                    - explain a SQL query
                    - Also provide schema name separately in a json format 
                    example {"explanation":"This sql queries blocks table and provides number of records", schema:"block_rewards"}
                    Note: your job is to output a json, dont speak anything else
                    """),
            self.user_message("json: " + sql),
        ]
      return self.submit_prompt(prompt=my_prompt)
  

class IONetVanna(Qdrant_VectorStore, IOIntelligence):
    def __init__(self, config):
        Qdrant_VectorStore.__init__(self, config=config)
        IOIntelligence.__init__(self, config=config)
