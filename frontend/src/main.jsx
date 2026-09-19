import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'
import './index.css'

if (import.meta.env.DEV) {
  const originalFetch = window.fetch.bind(window)

  window.fetch = (input, init = {}) => {
    const portal = window.localStorage.getItem('tbbd_local_portal')

    if (portal === 'candidate') {
      const headers = new Headers(init.headers || {})
      headers.set('X-TBBD-Local-Portal', 'candidate')

      return originalFetch(input, {
        ...init,
        headers,
      })
    }

    return originalFetch(input, init)
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
