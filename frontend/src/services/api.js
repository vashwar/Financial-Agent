import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:9001'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Ensure response headers include no-cache directives
    response.headers['cache-control'] = 'no-cache, no-store, must-revalidate'
    return response.data
  },
  (error) => {
    if (error.response?.status === 404) {
      return Promise.reject(new Error('Invalid ticker symbol'))
    }
    if (error.response?.status === 400) {
      return Promise.reject(new Error(error.response.data?.detail || 'Invalid request'))
    }
    if (error.response?.status === 500) {
      return Promise.reject(new Error('Server error: ' + (error.response.data?.detail || 'Unknown error')))
    }
    return Promise.reject(new Error(error.message || 'API request failed'))
  }
)

/**
 * Analyze a stock ticker
 * @param {string} ticker - Stock ticker symbol (e.g., 'AAPL')
 * @param {string} [transcript] - Optional user-provided transcript
 * @returns {Promise} Response with analysis data
 */
export const analyzeStock = (ticker, transcript = null) => {
  return apiClient.post('/api/analyze', {
    ticker: ticker.toUpperCase(),
    ...(transcript && { transcript }),
  }, {
    // Add cache-busting timestamp and headers
    params: {
      _t: Date.now(), // Cache-busting parameter
    },
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  })
}

/**
 * Process a transcript independently via Gemini AI
 * @param {string} transcript - Transcript text to analyze
 * @returns {Promise} Response with AI synthesis
 */
export const processTranscript = (transcript) => {
  return apiClient.post('/api/process-transcript', { transcript }, {
    timeout: 120000, // 2 minutes — LLM calls can be slow
  })
}

/**
 * Search for tickers by company name or symbol
 * @param {string} query - Search query (e.g., 'Apple' or 'AAPL')
 * @returns {Promise} Response with matching suggestions
 */
export const searchTickers = (query) => {
  return apiClient.get('/api/search', {
    params: { q: query },
    timeout: 5000,
  })
}

/**
 * Analyze an ETF ticker
 * @param {string} ticker - ETF ticker symbol (e.g., 'SPY')
 * @returns {Promise} Response with ETF analysis data
 */
export const analyzeETF = (ticker) => {
  return apiClient.post('/api/analyze-etf', {
    ticker: ticker.toUpperCase(),
  }, {
    params: { _t: Date.now() },
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  })
}

/**
 * Check API health
 * @returns {Promise} Health status
 */
export const checkHealth = () => {
  return apiClient.get('/health')
}

export default apiClient
