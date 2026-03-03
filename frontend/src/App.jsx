import React, { useState } from 'react'
import SearchBar from './components/SearchBar'
import TranscriptInput from './components/TranscriptInput'
import PriceChart from './components/PriceChart'
import ComparisonChart from './components/ComparisonChart'
import MetricsTable from './components/MetricsTable'
import LLMSynthesis from './components/LLMSynthesis'
import { analyzeStock, processTranscript } from './services/api'

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState(null)
  const [currentTicker, setCurrentTicker] = useState('')
  const [userTranscript, setUserTranscript] = useState(null)
  const [transcriptSynthesis, setTranscriptSynthesis] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processError, setProcessError] = useState('')

  const handleAnalyze = async (ticker) => {
    setIsLoading(true)
    setError('')
    setCurrentTicker(ticker)

    try {
      // Clear any cached data by reloading the component state
      setResults(null)

      // Add a small delay to ensure state is cleared before fetching
      await new Promise(resolve => setTimeout(resolve, 100))

      const data = await analyzeStock(ticker)
      setResults(data)
    } catch (err) {
      setError(err.message || 'Failed to analyze stock. Please try again.')
      setResults(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleTranscriptLoaded = (transcript) => {
    setUserTranscript(transcript)
    setTranscriptSynthesis(null)
    setProcessError('')
  }

  const handleProcess = async () => {
    if (!userTranscript) return

    setIsProcessing(true)
    setProcessError('')

    try {
      const data = await processTranscript(userTranscript)
      if (data.success) {
        setTranscriptSynthesis(data.synthesis)
      }
    } catch (err) {
      setProcessError(err.message || 'Failed to analyze transcript. Please try again.')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <SearchBar onAnalyze={handleAnalyze} isLoading={isLoading} />

      {/* Stock analysis error */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        </div>
      )}

      {results && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <PriceChart
              data={results.price_chart_data}
              ticker={currentTicker}
              isLoading={isLoading}
            />
            <ComparisonChart
              data={results.comparison_chart_data}
              ticker={currentTicker}
              isLoading={isLoading}
            />
          </div>

          {/* Metrics */}
          <MetricsTable
            metrics={results.metrics}
            ticker={currentTicker}
            isLoading={isLoading}
          />

          {/* LLM Synthesis from Analyze */}
          <LLMSynthesis
            synthesis={results.llm_synthesis}
            ticker={currentTicker}
            isLoading={isLoading}
          />
        </div>
      )}

      {/* Transcript section — always visible, independent of stock analysis */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {!results && !error && !isLoading && (
          <div className="text-center text-gray-600 mb-8">
            <p className="text-lg mb-4">Enter a stock ticker to begin analysis</p>
            <p className="text-sm text-gray-500">
              Get comprehensive financial analysis including 5-year price history,
              performance comparison with S&P 500, and AI-powered earnings call insights.
            </p>
          </div>
        )}

        <TranscriptInput
          onTranscriptLoaded={handleTranscriptLoaded}
          isDisabled={isLoading}
          onProcess={handleProcess}
          isProcessing={isProcessing}
          hasTranscript={!!userTranscript}
        />

        {/* Transcript processing error */}
        {processError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {processError}
          </div>
        )}

        {/* LLM Synthesis from Analyze Transcript */}
        {transcriptSynthesis && (
          <LLMSynthesis
            synthesis={transcriptSynthesis}
            title="Transcript Analysis"
            subtitle="Independent AI-powered analysis of the uploaded transcript"
          />
        )}
      </div>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-600">
          <p>Deterministic Strategic Analysis Engine (DSAE) • Data powered by Financial Modeling Prep • Analysis by Google Gemini</p>
        </div>
      </footer>
    </div>
  )
}

export default App
