# Data Support Services

This module contains services related to data analysis and retrieval, including the IODatabot.

## IODatabot Workflow

The following diagram illustrates the workflow of the IODatabot when answering a data-related question.

```mermaid
sequenceDiagram
    participant User
    participant ArchitectTools
    participant IONetDataBot
    participant LLMClient
    participant VectorDB
    participant PresetDatabase

    User->>ArchitectTools: Asks a question (e.g., "How many devices are online?")
    ArchitectTools->>IONetDataBot: query_data(question)
    
    IONetDataBot->>VectorDB: Search for similar questions/SQL
    VectorDB-->>IONetDataBot: Returns relevant examples
    
    IONetDataBot->>LLMClient: generate_sql(question, examples)
    LLMClient-->>IONetDataBot: SQL Query
    
    IONetDataBot->>PresetDatabase: run_sql(sql)
    PresetDatabase-->>IONetDataBot: Query Result (DataFrame)
    
    IONetDataBot->>LLMClient: generate_plotly_code(question, sql, df)
    LLMClient-->>IONetDataBot: Plotly Code
    
    IONetDataBot->>IONetDataBot: get_plotly_figure(code, df)
    
    IONetDataBot->>LLMClient: generate_followup_questions(question, sql, df)
    LLMClient-->>IONetDataBot: Follow-up Questions
    
    IONetDataBot-->>ArchitectTools: Returns data, chart, and follow-up questions
    ArchitectTools-->>User: Sends formatted response
