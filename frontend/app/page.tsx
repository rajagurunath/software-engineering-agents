'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Bot, 
  Code, 
  Database, 
  Shield, 
  Zap, 
  GitBranch, 
  BarChart3, 
  AlertTriangle,
  Play,
  Github,
  Youtube,
  ArrowRight,
  CheckCircle,
  Cpu,
  Network,
  Users,
  Sparkles
} from 'lucide-react'
import MermaidDiagram from './components/MermaidDiagram'
import CodeBlock from './components/CodeBlock'
import FeatureCard from './components/FeatureCard'
import AgentCard from './components/AgentCard'
import WorkflowSection from './components/WorkflowSection'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')

  const agents = [
    {
      name: 'Architect Agent',
      icon: <Cpu className="w-8 h-8" />,
      description: 'Deep research, data analysis, documentation synthesis, and multi-tool orchestration',
      capabilities: [
        'Comprehensive research combining multiple data sources',
        'Data visualization with interactive charts',
        'Documentation synthesis and analysis',
        'Multi-step workflow orchestration',
        'Context-aware analysis with user/device targeting'
      ],
      color: 'from-blue-500 to-cyan-500'
    },
    {
      name: 'Developer Agent',
      icon: <Code className="w-8 h-8" />,
      description: 'Complete GitHub workflow automation and code quality management',
      capabilities: [
        'Automated PR reviews with quality scoring',
        'Intelligent PR creation from descriptions',
        'PR comment resolution and code fixes',
        'GitHub integration and workflow automation',
        'Linear ticket integration'
      ],
      color: 'from-green-500 to-emerald-500'
    },
    {
      name: 'Data Analyst Agent',
      icon: <BarChart3 className="w-8 h-8" />,
      description: 'Network data analysis, reporting, and business intelligence',
      capabilities: [
        'SQL query generation and execution',
        'Interactive data visualizations',
        'Comprehensive report generation',
        'Performance metrics analysis',
        'Business intelligence insights'
      ],
      color: 'from-purple-500 to-violet-500'
    },
    {
      name: 'Sentry Agent',
      icon: <AlertTriangle className="w-8 h-8" />,
      description: 'Production monitoring, error debugging, and incident response',
      capabilities: [
        'Sentry issue analysis and debugging',
        'Log analysis and pattern recognition',
        'Error root cause analysis',
        'Production incident response',
        'Automated debugging workflows'
      ],
      color: 'from-red-500 to-orange-500'
    },
    {
      name: 'Main Dispatcher',
      icon: <Network className="w-8 h-8" />,
      description: 'Central coordination, file processing, and agent discovery',
      capabilities: [
        'Audio/video file transcription',
        'Agent routing and discovery',
        'Help and documentation',
        'File processing workflows',
        'Cross-agent coordination'
      ],
      color: 'from-indigo-500 to-purple-500'
    }
  ]

  const architectureDiagram = `
    graph TB
        subgraph "Slack Workspace"
            U[Users]
            C[Channels]
        end
        
        subgraph "Multi-Bot System"
            MD[Main Dispatcher Bot<br/>@main-bot]
            AB[Architect Bot<br/>@architect-bot]
            DB[Developer Bot<br/>@developer-bot]
            DAB[Data Analyst Bot<br/>@data-analyst-bot]
            SB[Sentry Bot<br/>@sentry-bot]
        end
        
        subgraph "Services Layer"
            AS[Architect Service]
            PRW[PR Workflows]
            SD[Sentry Debugger]
            RAG[RAG Systems]
            LLM[LLM Clients]
        end
        
        subgraph "External Integrations"
            GH[GitHub API]
            LIN[Linear API]
            SENT[Sentry API]
            DB_SYS[Database Systems]
        end
        
        U --> MD
        U --> AB
        U --> DB
        U --> DAB
        U --> SB
        
        MD --> AS
        AB --> AS
        AB --> RAG
        DB --> PRW
        DB --> GH
        DAB --> AS
        DAB --> DB_SYS
        SB --> SD
        SB --> SENT
        
        AS --> LLM
        PRW --> GH
        PRW --> LIN
        SD --> LLM
  `

  const workflowDiagram = `
    graph TD
        subgraph User_and_Slack
            User[Slack User] --> SlackAPI[Slack API]
        end

        subgraph Agent_Backend
            style Agent_Backend fill:#f9f9f9,stroke:#333,stroke-width:2px
            Bots[Multi-Bot System] --> Workflows[Durable Workflows - DBOS]
            Workflows --> Services[Agent Services - Architect, Developer, Data]
            Services --> Clients[API Clients - GitHub, LLM, RAG]
        end

        subgraph External_Services_and_Data
            style External_Services_and_Data fill:#f0f8ff,stroke:#333,stroke-width:2px
            GitHub[GitHub API]
            LLM[LLM Provider - io.net Intelligence]
            RAG[RAG System - Vector DB, Preset BI Tool]
        end

        SlackAPI -- Event --> Bots
        Clients --> GitHub
        Clients --> LLM
        Clients --> RAG

        RAG --> Clients
        GitHub --> Clients
        LLM --> Clients

        Bots -- Response --> SlackAPI
        SlackAPI --> User
  `

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 glass-card border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div 
              className="flex items-center space-x-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Bot className="w-8 h-8 text-primary-400" />
              <span className="text-xl font-bold gradient-text">Software Engineering Agents</span>
            </motion.div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#overview" className="hover:text-primary-400 transition-colors">Overview</a>
              <a href="#architecture" className="hover:text-primary-400 transition-colors">Architecture</a>
              <a href="#agents" className="hover:text-primary-400 transition-colors">Agents</a>
              <a href="#workflows" className="hover:text-primary-400 transition-colors">Workflows</a>
              <a href="#setup" className="hover:text-primary-400 transition-colors">Setup</a>
            </div>

            <motion.div 
              className="flex items-center space-x-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <a 
                href="https://github.com/rajagurunath/software-engineering-agents" 
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
              >
                <Github className="w-4 h-4" />
                <span>GitHub</span>
              </a>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Decentralised Software Agents</span>
              <br />
              <span className="text-white">for Startups & Enterprises</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto">
              Powered by <span className="text-primary-400 font-semibold">io.net</span> - 
              Multi-bot architecture enabling 10x productivity through AI-powered automation
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <motion.a
                href="https://youtu.be/tGZxhFgC1m8"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 px-8 py-4 bg-red-600 hover:bg-red-700 rounded-lg transition-colors glow-effect"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Play className="w-5 h-5" />
                <span className="font-semibold">Watch Demo Video</span>
              </motion.a>
              
              <motion.a
                href="#setup"
                className="flex items-center space-x-2 px-8 py-4 glass-card hover:bg-white/20 rounded-lg transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Zap className="w-5 h-5" />
                <span className="font-semibold">Get Started</span>
                <ArrowRight className="w-4 h-4" />
              </motion.a>
            </div>

            {/* Hero Image/Video Placeholder */}
            <motion.div
              className="relative max-w-4xl mx-auto"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.3 }}
            >
              <div className="glass-card p-8 glow-effect">
                <img 
                  src="https://img.youtube.com/vi/tGZxhFgC1m8/0.jpg" 
                  alt="Demo Video Thumbnail"
                  className="w-full rounded-lg shadow-2xl"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-20 h-20 bg-red-600 rounded-full flex items-center justify-center hover:bg-red-700 transition-colors cursor-pointer">
                    <Play className="w-8 h-8 text-white ml-1" />
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Key Benefits */}
      <section id="overview" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Why io.net?
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Leverage the power of decentralized GPU networks for AI agent deployment with complete control over your data and infrastructure.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Data Privacy & Compliance"
              description="Self-hosted LLM models ensure complete data privacy and regulatory compliance"
              delay={0.1}
            />
            <FeatureCard
              icon={<Cpu className="w-8 h-8" />}
              title="Self-Hosting Power"
              description="Deploy on io.net's CaaS or Baremetal clusters with full control"
              delay={0.2}
            />
            <FeatureCard
              icon={<Network className="w-8 h-8" />}
              title="Flexible Deployment"
              description="Scale LLMs as needed using io.net's distributed infrastructure"
              delay={0.3}
            />
            <FeatureCard
              icon={<Sparkles className="w-8 h-8" />}
              title="Continuous Improvement"
              description="Gather data, annotate prompts, and fine-tune with TaaS"
              delay={0.4}
            />
          </div>
        </div>
      </section>

      {/* Architecture Overview */}
      <section id="architecture" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Multi-Bot Architecture
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Specialized agents working together in a distributed system for maximum efficiency and clear separation of concerns.
            </p>
          </motion.div>

          <div className="mermaid-container mb-12">
            <MermaidDiagram diagram={architectureDiagram} />
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="glass-card p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Bot className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold">Specialized Identity</h3>
              </div>
              <p className="text-gray-300">Each agent appears as distinct bot in Slack with unique personalities and capabilities.</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-xl font-semibold">Modular Design</h3>
              </div>
              <p className="text-gray-300">Independent deployment and scaling with self-contained logic per agent.</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-semibold">Better UX</h3>
              </div>
              <p className="text-gray-300">Users can directly mention specific agents with no command conflicts.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Agents Section */}
      <section id="agents" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Specialized AI Agents
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Five specialized bots, each with dedicated capabilities and identities, working together to provide comprehensive software engineering support.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {agents.map((agent, index) => (
              <AgentCard key={agent.name} agent={agent} delay={index * 0.1} />
            ))}
          </div>
        </div>
      </section>

      {/* Workflows Section */}
      <section id="workflows" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              End-to-End Workflows
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Comprehensive request lifecycle from Slack to agent response, powered by durable execution.
            </p>
          </motion.div>

          <div className="mermaid-container mb-12">
            <MermaidDiagram diagram={workflowDiagram} />
          </div>

          <WorkflowSection />
        </div>
      </section>

      {/* Setup Section */}
      <section id="setup" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Quick Start Guide
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Get your agent team up and running in minutes with our comprehensive setup guide.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-12">
            <div className="space-y-8">
              <div className="glass-card p-6">
                <h3 className="text-2xl font-bold mb-4 flex items-center">
                  <span className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
                  Multi-Bot System Setup
                </h3>
                <CodeBlock
                  language="bash"
                  code={`# Clone and install
git clone https://github.com/rajagurunath/software-engineering-agents
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your Slack tokens for each bot

# Run all specialized bots
python multi_bot_main.py`}
                />
              </div>

              <div className="glass-card p-6">
                <h3 className="text-2xl font-bold mb-4 flex items-center">
                  <span className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
                  Create Slack Applications
                </h3>
                <p className="text-gray-300 mb-4">
                  You'll need to create 5 separate Slack Apps and configure tokens for each agent:
                </p>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                    Architect Agent (@architect-bot)
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                    Developer Agent (@developer-bot)
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                    Data Analyst Agent (@data-analyst-bot)
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                    Sentry Agent (@sentry-bot)
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                    Main Dispatcher (@main-bot)
                  </li>
                </ul>
              </div>
            </div>

            <div className="space-y-8">
              <div className="glass-card p-6">
                <h3 className="text-2xl font-bold mb-4 flex items-center">
                  <span className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
                  Basic Usage Examples
                </h3>
                <CodeBlock
                  language="bash"
                  code={`# Research and analysis
ask architect How is the network performing?

# Code management  
review pr https://github.com/owner/repo/pull/123

# Data analysis
analyze data How many devices are online?

# Error debugging
handle sentry  # Use in Sentry alert threads

# Get help
help  # Shows all available commands`}
                />
              </div>

              <div className="glass-card p-6">
                <h3 className="text-2xl font-bold mb-4">Key Features</h3>
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Everyone leads a team of agents for 10x productivity</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Vibe code entire fixes and features from Slack</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Answer questions about codebase and architecture</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Create PRs, handle comments, and review code</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Every person becomes a product engineer</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <Bot className="w-8 h-8 text-primary-400" />
              <span className="text-xl font-bold gradient-text">Software Engineering Agents</span>
            </div>
            
            <div className="flex items-center space-x-6">
              <a 
                href="https://github.com/rajagurunath/software-engineering-agents" 
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
                <span>GitHub</span>
              </a>
              <a 
                href="https://www.youtube.com/playlist?list=PLZDaBdSBp7PePrYxVWvBIRYLRybAydPN_" 
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              >
                <Youtube className="w-5 h-5" />
                <span>Demo Playlist</span>
              </a>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-white/10 text-center text-gray-400">
            <p>&copy; 2024 Software Engineering Agents. Powered by io.net intelligence.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}