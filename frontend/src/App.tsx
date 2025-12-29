import { useState } from 'react'
import Map from './components/Map'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Housefly: Buffalo Profitability Scoring</h1>
        <p>Click on any neighborhood to view its profitability score</p>
      </header>
      <Map />
    </div>
  )
}

export default App

