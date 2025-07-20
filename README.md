## Decentralised Software agents for startups and Enterprises

Nowadays Agent can do mind blowing things. They can write code, create content, and even manage complex tasks autonomously. This repository is a collection of such agents that can be used to build your own AI applications.

With help of io.net io intelligence, we can access open source model all the time.
if needed we can deploy our own model in io.net platform. 

We can use io.net CaaS or Baremetal clusters to deploy the LLM Models as well, which can be used to build all this enterprise Agents.

## ! Important by controlling the LLM Model, we can ensure data privacy and compliance with regulations. 
- We can share the propertieray code to this models without fear of data leaks.
- And also the data related information also be shared with the model since it is self hosted and privacy is ensured.
- if needed you can save this conversations , collect the dataset and use io.net's TaaS to train/fine-tune the model with your own data. 

This gives the complete self improving life cycle of the Agent ecosystem in a organisation.

## UseCases

### Agents Team available in this repository:
- Software Architect Agent
    - Research Agent , who can connect with all the other agent, plan the task and provide complete end to end solution
- Junior Engineering Agent
    - Can read docs and write code, create PRs, handle PR comments, PR reviews
- Senior Engineering Agent
    - All the Junior Engineering Agent capabilities, plus can handle complex tasks, review code, and provide architectural guidance,
    - Senior Engineering Agent has good grasp of the architecture behind the application and can answer all the complex questions about the github repository, architecture of each frameworks used in the organisation.
- Data Analyst Agent
    - Can analyze data, generate reports, and provide insights to the team.
    - Can create dashboards and visualizations to help the team understand the data better.
- Sentry Agent
    - Can monitor the application, detect issues, and provide alerts to the team.

Currently all this agents are accessible from **Slack**. By using this Agents

- Each person can manage a team of agents to handle all the tasks - Everyone is leading a team of agents
- Answer all questions about the codebase, architecture, and data.
- Can create PRs, handle PR comments, and review code.
- ## importantly Vibe code the entire fixes, features and improvements from convience of slack.  No editor needed. 
    - just io-intelligence and Slack is enough to create, manage and improve code

- Suddenly every person in the organisation is a product Engineer, everyone can work for product improvements and suggest new things to the product.
- This Agent Team can help achieve 10x productivity of the team , by colloborating with each other and providing the best solutions to the problems.
- you can slack call all this agent and explain the problem statement and spend your energy somewhere else, agents work on the problem statement and get back with proper solution, Every software egnineer is reviewer now.



## How to use this repository
- This repository contains end to end code workflows to deploy agents to your organisation.

Preparation for Agents Team: (pre-deployment phase)
- Web scraping 
   - `rag/web_crawler/scraper.py`
     - This script scrapes the organisation's product description, api documentation etc.
     - Check the scraped data sample `data/docs_markdown`
- Data Schema Scraping from the RDS
    - `rag/sql_rag/qdrant_vector_store.py`
      - This script scrapes the data schema from the RDS and creates a vector store for the data.
    - Additionally adds the day to day sqls used across the team
- Additional Data related Questions (gathered from team mates which we use on day to day basiss)

- indexing the data
  - `rag/indexer/indexer.py`
    - This script indexes the data scraped from the web and RDS into a vector store.
    - It uses both the io.net R2R RAG APIs and Qdrant as the vector store and SentenceTransformer for embedding the data.
        - we use qdrant because we exceeded the daily limit of R2R RAG APIs, otherwise R2R RAG APIs are enough to index the data.
   - `rag/indexer/embedder.py`
     - This script embeds the data into the vector store.
     - It can be used to test the embedding of json files standalone.

Deploy Agents Team:
- Create a slack bot and provide the api key for each bot

- Monitor the agents and their performance
  - monitor the conversations between the agents and the team 
  - Trace the performance, latency of api calls ,tool calls etc.
  - we use opik for observability and monitoring of the agents

Self Improvement of Agents Team:
  - By gathering the data from the conversations, we can collect the prompts and annotate the useful prompts and use them for following
    - We can fine-tune the RAG Dataset as well which will eventually improves the performance of the agents.
    - We can use the TaaS to train the model with the collected data.
    







