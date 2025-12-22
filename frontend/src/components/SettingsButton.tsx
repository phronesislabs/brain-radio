import './SettingsButton.css'

interface SettingsButtonProps {
  onClick: () => void
}

export function SettingsButton({ onClick }: SettingsButtonProps) {
  return (
    <button className="settings-button" onClick={onClick} title="Settings">
      ⚙️
    </button>
  )
}

