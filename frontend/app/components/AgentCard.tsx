'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'
import { CheckCircle } from 'lucide-react'

interface Agent {
  name: string
  icon: ReactNode
  description: string
  capabilities: string[]
  color: string
}

interface AgentCardProps {
  agent: Agent
  delay?: number
}

export default function AgentCard({ agent, delay = 0 }: AgentCardProps) {
  return (
    <motion.div
      className="glass-card p-6 hover:bg-white/10 transition-all duration-300 group h-full"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      viewport={{ once: true }}
      whileHover={{ y: -5 }}
    >
      <div className="flex items-center space-x-4 mb-6">
        <div className={`w-16 h-16 bg-gradient-to-br ${agent.color} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform`}>
          <div className="text-white">
            {agent.icon}
          </div>
        </div>
        <div>
          <h3 className="text-xl font-bold text-white group-hover:text-primary-300 transition-colors">
            {agent.name}
          </h3>
        </div>
      </div>
      
      <p className="text-gray-300 mb-6 leading-relaxed">
        {agent.description}
      </p>
      
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-primary-400 uppercase tracking-wide">
          Key Capabilities
        </h4>
        <ul className="space-y-2">
          {agent.capabilities.map((capability, index) => (
            <li key={index} className="flex items-start text-sm text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
              <span>{capability}</span>
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  )
}