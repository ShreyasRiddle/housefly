import './TimeSlider.css'

interface TimeSliderProps {
  selectedYears: 1 | 3 | 5
  onChange: (years: 1 | 3 | 5) => void
}

export default function TimeSlider({ selectedYears, onChange }: TimeSliderProps) {
  const options: Array<{ years: 1 | 3 | 5; label: string }> = [
    { years: 1, label: '1 Year' },
    { years: 3, label: '3 Years' },
    { years: 5, label: '5 Years' }
  ]

  return (
    <div className="time-slider">
      <label className="time-slider-label">Projection Timeframe:</label>
      <div className="time-slider-buttons">
        {options.map(option => (
          <button
            key={option.years}
            className={`time-slider-button ${selectedYears === option.years ? 'active' : ''}`}
            onClick={() => onChange(option.years)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}

