import { useState, useEffect } from 'react'
import { SpotifyPlayer } from './components/SpotifyPlayer'
import { ModeSelector } from './components/ModeSelector'
import { LoginButton } from './components/LoginButton'
import { OpenAIKeyModal } from './components/OpenAIKeyModal'
import { SettingsButton } from './components/SettingsButton'
import { api } from './services/api'
import type { Mode, TrackMetadata, PlaylistResult } from './types'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isPremium, setIsPremium] = useState(false)
  const [selectedMode, setSelectedMode] = useState<Mode | null>(null)
  const [playlist, setPlaylist] = useState<PlaylistResult | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasOpenAIKey, setHasOpenAIKey] = useState(false)
  const [showOpenAIModal, setShowOpenAIModal] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      checkOpenAIKey()
    }
  }, [isAuthenticated])

  const checkAuth = async () => {
    try {
      const response = await api.get('/auth/status')
      setIsAuthenticated(response.data.authenticated)
      setIsPremium(response.data.is_premium || false)
      setHasOpenAIKey(response.data.has_openai_key || false)
    } catch (err) {
      setIsAuthenticated(false)
    }
  }

  const checkOpenAIKey = async () => {
    try {
      const response = await api.get('/config/openai/status')
      setHasOpenAIKey(response.data.configured || false)
      if (!response.data.configured) {
        setShowOpenAIModal(true)
      }
    } catch (err) {
      // If endpoint fails, assume not configured
      setHasOpenAIKey(false)
    }
  }

  const handleLogin = () => {
    window.location.href = '/api/auth/login'
  }

  const handleModeSelect = async (mode: Mode, genre?: string, duration?: number) => {
    if (!isAuthenticated) {
      setError('Please log in with Spotify first')
      return
    }

    if (!hasOpenAIKey) {
      setShowOpenAIModal(true)
      setError('OpenAI API key is required to generate playlists')
      return
    }

    setSelectedMode(mode)
    setIsGenerating(true)
    setError(null)
    setPlaylist(null)

    try {
      const response = await api.post('/playlist/generate', {
        mode,
        genre: genre || null,
        duration_minutes: duration || 60,
      })
      setPlaylist(response.data)
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || 'Failed to generate playlist'
      setError(errorDetail)
      if (errorDetail.includes('OpenAI API key')) {
        setShowOpenAIModal(true)
        setHasOpenAIKey(false)
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleOpenAISuccess = () => {
    setHasOpenAIKey(true)
    setError(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        {isAuthenticated && (
          <SettingsButton onClick={() => setShowOpenAIModal(true)} />
        )}
        <h1 className="app-title">Brain-Radio</h1>
        <p className="app-subtitle">Functional Music for Focus, Relax, Sleep & Meditation</p>
      </header>

      <main className="app-main">
        {!isAuthenticated ? (
          <div className="login-container">
            <LoginButton onLogin={handleLogin} />
            <p className="login-description">
              Connect with Spotify to generate scientifically-tuned playlists
              based on your music taste
            </p>
          </div>
        ) : (
          <>
            <ModeSelector
              onModeSelect={handleModeSelect}
              isGenerating={isGenerating}
              selectedMode={selectedMode}
            />

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {!isPremium && (
              <div className="premium-warning">
                <p>
                  ⚠️ Spotify Premium is required for in-browser playback.
                  Playlists can still be generated and saved to your Spotify account.
                </p>
              </div>
            )}

            {!hasOpenAIKey && (
              <div className="openai-warning">
                <p>
                  ⚠️ OpenAI API key is required to generate playlists.
                  <button
                    className="link-button"
                    onClick={() => setShowOpenAIModal(true)}
                  >
                    Configure API key
                  </button>
                </p>
              </div>
            )}

            {playlist && (
              <SpotifyPlayer
                playlist={playlist}
                isPremium={isPremium}
                mode={selectedMode!}
              />
            )}

            <OpenAIKeyModal
              isOpen={showOpenAIModal}
              onClose={() => setShowOpenAIModal(false)}
              onSuccess={handleOpenAISuccess}
            />
          </>
        )}
      </main>
    </div>
  )
}

export default App

