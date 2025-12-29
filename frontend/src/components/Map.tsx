import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import { neighborhoodsApi, scoresApi, Neighborhood, Score } from '../services/api'
import NeighborhoodPopup from './NeighborhoodPopup'
import './Map.css'

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface MapProps {}

function MapContent({ neighborhoods, scores }: { neighborhoods: Neighborhood[], scores: Score[] }) {
  const map = useMap()
  
  useEffect(() => {
    if (neighborhoods.length > 0) {
      // Fit map to Buffalo bounds
      const bounds = L.latLngBounds([
        [42.8, -79.0],
        [42.95, -78.7]
      ])
      map.fitBounds(bounds)
    }
  }, [neighborhoods, map])
  
  return null
}

export default function Map() {
  const [neighborhoods, setNeighborhoods] = useState<Neighborhood[]>([])
  const [scores, setScores] = useState<Record<number, Score>>({})
  const [selectedNeighborhood, setSelectedNeighborhood] = useState<Neighborhood | null>(null)
  const [loading, setLoading] = useState(true)
  const [geojsonData, setGeojsonData] = useState<any>(null)

  useEffect(() => {
    async function loadData() {
      try {
        const [neighborhoodsData, scoresData] = await Promise.all([
          neighborhoodsApi.getAll(),
          scoresApi.getAll()
        ])
        
        setNeighborhoods(neighborhoodsData)
        
        const scoresMap: Record<number, Score> = {}
        scoresData.forEach(score => {
          scoresMap[score.neighborhood_id] = score
        })
        setScores(scoresMap)
        
        // Load GeoJSON data
        // In production, this would come from the API
        // For now, we'll create a placeholder structure
        setGeojsonData({
          type: 'FeatureCollection',
          features: neighborhoodsData.map(nh => ({
            type: 'Feature',
            properties: {
              id: nh.id,
              name: nh.name,
              score: scoresMap[nh.id]?.profitability_score || 0
            },
            geometry: {
              type: 'Polygon',
              coordinates: [] // Will be populated from API
            }
          }))
        })
        
        setLoading(false)
      } catch (error) {
        console.error('Error loading data:', error)
        setLoading(false)
      }
    }
    
    loadData()
  }, [])

  const getColorForScore = (score: number): string => {
    // Color scale from red (0) to green (100)
    if (score >= 80) return '#00C853' // Green
    if (score >= 60) return '#64DD17' // Light green
    if (score >= 40) return '#FFD600' // Yellow
    if (score >= 20) return '#FF6D00' // Orange
    return '#D32F2F' // Red
  }

  const onEachFeature = (feature: any, layer: L.Layer) => {
    const neighborhoodId = feature.properties.id
    const neighborhood = neighborhoods.find(n => n.id === neighborhoodId)
    const score = scores[neighborhoodId]
    
    if (neighborhood) {
      layer.on({
        click: () => {
          setSelectedNeighborhood(neighborhood)
        },
        mouseover: (e: L.LeafletMouseEvent) => {
          const layer = e.target
          layer.setStyle({
            weight: 3,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.7
          })
        },
        mouseout: (e: L.LeafletMouseEvent) => {
          const layer = e.target
          const score = scores[neighborhoodId]?.profitability_score || 0
          layer.setStyle({
            weight: 2,
            color: getColorForScore(score),
            dashArray: '',
            fillOpacity: 0.5
          })
        }
      })
    }
  }

  const style = (feature: any) => {
    const score = feature.properties.score || 0
    return {
      fillColor: getColorForScore(score),
      weight: 2,
      opacity: 1,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0.5
    }
  }

  if (loading) {
    return (
      <div className="map-loading">
        <p>Loading map data...</p>
      </div>
    )
  }

  return (
    <div className="map-container">
      <MapContainer
        center={[42.8864, -78.8784]}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapContent neighborhoods={neighborhoods} scores={Object.values(scores)} />
        
        {geojsonData && (
          <GeoJSON
            data={geojsonData}
            style={style}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
      
      {selectedNeighborhood && (
        <NeighborhoodPopup
          neighborhood={selectedNeighborhood}
          onClose={() => setSelectedNeighborhood(null)}
        />
      )}
    </div>
  )
}
