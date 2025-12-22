import { useState } from 'react'
import { api } from '../services/api'
import './OpenAIKeyModal.css'

interface OpenAIKeyModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export function OpenAIKeyModal({ isOpen, onClose, onSuccess }: OpenAIKeyModalProps) {
  const [apiKey, setApiKey] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await api.post('/config/openai', { api_key: apiKey })
      setApiKey('')
      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save API key')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ×
        </button>
        <h2 className="modal-title">OpenAI API Key</h2>
        <p className="modal-description">
          Brain-Radio uses OpenAI to generate playlists. Please provide your OpenAI API key.
          Your key is stored securely in your session and never shared.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="api-key">OpenAI API Key</label>
            <input
              id="api-key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              required
              disabled={isLoading}
            />
            <p className="form-help">
              Get your API key from{' '}
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
              >
                platform.openai.com
              </a>
            </p>
          </div>
          {error && <div className="error-message">{error}</div>}
          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" disabled={isLoading || !apiKey}>
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

