import React, { useState } from 'react'
import SearchBar from './components/SearchBar'
import TranscriptInput from './components/TranscriptInput'
import PriceChart from './components/PriceChart'
import ComparisonChart from './components/ComparisonChart'
import MetricsTable from './components/MetricsTable'
import HoldingsTable from './components/HoldingsTable'
import LLMSynthesis from './components/LLMSynthesis'
import { analyzeStock, analyzeETF, processTranscript } from './services/api'

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState(null)
  const [etfResults, setEtfResults] = useState(null)
  const [currentTicker, setCurrentTicker] = useState('')
  const [analysisMode, setAnalysisMode] = useState('stock')
  const [userTranscript, setUserTranscript] = useState(null)
  const [transcriptSynthesis, setTranscriptSynthesis] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processError, setProcessError] = useState('')

  const handleModeChange = (mode) => {
    setAnalysisMode(mode)
    setResults(null)
    setEtfResults(null)
    setError('')
  }

  const handleAnalyze = async (ticker) => {
    setIsLoading(true)
    setError('')
    setCurrentTicker(ticker)
    setResults(null)
    setEtfResults(null)

    try {
      await new Promise(resolve => setTimeout(resolve, 100))

      if (analysisMode === 'etf') {
        const data = await analyzeETF(ticker)
        setEtfResults(data)
      } else {
        const data = await analyzeStock(ticker)
        setResults(data)
      }
    } catch (err) {
      setError(err.message || `Failed to analyze ${analysisMode === 'etf' ? 'ETF' : 'stock'}. Please try again.`)
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
      <SearchBar
        onAnalyze={handleAnalyze}
        isLoading={isLoading}
        analysisMode={analysisMode}
        onModeChange={handleModeChange}
      />

      {/* Analysis error */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        </div>
      )}

      {/* Stock results */}
      {results && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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

          <MetricsTable
            metrics={results.metrics}
            ticker={currentTicker}
            isLoading={isLoading}
          />

          <LLMSynthesis
            synthesis={results.llm_synthesis}
            ticker={currentTicker}
            isLoading={isLoading}
          />
        </div>
      )}

      {/* ETF results */}
      {etfResults && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <PriceChart
              data={etfResults.price_chart_data}
              ticker={currentTicker}
              isLoading={isLoading}
            />
            <ComparisonChart
              data={etfResults.comparison_chart_data}
              ticker={currentTicker}
              isLoading={isLoading}
            />
          </div>

          <HoldingsTable
            holdings={etfResults.holdings}
            ticker={currentTicker}
          />

          {etfResults.summary && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                AI Insight — {etfResults.name || currentTicker}
              </h2>
              <p className="text-gray-700 leading-relaxed">{etfResults.summary}</p>
              <div className="mt-4 text-xs text-gray-400">
                Powered by Google Gemini AI
              </div>
            </div>
          )}
        </div>
      )}

      {/* Transcript section — only in stock mode */}
      {analysisMode !== 'etf' && (
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

          {processError && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {processError}
            </div>
          )}

          {transcriptSynthesis && (
            <LLMSynthesis
              synthesis={transcriptSynthesis}
              title="Transcript Analysis"
              subtitle="Independent AI-powered analysis of the uploaded transcript"
            />
          )}
        </div>
      )}

      {/* Empty state for ETF mode */}
      {analysisMode === 'etf' && !etfResults && !error && !isLoading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p className="text-lg mb-4">Enter an ETF ticker to begin analysis</p>
            <p className="text-sm text-gray-500">
              Get 5-year price history, S&P 500 comparison, top holdings, and AI-powered insights.
            </p>
          </div>
        </div>
      )}

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-600">
          <p>VibeFinQuant • Data powered by Yahoo Finance • Analysis by Google Gemini</p>
        </div>
      </footer>
    </div>
  )
}

export default App
