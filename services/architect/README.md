# Architect Agent

The Architect Agent is a deep research agent that can orchestrate multiple tools to provide comprehensive analysis and reports.

## Architect Agent Workflow

The following diagram illustrates the workflow of the Architect Agent when conducting research.

```mermaid
graph TD
    A[ArchitectService - conduct_research] --> B{ArchitectAgent - conduct_research}
    B --> C[Create Research Plan]
    C --> D[Determine Research Type]
    D --> E[Planner Agent - Generate Plan]
    E --> F[Research Plan Created]
    
    B --> G[Execute Research Steps]
    G --> H[Loop through each step]
    H --> I[Tools - execute_tool_action]
    I --> J[Step Result]
    J --> H
    
    B --> K[Synthesize Results]
    K --> L[Collect all findings]
    L --> M[Summarizer Agent - Generate Summary]
    M --> N[Summarizer Agent - Generate Recommendations]
    N --> O[ResearchResult Created]
    
    B --> P[Generate HTML Report]
    P --> Q[HTML Report Created]
    Q --> R[Return ResearchResult]

    %% Subgraphs for logical grouping
    subgraph "Step 1: Planning"
        C
        D
        E
        F
    end

    subgraph "Step 2: Execution"
        G
        H
        I
        J
    end

    subgraph "Step 3: Synthesis"
        K
        L
        M
        N
        O
    end

    subgraph "Step 4: Reporting"
        P
        Q
    end

