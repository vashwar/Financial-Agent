import React, { useState } from 'react'
import apiClient from '../services/api'

export default function TranscriptInput({ onTranscriptLoaded, isDisabled, onProcess, isProcessing, hasTranscript }) {
  const [activeTab, setActiveTab] = useState('file') // 'file' or 'youtube'
  const [fileName, setFileName] = useState('')
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post('/api/transcript/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.success) {
        setSuccess(`Transcript loaded successfully (${response.length} characters)`)
        setFileName(file.name)
        onTranscriptLoaded(response.transcript)
      } else {
        setError(response.message)
      }
    } catch (err) {
      setError(err.message || 'Failed to upload transcript')
    } finally {
      setIsLoading(false)
    }
  }

  const handleYoutubeSubmit = async (e) => {
    e.preventDefault()
    if (!youtubeUrl.trim()) {
      setError('Please enter a YouTube URL')
      return
    }

    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      const response = await apiClient.post('/api/transcript/youtube', {
        youtube_url: youtubeUrl,
      })

      if (response.success) {
        setSuccess(`Transcript extracted successfully (${response.length} characters)`)
        setYoutubeUrl('')
        onTranscriptLoaded(response.transcript)
      } else {
        setError(response.message)
      }
    } catch (err) {
      setError(err.message || 'Failed to extract YouTube transcript')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Earnings Transcript</h2>

      <div className="flex gap-2 mb-4 border-b border-gray-200">
        <button
          onClick={() => {
            setActiveTab('file')
            setError('')
            setSuccess('')
          }}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'file'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
          disabled={isDisabled || isLoading}
        >
          Upload File
        </button>
        <button
          onClick={() => {
            setActiveTab('youtube')
            setError('')
            setSuccess('')
          }}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'youtube'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
          disabled={isDisabled || isLoading}
        >
          YouTube Link
        </button>
      </div>

      {activeTab === 'file' && (
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".txt,.text"
              onChange={handleFileUpload}
              disabled={isDisabled || isLoading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          {fileName && (
            <p className="text-sm text-gray-600">Selected: {fileName}</p>
          )}
        </div>
      )}

      {activeTab === 'youtube' && (
        <form onSubmit={handleYoutubeSubmit} className="space-y-4">
          <input
            type="url"
            value={youtubeUrl}
            onChange={(e) => {
              setYoutubeUrl(e.target.value)
              setError('')
            }}
            placeholder="Paste YouTube video URL (e.g., https://www.youtube.com/watch?v=...)"
            disabled={isDisabled || isLoading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isDisabled || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Extracting...' : 'Extract Transcript'}
          </button>
        </form>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
          ✓ {success}
        </div>
      )}

      {hasTranscript && onProcess && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={onProcess}
            disabled={isProcessing || isDisabled}
            className="px-6 py-2.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isProcessing ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing Transcript...
              </>
            ) : (
              'Analyze Transcript'
            )}
          </button>
          <p className="mt-1 text-xs text-gray-500">
            Analyze this transcript with Gemini AI (independent of stock Analyze button above)
          </p>
        </div>
      )}
    </div>
  )
}
