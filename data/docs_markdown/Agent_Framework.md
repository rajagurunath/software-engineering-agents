# Agent Framework
A modular framework for orchestrating LLMs, tools, memory, and user interaction.
Welcome to the IO Intelligence Agent Framework — our foundational architecture for building modular, production-grade AI agents. This framework guides how we design, orchestrate, and scale intelligent systems across various use cases.
> ## 📘
> This framework is currently used internally and shared here to help developers understand our AI agent design philosophy.
## [](https://docs.io.net/docs/agent-framework#overview)
This framework brings together the key layers of the modern AI stack and provides a structured approach to building agents that can:
  * Retrieve relevant context and knowledge
  * Reason and make decisions
  * Use external tools and APIs
  * Interact with users through intuitive UIs


It is designed for real-world use cases and is actively used in production.
## [](https://docs.io.net/docs/agent-framework#architecture)
![](https://files.readme.io/f95f974e1e75c3beff44de80b413e384b3e710125ce8f319f1a3d04cb603d966-Orchestration2.jpeg)
At the core of the framework is an **orchestration layer** , powered by **Langchain** and **LlamaIndex**. It acts as the central hub, coordinating data flow and interactions between the following components:
  * **Prompt Engineering**  
Tools like **Langsmith** and **Promptsmith** help design structured prompts and prompt chains that drive agent behavior.
  * **Frontend / UI**  
Built with platforms like **Vercel AI** and **Stramship** , allowing users to interact with agents seamlessly.
  * **AI Tools / Agents**  
We integrate with services such as **VertexAI** and **Postman** to enable action-taking, API execution, and task automation.
  * **Vector Databases**  
**Pinecone** and **Deviate** provide long-term, searchable memory via retrieval-augmented generation (RAG).
  * **LLMs**  
Models from **OpenAI** and **Snowflake** power the core reasoning and natural language understanding behind the agents.


## [](https://docs.io.net/docs/agent-framework#why-orchestration-matters)
AI agents often need to perform multiple tasks in a coordinated flow:
  1. Query memory from a vector database
  2. Call a tool or external API
  3. Interpret results with an LLM
  4. Return structured output to the user


The orchestration layer ensures all these components work together smoothly and reliably.
## [](https://docs.io.net/docs/agent-framework#use-cases)
The IO Intelligence Agent Framework powers a wide variety of real-world applications, including:
  * Autonomous customer support and helpdesk agents
  * Internal copilots for devops, analytics, and operations
  * Document Q&A and knowledge assistants
  * Task agents that combine memory, reasoning, and API execution


## [](https://docs.io.net/docs/agent-framework#built-with)
Layer | Technologies Used  
---|---  
Orchestration | Langchain, LlamaIndex  
Prompt Engineering | Langsmith, Promptsmith  
Frontend | Vercel AI, Stramship  
Tools | VertexAI, Postman  
Vector DBs | Pinecone, Deviate  
LLMs | OpenAI, Snowflake  
* * *
## [](https://docs.io.net/docs/agent-framework#get-involved)
This framework is open source and available on [GitHub repository](https://github.com/ionet-official/iointel). If you’re building agent-based systems or are exploring LLM orchestration, we invite you to explore, fork, and build with it.
15 days ago
* * *
  * [](https://docs.io.net/docs/agent-framework)
  *     * [Overview](https://docs.io.net/docs/agent-framework#overview)
    * [Architecture](https://docs.io.net/docs/agent-framework#architecture)
    * [Why Orchestration Matters](https://docs.io.net/docs/agent-framework#why-orchestration-matters)
    * [Use Cases](https://docs.io.net/docs/agent-framework#use-cases)
    * [Built With](https://docs.io.net/docs/agent-framework#built-with)
    * [Get Involved](https://docs.io.net/docs/agent-framework#get-involved)


