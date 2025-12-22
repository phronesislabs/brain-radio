import { useState } from 'react'
import type { Mode } from '../types'
import './ModeSelector.css'

interface ModeSelectorProps {
  onModeSelect: (mode: Mode, genre?: string, duration?: number) => void
  isGenerating: boolean
  selectedMode: Mode | null
}

const modes: Array<{
  id: Mode
  label: string
  description: string
  color: string
  icon: string
}> = [
  {
    id: 'focus',
    label: 'Focus',
    description: '120-140 BPM, no vocals, steady rhythm',
    color: 'var(--focus-color)',
    icon: '🎯',
  },
  {
    id: 'relax',
    label: 'Relax',
    description: '60-90 BPM, major keys, acoustic textures',
    color: 'var(--relax-color)',
    icon: '🌊',
  },
  {
    id: 'sleep',
    label: 'Sleep',
    description: '<60 BPM, ambient/drone, no sudden transients',
    color: 'var(--sleep-color)',
    icon: '🌙',
  },
  {
    id: 'meditation',
    label: 'Meditation',
    description: 'Low energy, slow tempo, repetitive elements',
    color: 'var(--meditation-color)',
    icon: '🧘',
  },
]

export function ModeSelector({ onModeSelect, isGenerating, selectedMode }: ModeSelectorProps) {
  const [genre, setGenre] = useState('')
  const [duration, setDuration] = useState(60)

  const handleModeClick = (mode: Mode) => {
    onModeSelect(mode, genre || undefined, duration)
  }

  return (
    <div className="mode-selector">
      <h2 className="mode-selector-title">Select Your Mode</h2>
      
      <div className="mode-options">
        {modes.map((mode) => (
          <button
            key={mode.id}
            className={`mode-card ${selectedMode === mode.id ? 'selected' : ''}`}
            onClick={() => handleModeClick(mode.id)}
            disabled={isGenerating}
            style={{
              '--mode-color': mode.color,
            } as React.CSSProperties}
          >
            <span className="mode-icon">{mode.icon}</span>
            <h3 className="mode-label">{mode.label}</h3>
            <p className="mode-description">{mode.description}</p>
          </button>
        ))}
      </div>

      <div className="mode-options-form">
        <div className="form-group">
          <label htmlFor="genre">Genre Preference (optional)</label>
          <input
            id="genre"
            type="text"
            placeholder="e.g., Techno, Jazz, Ambient"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            disabled={isGenerating}
          />
        </div>

        <div className="form-group">
          <label htmlFor="duration">Duration (minutes)</label>
          <input
            id="duration"
            type="number"
            min="15"
            max="240"
            step="15"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value) || 60)}
            disabled={isGenerating}
          />
        </div>
      </div>

      {isGenerating && (
        <div className="generating-indicator">
          <div className="spinner"></div>
          <p>Generating your playlist...</p>
        </div>
      )}
    </div>
  )
}

