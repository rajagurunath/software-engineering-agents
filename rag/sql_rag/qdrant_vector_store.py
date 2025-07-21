import os
import json
import requests
import pandas as pd
from vanna.base import VannaBase
from vanna.utils import deterministic_uuid
import vanna
from vanna.base import VannaBase
from langchain_openai import ChatOpenAI
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from load_dotenv import load_dotenv
load_dotenv()
import sys
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__))+ "/.." + "/.."+ "/config")
sys.path.append(d)
from config.settings import settings

config = dict(model=settings.io_model,  # e.g., "meta-llama/Llama-3.3-70B-Instruct"
            temperature=0,
            client=QdrantClient(url=settings.qdrant_url),  # e.g., "http://localhost:6333"
            max_retries=2,
            api_key=settings.openai_api_key,  # if you prefer to pass api key in directly instaed of using env vars
            base_url=settings.openai_base_url,
            dialect='postgresql',  # Default dialect, can be overridden in config
            max_tokens=10000,
    )

# Simple token storage
_preset_token = None

def refresh_preset_token():
    global _preset_token
    payload = json.dumps({
        "name":  settings.preset_name,
        "secret": settings.preset_secret,
        })
    print("payload:", payload)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", settings.preset_api_url, headers=headers, data=payload)
    print(response.raise_for_status())
    _preset_token = response.json()["payload"]['access_token']

def get_preset_token():
    global _preset_token
    return _preset_token

def run_sql(sql: str):
    url = settings.superset_api_url+ "/api/v1/sqllab/execute/"
    print(url)
    DatabaseID = 4  # prod_ionet.value 
    payload = {"database_id": DatabaseID,"sql": sql}
    headers = {
      'Authorization': f'Bearer {get_preset_token()}',
      'Content-Type': 'application/json',
      'Referer': 'https://68ab3360.us2a.app.preset.io'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    print("run_sql:",response.text[:100])
    if response.status_code != 200:
        print(f"Error running SQL: {response.status_code} - {response.text}")
        raise Exception(f"Error running SQL: {response.status_code} - {response.text}")
    return response.json()['data']


class IOIntelligence(VannaBase):
  def __init__(self, config={}):
    self.dialect = config.get('dialect')
    self.max_tokens = config.get("max_tokens")
    self.llm = ChatOpenAI(
        model= config.get("model"),
        temperature=config.get("temperature"),
        max_tokens=self.max_tokens,
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
        question += " Note: Another important thing is to use user_id or device_id in the sql query correctly generate the working postgres sql query"
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
  

class IONetDataBot(Qdrant_VectorStore, IOIntelligence):
    def __init__(self, config=config):
        self.config = config
        self.dialect = 'postgresql'  # Default dialect, can be overridden in config
        Qdrant_VectorStore.__init__(self, config=config)
        IOIntelligence.__init__(self, config=config)

def add_sql_layer(vn: VannaBase):
    # This gives the package a function that it can use to run the SQL
    vn.run_sql = run_sql
    vn.run_sql_is_set = True

if __name__ == "__main__":
    # Example usage
    refresh_preset_token()
    data_training = False
    sql_bot = IONetDataBot()
    vn = IONetDataBot(config=config
            )
    add_sql_layer(vn)
    print("SQL Bot initialized with model:", sql_bot.llm.model_name)
    if data_training:
        print("Training data...")
        # ans = vn.ask("how many devices got failed for last few two blocks ?")
        # print("Answer:", ans)
        df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
        df_information_schema = df_information_schema[~df_information_schema['table_schema'].isin(['pg_catalog','information_schema','cron','extensions',"br_staging"])]
        print(df_information_schema.head(2))
        sql_df = pd.read_csv("/Users/gurunathlunkupalivenugopal/Downloads/ionet internal sql - sql-df.csv")
        for row in sql_df.iterrows():
            question = row[1].questions
            sql = row[1].sqls
            vn.add_question_sql(question=question, sql=sql)
        plan = vn.get_training_plan_generic(df_information_schema)
        vn.train(plan=plan)
    vn.ask(question="How many devices failed to earn block rewards for each block today ?")
