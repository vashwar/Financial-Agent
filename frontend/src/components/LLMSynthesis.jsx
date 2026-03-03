import React, { useState } from 'react'

const Section = ({ title, content, isOpen, onToggle }) => (
  <div className="border border-gray-200 rounded-lg mb-4">
    <button
      onClick={onToggle}
      className="w-full flex justify-between items-center px-6 py-4 hover:bg-gray-50 transition-colors"
    >
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      <span className="text-gray-500 text-xl">
        {isOpen ? '−' : '+'}
      </span>
    </button>
    {isOpen && (
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <p className="text-gray-700 leading-relaxed">{content}</p>
      </div>
    )}
  </div>
)

export default function LLMSynthesis({ synthesis, ticker, isLoading, title, subtitle }) {
  const [openSections, setOpenSections] = useState({
    quarterly_performance: true,
    forward_guidance: false,
    challenges: false,
    positive_signs: false,
    analyst_qa_focus: false,
    strategic_initiatives: false,
    management_tone: false,
    conclusion: true,
  })

  const toggleSection = (key) => {
    setOpenSections(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">Loading synthesis...</div>
      </div>
    )
  }

  if (!synthesis) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">No synthesis available</div>
      </div>
    )
  }

  const sections = [
    { key: 'quarterly_performance', title: '1. Quarterly Performance', content: synthesis.quarterly_performance },
    { key: 'forward_guidance', title: '2. Forward Guidance', content: synthesis.forward_guidance },
    { key: 'challenges', title: '3. Challenges', content: synthesis.challenges },
    { key: 'positive_signs', title: '4. Positive Signs', content: synthesis.positive_signs },
    { key: 'analyst_qa_focus', title: '5. Analyst Q&A Focus', content: synthesis.analyst_qa_focus },
    { key: 'strategic_initiatives', title: '6. Strategic Initiatives & Capital Allocation', content: synthesis.strategic_initiatives },
    { key: 'management_tone', title: '7. Management Tone', content: synthesis.management_tone },
    { key: 'conclusion', title: '8. Conclusion', content: synthesis.conclusion },
  ]

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-2">
        {title || `${ticker} - Earnings Call Strategic Synthesis`}
      </h2>
      <p className="text-gray-600 text-sm mb-6">
        {subtitle || 'AI-powered analysis of the latest earnings call transcript'}
      </p>

      <div className="space-y-2">
        {sections.map((section) => (
          <Section
            key={section.key}
            title={section.title}
            content={section.content}
            isOpen={openSections[section.key]}
            onToggle={() => toggleSection(section.key)}
          />
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
        Analysis powered by Google Gemini AI. Please verify key insights with primary sources.
      </div>
    </div>
  )
}
