import { useState, useEffect, useRef } from 'react'
import type { PlaylistResult, TrackMetadata, Mode } from '../types'
import './SpotifyPlayer.css'

interface SpotifyPlayerProps {
  playlist: PlaylistResult
  isPremium: boolean
  mode: Mode
}

declare global {
  interface Window {
    Spotify: any
    onSpotifyWebPlaybackSDKReady: () => void
  }
}

export function SpotifyPlayer({ playlist, isPremium, mode }: SpotifyPlayerProps) {
  const [player, setPlayer] = useState<any>(null)
  const [isReady, setIsReady] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTrack, setCurrentTrack] = useState<TrackMetadata | null>(null)
  const [position, setPosition] = useState(0)
  const [deviceId, setDeviceId] = useState<string | null>(null)
  const playerRef = useRef<any>(null)

  useEffect(() => {
    if (!isPremium) {
      return
    }

    // Load Spotify Web Playback SDK
    const script = document.createElement('script')
    script.src = 'https://sdk.scdn.co/spotify-player.js'
    script.async = true
    document.body.appendChild(script)

    window.onSpotifyWebPlaybackSDKReady = () => {
      // SDK is ready, will initialize after getting token
      initializePlayer()
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.disconnect()
      }
    }
  }, [isPremium])

  const initializePlayer = async () => {
    try {
      const response = await fetch('/api/auth/token')
      const data = await response.json()
      const token = data.access_token

      const spotifyPlayer = new window.Spotify.Player({
        name: 'Brain-Radio Player',
        getOAuthToken: (cb: (token: string) => void) => {
          cb(token)
        },
        volume: 0.5,
      })

      spotifyPlayer.addListener('ready', ({ device_id }: { device_id: string }) => {
        setDeviceId(device_id)
        setIsReady(true)
      })

      spotifyPlayer.addListener('not_ready', ({ device_id }: { device_id: string }) => {
        setIsReady(false)
      })

      spotifyPlayer.addListener('player_state_changed', (state: any) => {
        if (!state) {
          return
        }

        setIsPlaying(!state.paused)
        setPosition(state.position)

        const track = state.track_window.current_track
        if (track) {
          setCurrentTrack({
            spotify_id: track.id,
            spotify_uri: track.uri,
            name: track.name,
            artist: track.artists[0]?.name || 'Unknown',
            album: track.album?.name,
            duration_ms: track.duration_ms,
            explicit: false,
            is_live: false,
            is_remaster: false,
            has_feat: false,
            source: 'spotify',
          })
        }
      })

      await spotifyPlayer.connect()
      setPlayer(spotifyPlayer)
      playerRef.current = spotifyPlayer
    } catch (error) {
      // Failed to initialize Spotify player - user will see error in UI
      setIsReady(false)
    }
  }

  const handlePlay = async () => {
    if (!player || !isReady || !deviceId) {
      return
    }

    try {
      if (playlist.tracks.length > 0) {
        const uris = playlist.tracks.map((track) => track.spotify_uri)
        await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${await getAccessToken()}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ uris }),
        })
        setIsPlaying(true)
      }
    } catch (error) {
      // Failed to play - error will be shown in UI
    }
  }

  const handlePause = async () => {
    if (!player || !isReady) {
      return
    }

    try {
      await player.pause()
      setIsPlaying(false)
    } catch (error) {
      // Failed to pause - error will be shown in UI
    }
  }

  const handleSkip = async () => {
    if (!player || !isReady) {
      return
    }

    try {
      await player.nextTrack()
    } catch (error) {
      // Failed to skip - error will be shown in UI
    }
  }

  const getAccessToken = async (): Promise<string> => {
    try {
      const response = await fetch('/api/auth/token', {
        credentials: 'include',
      })
      if (!response.ok) {
        throw new Error('Failed to get access token')
      }
      const data = await response.json()
      return data.access_token
    } catch (error) {
      // Error getting access token - will be handled by caller
      throw error
    }
  }

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="spotify-player">
      <div className="player-header">
        <h2 className="player-title">
          {mode.charAt(0).toUpperCase() + mode.slice(1)} Playlist
        </h2>
        <p className="player-info">
          {playlist.tracks.length} tracks • {formatTime(playlist.total_duration_ms)}
        </p>
      </div>

      {isPremium ? (
        <>
          {!isReady ? (
            <div className="player-loading">
              <div className="spinner"></div>
              <p>Initializing Spotify player...</p>
            </div>
          ) : (
            <>
              <div className="player-controls">
                <button
                  className="control-button skip-button"
                  onClick={handleSkip}
                  disabled={!isReady}
                  title="Skip Next"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    width="24"
                    height="24"
                  >
                    <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
                  </svg>
                </button>
                <button
                  className="control-button play-pause-button"
                  onClick={isPlaying ? handlePause : handlePlay}
                  disabled={!isReady}
                  title={isPlaying ? 'Pause' : 'Play'}
                >
                  {isPlaying ? (
                    <svg
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      width="32"
                      height="32"
                    >
                      <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                    </svg>
                  ) : (
                    <svg
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      width="32"
                      height="32"
                    >
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  )}
                </button>
                <button
                  className="control-button skip-button"
                  onClick={handleSkip}
                  disabled={!isReady}
                  title="Skip Next"
                  style={{ transform: 'scaleX(-1)' }}
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    width="24"
                    height="24"
                  >
                    <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
                  </svg>
                </button>
              </div>

              {currentTrack && (
                <div className="current-track">
                  <div className="track-info">
                    <h3 className="track-name">{currentTrack.name}</h3>
                    <p className="track-artist">{currentTrack.artist}</p>
                    {currentTrack.album && (
                      <p className="track-album">{currentTrack.album}</p>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      ) : (
        <div className="premium-required">
          <p>Spotify Premium is required for in-browser playback.</p>
          <p className="premium-note">
            Your playlist has been generated with {playlist.tracks.length} tracks.
            You can find it in your Spotify account.
          </p>
        </div>
      )}

      <div className="playlist-tracks">
        <h3 className="tracks-title">Playlist Tracks</h3>
        <div className="tracks-list">
          {playlist.tracks.map((track, index) => (
            <div
              key={track.spotify_id}
              className={`track-item ${currentTrack?.spotify_id === track.spotify_id ? 'current' : ''}`}
            >
              <span className="track-number">{index + 1}</span>
              <div className="track-details">
                <span className="track-name-text">{track.name}</span>
                <span className="track-artist-text">{track.artist}</span>
              </div>
              {track.bpm && (
                <span className="track-bpm">{Math.round(track.bpm)} BPM</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

