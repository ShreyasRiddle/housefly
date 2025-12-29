import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

export const neighborhoodsApi = {
  getAll: async (): Promise<Neighborhood[]> => {
    const response = await api.get('/api/neighborhoods')
    return response.data
  },
  getById: async (id: number): Promise<Neighborhood> => {
    const response = await api.get(`/api/neighborhoods/${id}`)
    return response.data
  },
  getScores: async (id: number): Promise<Score> => {
    const response = await api.get(`/api/neighborhoods/${id}/scores`)
    return response.data
  },
}

export const scoresApi = {
  getAll: async (): Promise<Score[]> => {
    const response = await api.get('/api/scores')
    return response.data
  },
  getProjection: async (neighborhoodId: number, years: 1 | 3 | 5): Promise<ScoreProjection> => {
    const response = await api.get(`/api/scores/${neighborhoodId}`, {
      params: { years },
    })
    return response.data
  },
  getBreakdown: async (neighborhoodId: number): Promise<ScoreBreakdown> => {
    const response = await api.get(`/api/scores/breakdown/${neighborhoodId}`)
    return response.data
  },
}

export default api

