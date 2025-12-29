import { useEffect, useState } from 'react'
import { ScoreBreakdown, ScoreProjection } from '../services/api'
import { scoresApi } from '../services/api'
import TimeSlider from './TimeSlider'
import ScoreBreakdownChart from './ScoreBreakdown'
import './NeighborhoodPopup.css'

interface NeighborhoodPopupProps {
  neighborhood: {
    id: number
    name: string
  }
  onClose: () => void
}

export default function NeighborhoodPopup({ neighborhood, onClose }: NeighborhoodPopupProps) {
  const [breakdown, setBreakdown] = useState<ScoreBreakdown | null>(null)
  const [projection, setProjection] = useState<ScoreProjection | null>(null)
  const [selectedYears, setSelectedYears] = useState<1 | 3 | 5>(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const [breakdownData, projectionData] = await Promise.all([
          scoresApi.getBreakdown(neighborhood.id),
          scoresApi.getProjection(neighborhood.id, selectedYears)
        ])
        setBreakdown(breakdownData)
        setProjection(projectionData)
        setLoading(false)
      } catch (error) {
        console.error('Error loading neighborhood data:', error)
        setLoading(false)
      }
    }
    
    loadData()
  }, [neighborhood.id, selectedYears])

  const currentScore = projection?.current_score || breakdown?.profitability_score || 0
  const projectedScore = selectedYears === 1 
    ? projection?.projection_1yr 
    : selectedYears === 3 
    ? projection?.projection_3yr 
    : projection?.projection_5yr || currentScore

  if (loading) {
    return (
      <div className="popup-overlay" onClick={onClose}>
        <div className="popup-content" onClick={(e) => e.stopPropagation()}>
          <div className="popup-loading">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-content" onClick={(e) => e.stopPropagation()}>
        <button className="popup-close" onClick={onClose}>×</button>
        
        <h2>{neighborhood.name}</h2>
        
        <div className="score-display">
          <div className="score-main">
            <div className="score-label">Profitability Score</div>
            <div className="score-value">{projectedScore.toFixed(1)}</div>
            <div className="score-scale">out of 100</div>
          </div>
          
          {projection && (
            <div className="trend-indicator">
              {projection.trend === 'up' && <span className="trend-up">↑</span>}
              {projection.trend === 'down' && <span className="trend-down">↓</span>}
              {projection.trend === 'stable' && <span className="trend-stable">→</span>}
            </div>
          )}
        </div>

        <TimeSlider
          selectedYears={selectedYears}
          onChange={setSelectedYears}
        />

        {breakdown && (
          <ScoreBreakdownChart breakdown={breakdown} />
        )}

        <div className="popup-footer">
          <small>Last updated: {breakdown?.calculated_at ? new Date(breakdown.calculated_at).toLocaleDateString() : 'N/A'}</small>
        </div>
      </div>
    </div>
  )
}

