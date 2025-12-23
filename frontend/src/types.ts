export type Mode = 'focus' | 'relax' | 'sleep' | 'meditation'

export interface TrackMetadata {
  spotify_id: string
  spotify_uri: string
  name: string
  artist: string
  album?: string
  duration_ms?: number
  bpm?: number
  key?: string
  is_instrumental?: boolean
  energy?: number
  speechiness?: number
  instrumentalness?: number
  explicit: boolean
  is_live: boolean
  is_remaster: boolean
  has_feat: boolean
  source: string
}

export interface PlaylistResult {
  mode: Mode
  tracks: TrackMetadata[]
  total_duration_ms: number
  verification_summary: Record<string, number>
}

export interface AuthStatus {
  authenticated: boolean
  is_premium?: boolean
  user_id?: string
}

export interface PlaylistRequest {
  mode: Mode
  genre?: string | null
  duration_minutes?: number
}

