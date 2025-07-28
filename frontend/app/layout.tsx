import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Software Engineering Agents - Decentralized AI for Startups & Enterprises',
  description: 'Decentralised Software Agents for Startups and Enterprises powered by io.net. Multi-bot architecture for deep research, code reviews, data analysis, and production monitoring.',
  keywords: 'AI agents, software engineering, automation, io.net, decentralized, multi-bot, code review, data analysis',
  authors: [{ name: 'Software Engineering Agents Team' }],
  openGraph: {
    title: 'Software Engineering Agents',
    description: 'Decentralised Software Agents for Startups and Enterprises',
    type: 'website',
    images: ['/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Software Engineering Agents',
    description: 'Decentralised Software Agents for Startups and Enterprises',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}