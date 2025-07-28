'use client'

import { useEffect, useRef } from 'react'
import mermaid from 'mermaid'

interface MermaidDiagramProps {
  diagram: string
  id?: string
}

export default function MermaidDiagram({ diagram, id }: MermaidDiagramProps) {
  const elementRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (elementRef.current) {
      mermaid.initialize({
        startOnLoad: true,
        theme: 'dark',
        themeVariables: {
          primaryColor: '#3b82f6',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#1e40af',
          lineColor: '#6b7280',
          sectionBkgColor: '#1f2937',
          altSectionBkgColor: '#374151',
          gridColor: '#4b5563',
          secondaryColor: '#7c3aed',
          tertiaryColor: '#ec4899',
          background: 'transparent',
          mainBkg: '#1f2937',
          secondBkg: '#374151',
          tertiaryBkg: '#4b5563',
        },
      })

      const renderDiagram = async () => {
        try {
          const { svg } = await mermaid.render(
            id || `mermaid-${Math.random().toString(36).substr(2, 9)}`,
            diagram
          )
          if (elementRef.current) {
            elementRef.current.innerHTML = svg
          }
        } catch (error) {
          console.error('Error rendering Mermaid diagram:', error)
          if (elementRef.current) {
            elementRef.current.innerHTML = '<p class="text-red-400">Error rendering diagram</p>'
          }
        }
      }

      renderDiagram()
    }
  }, [diagram, id])

  return (
    <div 
      ref={elementRef} 
      className="w-full overflow-x-auto"
      style={{ minHeight: '200px' }}
    />
  )
}