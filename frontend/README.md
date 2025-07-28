# Software Engineering Agents Frontend

A modern, interactive landing page for the Software Engineering Agents project built with Next.js, React, Tailwind CSS, and Framer Motion.

## Features

- 🎨 Modern, responsive design with glassmorphism effects
- 🚀 Built with Next.js 14 and React 18
- 💫 Smooth animations with Framer Motion
- 📊 Interactive Mermaid diagrams for workflows
- 🎯 Optimized for Vercel deployment
- 📱 Mobile-first responsive design
- 🌙 Dark theme with gradient accents

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Diagrams**: Mermaid
- **Icons**: Lucide React
- **Code Highlighting**: React Syntax Highlighter
- **Deployment**: Vercel

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

This project is optimized for Vercel deployment:

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically

## Project Structure

```
frontend/
├── app/
│   ├── components/     # Reusable React components
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Main page
├── public/             # Static assets
└── package.json        # Dependencies
```

## Components

- **MermaidDiagram**: Interactive workflow diagrams
- **CodeBlock**: Syntax-highlighted code blocks with copy functionality
- **FeatureCard**: Animated feature showcase cards
- **AgentCard**: Specialized agent information cards
- **WorkflowSection**: Expandable workflow documentation

## Customization

The design system is built with Tailwind CSS custom utilities:

- `gradient-text`: Gradient text effects
- `glass-card`: Glassmorphism card styling
- `glow-effect`: Subtle glow effects
- Custom color palette with primary and dark variants

## Performance

- Optimized images and assets
- Code splitting with Next.js
- Lazy loading for components
- Minimal bundle size