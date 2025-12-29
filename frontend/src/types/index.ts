export interface Neighborhood {
  id: number
  name: string
  created_at: string
  scores?: Score
}

export interface Score {
  id: number
  neighborhood_id: number
  crime_score: number
  infrastructure_score: number
  demographic_score: number
  sentiment_score: number
  profitability_score: number
  calculated_at: string
}

export interface ScoreBreakdown {
  neighborhood_id: number
  neighborhood_name: string
  crime_score: number
  infrastructure_score: number
  demographic_score: number
  sentiment_score: number
  profitability_score: number
  calculated_at: string
}

export interface ScoreProjection {
  neighborhood_id: number
  neighborhood_name: string
  current_score: number
  projection_1yr: number
  projection_3yr: number
  projection_5yr: number
  trend: 'up' | 'down' | 'stable'
}

