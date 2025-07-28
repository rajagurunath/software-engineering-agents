'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface FeatureCardProps {
  icon: ReactNode
  title: string
  description: string
  delay?: number
}

export default function FeatureCard({ icon, title, description, delay = 0 }: FeatureCardProps) {
  return (
    <motion.div
      className="glass-card p-6 hover:bg-white/15 transition-all duration-300 group"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      viewport={{ once: true }}
      whileHover={{ y: -5 }}
    >
      <div className="flex items-center justify-center w-16 h-16 bg-primary-500/20 rounded-xl mb-4 group-hover:bg-primary-500/30 transition-colors">
        <div className="text-primary-400 group-hover:text-primary-300 transition-colors">
          {icon}
        </div>
      </div>
      
      <h3 className="text-xl font-semibold mb-3 text-white group-hover:text-primary-300 transition-colors">
        {title}
      </h3>
      
      <p className="text-gray-300 leading-relaxed">
        {description}
      </p>
    </motion.div>
  )
}