'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import MermaidDiagram from './MermaidDiagram'

export default function WorkflowSection() {
  const [expandedWorkflow, setExpandedWorkflow] = useState<string | null>(null)

  const workflows = [
    {
      id: 'pr-review',
      title: 'PR Review Workflow',
      description: 'Automated pull request review with quality scoring and recommendations',
      diagram: `
        sequenceDiagram
            participant User
            participant SlackBotHandler
            participant PRWorkflows
            participant PRReviewService
            participant GitHubClient
            participant LLMClient
            participant LinearClient

            User->>SlackBotHandler: "review pr <pr_url>"
            SlackBotHandler->>PRWorkflows: pr_review_workflow(request)
            PRWorkflows->>PRReviewService: review_pr(request)
            
            PRReviewService->>GitHubClient: get_pr_details()
            GitHubClient-->>PRReviewService: PR Details
            
            PRReviewService->>GitHubClient: get_pr_diff()
            GitHubClient-->>PRReviewService: PR Diff
            
            PRReviewService->>GitHubClient: get_pr_files()
            GitHubClient-->>PRReviewService: PR Files
            
            opt Linear Issue ID present
                PRReviewService->>LinearClient: get_issue_details()
                LinearClient-->>PRReviewService: Linear Context
            end
            
            PRReviewService->>GitHubClient: get_ci_status()
            GitHubClient-->>PRReviewService: CI Status
            
            PRReviewService->>LLMClient: _analyze_code_quality(diff)
            LLMClient-->>PRReviewService: Quality Analysis
            
            PRReviewService->>LLMClient: _find_bugs(diff)
            LLMClient-->>PRReviewService: Bugs Found
            
            PRReviewService->>PRReviewService: _check_test_coverage(files)
            
            PRReviewService->>LLMClient: _generate_recommendations(...)
            LLMClient-->>PRReviewService: Recommendations
            
            PRReviewService->>LLMClient: _generate_review_summary(...)
            LLMClient-->>PRReviewService: Review Summary
            
            PRReviewService->>GitHubClient: add_pr_comment(summary)
            
            PRReviewService-->>PRWorkflows: PRReviewResponse
            PRWorkflows-->>SlackBotHandler: PRReviewResponse
            SlackBotHandler->>User: Sends review summary
      `
    },
    {
      id: 'pr-creation',
      title: 'PR Creation Workflow',
      description: 'Intelligent PR creation from descriptions with automated implementation',
      diagram: `
        graph TD
            A[User] --> B(SlackBotHandler: create pr);
            B --> C{PRWorkflows: pr_creation_workflow};
            C --> D{Approval Check};
            D -- Yes --> E[ApprovalService: request_approval];
            E --> F[User Approves];
            F --> C;
            D -- No --> G{PRCreatorService: create_pr};
            G --> H[SandboxManager: get_sandbox];
            H --> I[Clone Repo & Create Branch];
            I --> J{LLMClient: generate_implementation_plan};
            J --> K[Implement Changes];
            K --> L[Run Tests];
            L --> M{Tests Passed?};
            M -- No --> N[LLMClient: suggest_test_fixes];
            N --> K;
            M -- Yes --> O[Commit & Push Changes];
            O --> P{GitHubClient: create_pr};
            P --> Q[PR Creation Response];
            Q --> C;
            C --> B;
            B --> A;
      `
    },
    {
      id: 'architect-workflow',
      title: 'Architect Agent Workflow',
      description: 'Deep research and analysis combining multiple tools and data sources',
      diagram: `
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
      `
    },
    {
      id: 'data-workflow',
      title: 'Data Analysis Workflow',
      description: 'IODatabot workflow for network metrics and business intelligence',
      diagram: `
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
      `
    },
    {
      id: 'multimedia-rag',
      title: 'Multimedia RAG Workflow',
      description: 'Audio and video processing with transcription and analysis',
      diagram: `
        graph TD
            subgraph Slack
                User[User uploads audio/video file]
            end

            subgraph Agent Backend
                A[Slack Event Handler] --> B{process_slack_video_event};
                B --> C[Download file from Slack];
                C --> D{VideoRAG: process_video};
                D --> E[Insert into Pixeltable];
                E --> F[Extract audio track];
                F --> G[Transcribe audio with Whisper];
                G --> H[Extract keyframes with OpenCV];
                H --> I{LLMClient: Analyze with Vision Model};
                I --> J[Generate comprehensive analysis];
                J --> K[Return results to user];
            end

            User --> A;
            K --> User;
      `
    }
  ]

  const toggleWorkflow = (id: string) => {
    setExpandedWorkflow(expandedWorkflow === id ? null : id)
  }

  return (
    <div className="space-y-6">
      {workflows.map((workflow, index) => (
        <motion.div
          key={workflow.id}
          className="glass-card overflow-hidden"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: index * 0.1 }}
          viewport={{ once: true }}
        >
          <button
            onClick={() => toggleWorkflow(workflow.id)}
            className="w-full p-6 text-left hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {workflow.title}
                </h3>
                <p className="text-gray-300">
                  {workflow.description}
                </p>
              </div>
              <div className="text-primary-400">
                {expandedWorkflow === workflow.id ? (
                  <ChevronDown className="w-6 h-6" />
                ) : (
                  <ChevronRight className="w-6 h-6" />
                )}
              </div>
            </div>
          </button>
          
          {expandedWorkflow === workflow.id && (
            <motion.div
              className="border-t border-white/10 p-6"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mermaid-container">
                <MermaidDiagram diagram={workflow.diagram} id={workflow.id} />
              </div>
            </motion.div>
          )}
        </motion.div>
      ))}
    </div>
  )
}