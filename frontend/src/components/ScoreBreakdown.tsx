import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { ScoreBreakdown as ScoreBreakdownType } from '../services/api'
import './ScoreBreakdown.css'

interface ScoreBreakdownProps {
  breakdown: ScoreBreakdownType
}

export default function ScoreBreakdownChart({ breakdown }: ScoreBreakdownProps) {
  const data = [
    {
      name: 'Crime',
      score: (breakdown.crime_score * 100).toFixed(1),
      value: breakdown.crime_score * 100
    },
    {
      name: 'Infrastructure',
      score: (breakdown.infrastructure_score * 100).toFixed(1),
      value: breakdown.infrastructure_score * 100
    },
    {
      name: 'Demographics',
      score: (breakdown.demographic_score * 100).toFixed(1),
      value: breakdown.demographic_score * 100
    },
    {
      name: 'Sentiment',
      score: (breakdown.sentiment_score * 100).toFixed(1),
      value: breakdown.sentiment_score * 100
    }
  ]

  const colors = {
    Crime: '#f44336',
    Infrastructure: '#2196f3',
    Demographics: '#4caf50',
    Sentiment: '#ff9800'
  }

  return (
    <div className="score-breakdown">
      <h3 className="score-breakdown-title">Score Breakdown</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip 
            formatter={(value: number) => [`${value.toFixed(1)}`, 'Score']}
            labelStyle={{ color: '#333' }}
          />
          <Bar dataKey="value" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Bar.Cell 
                key={`cell-${index}`} 
                fill={colors[entry.name as keyof typeof colors]} 
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      <div className="score-breakdown-legend">
        {data.map(item => (
          <div key={item.name} className="legend-item">
            <span 
              className="legend-color" 
              style={{ backgroundColor: colors[item.name as keyof typeof colors] }}
            />
            <span className="legend-label">{item.name}:</span>
            <span className="legend-value">{item.score}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

