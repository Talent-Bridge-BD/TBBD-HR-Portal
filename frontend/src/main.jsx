import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'
import './index.css'
import { initializeMsal } from './utils/auth'

async function startApp() {
  try {
    await initializeMsal()
  } catch (error) {
    console.error(
      'Failed to initialize Microsoft Entra authentication:',
      error,
    )
  }

  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
}

startApp()
