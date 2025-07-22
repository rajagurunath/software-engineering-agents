import os
import json
import requests
import pandas as pd
from vanna.base import VannaBase
from vanna.utils import deterministic_uuid
import vanna
from vanna.base import VannaBase
from langchain_openai import ChatOpenAI
from load_dotenv import load_dotenv
load_dotenv()
import sys
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__))+ "/.." + "/.."+ "/config")
sys.path.append(d)
print(os.environ)
from config.settings import settings

config = dict(model=settings.io_model,  # e.g., "meta-llama/Llama-3.3-70B-Instruct"
            temperature=0,
            max_retries=2,
            api_key=settings.openai_api_key,  # if you prefer to pass api key in directly instaed of using env vars
            base_url=settings.openai_base_url,
            dialect='postgresql',  # Default dialect, can be overridden in config
            max_tokens=14000,
    )

# Simple token storage
_preset_token = None

def refresh_preset_token():
    global _preset_token
    payload = json.dumps({
        "name":  settings.preset_name,
        "secret": settings.preset_secret,
        })
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

class R2R_VectorStore(VannaBase):
    def __init__(self, config=None):
        super().__init__(config)
        if config is None:
            config = {}
        self.api_key = config.get("api_key", settings.openai_api_key)
        self.base_url = config.get("rag_base_url", "https://api.intelligence.io.solutions/api/r2r/v3")
        self.collection_name = config.get("collection_name", "vanna-training-data")
        self.collection_description = config.get("collection_description", "Sql AI Training Data")
        self.collection_id = None
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self._setup_collection()

    def _run_request(self, method, endpoint, headers=None, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        try:
            response = requests.request(method, url, headers=request_headers, **kwargs)
            response.raise_for_status()
            # Handle cases where response might be empty
            if response.status_code == 204 or not response.content:
                return {}
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Handle 409 Conflict for duplicate documents gracefully
            if response.status_code == 409 and method == "POST" and endpoint == "documents":
                print(f"Document already exists (409): {kwargs.get('files', '')}")
                return {"status": "exists"}
            print(f"Error: {e}")
            raise Exception(f"Failed to run request: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            raise Exception(f"Failed to run request: {e}")
        return None

    def _setup_collection(self):
        # First, try to find the collection and get its ID
        response = self._run_request("GET", "collections", headers={"Content-Type": "application/json"})
        if response:
            for collection in response.get('results', []):
                if collection.get('name') == self.collection_name:
                    self.collection_id = collection['id']
                    print(f"Found existing collection '{self.collection_name}' with ID: {self.collection_id}")
                    return

        # If not found, create it
        print(f"Collection '{self.collection_name}' not found. Creating...")
        data = {"name": self.collection_name, "description": self.collection_description}
        response = self._run_request("POST", "collections", headers={"Content-Type": "application/json"}, data=json.dumps(data))
        if response and response.get('results', {}).get('id'):
            self.collection_id = response['results']['id']
            print(f"Collection '{self.collection_name}' created successfully with ID: {self.collection_id}")
        else:
            print(f"Error: Failed to create or find collection '{self.collection_name}'.")

    def _add_document(self, content: str, metadata: dict) -> str:
        if not self.collection_id:
            print("Error: Collection ID is not set. Cannot add document.")
            return None
        doc_id = deterministic_uuid(content)
        files = {
            'raw_text': (None, content),
            'collection_ids': (None, json.dumps([self.collection_name])),
            'metadata': (None, json.dumps(metadata)),
            'ingestion_mode': (None, 'fast'),
            'id': (None, doc_id)
        }
        response = self._run_request("POST", "documents", files=files)
        # Accept both successful and already-exists cases
        if response is not None:
            return doc_id
        return None

    def add_ddl(self, ddl: str, **kwargs) -> str:
        return self._add_document(ddl, {"type": "ddl"})

    def add_documentation(self, doc: str, **kwargs) -> str:
        return self._add_document(doc, {"type": "documentation"})

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        content = f"Question: {question}\nSQL: {sql}"
        return self._add_document(content, {"type": "question_sql", "question": question, "sql": sql})

    def _get_related_documents(self, question: str, doc_type: str, **kwargs) -> list:
        if not self.collection_id:
            print("Error: Collection ID is not set. Cannot perform search.")
            return []

        data = {
            "query": question,
            "filters": {
                "collection_id":self.collection_id
            },
            # "search_mode": "custom",
            # "search_settings": {
            #     "use_semantic_search": True,
            #     "use_fulltext_search": True,
            #     "limit": kwargs.get("limit", 10),  # match curl
            #     "include_metadatas": True,
            #     "include_scores": True
            # }
        }
        response = self._run_request("POST", "retrieval/search", headers={"Content-Type": "application/json"}, data=json.dumps(data))
        if response:
            # Optionally filter by doc_type in Python if needed
            results = response.get("results", {}).get("chunk_search_results", [])
            if doc_type:
                results = [res for res in results if res.get('metadata', {}).get('type') == doc_type]
            return results
        return []

    def get_related_ddl(self, question: str, **kwargs) -> list:
        results = self._get_related_documents(question, "ddl", **kwargs)
        return [res['text'] for res in results]

    def get_related_documentation(self, question: str, **kwargs) -> list:
        results = self._get_related_documents(question, "documentation", **kwargs)
        return [res['text'] for res in results]

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        results = self._get_related_documents(question, "question_sql", **kwargs)
        return [res['metadata'] for res in results]

    def generate_embedding(self, data: str, **kwargs):
        # embedding_model = self._client._get_or_init_model(
        #     model_name=self.fastembed_model
        # )
        # embedding = next(embedding_model.embed(data))

        return [data]


    def get_training_data(self, **kwargs) -> pd.DataFrame:
        response = self._run_request("GET", f"collections/{self.collection_name}/documents")
        if not response or "results" not in response:
            return pd.DataFrame()

        records = []
        for doc in response["results"]:
            doc_type = doc.get("metadata", {}).get("type")
            if doc_type == "ddl":
                records.append({"id": doc["id"], "training_data_type": "ddl", "question": None, "content": doc["content"]})
            elif doc_type == "documentation":
                records.append({"id": doc["id"], "training_data_type": "documentation", "question": None, "content": doc["content"]})
            elif doc_type == "question_sql":
                records.append({"id": doc["id"], "training_data_type": "sql", "question": doc["metadata"]["question"], "content": doc["metadata"]["sql"]})
        
        return pd.DataFrame(records)

    def remove_training_data(self, id: str, **kwargs) -> bool:
        response = self._run_request("DELETE", f"collections/{self.collection_name}/documents/{id}")
        return response is not None



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
  

class IONetDataBot(R2R_VectorStore, IOIntelligence):
    def __init__(self, config=config):
        self.config = config
        self.dialect = 'postgresql'  # Default dialect, can be overridden in config
        R2R_VectorStore.__init__(self, config=config)
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
    vn = IONetDataBot(config={
            'model': settings.io_model,  # e.g., "meta-llama/Llama-3.3-70B-Instruct"
            'max_retries': 2,
            'api_key': settings.openai_api_key,  # if you prefer to pass api key in directly instaed of using env vars
            'base_url': settings.openai_base_url
            }
            )
    add_sql_layer(vn)
    print("SQL Bot initialized with model:", sql_bot.llm.model_name)
    if data_training:
        print("Training data...")
        # ans = vn.ask("how many devices got failed for last few two blocks ?")
        # print("Answer:", ans)
        df_information_schema = pd.DataFrame(vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS"))
        df_information_schema = df_information_schema[~df_information_schema['table_schema'].isin(['pg_catalog','information_schema','cron','extensions',"br_staging"])]
        print(df_information_schema.head(2))
        sql_df = pd.read_csv("/Users/gurunathlunkupalivenugopal/Downloads/ionet internal sql - sql-df.csv")
        for row in sql_df.iterrows():
            question = row[1].questions
            sql = row[1].sqls
            vn.add_question_sql(question=question, sql=sql)
        plan = vn.get_training_plan_generic(df_information_schema)
        vn.train(plan=plan)
    vn.ask(question="How many cpu and gpu devices present?")
