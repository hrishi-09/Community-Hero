import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('ch_user')) } catch { return null }
  })
  const [loading, setLoading] = useState(false)

  const login = (token, userData) => {
    localStorage.setItem('ch_token', token)
    localStorage.setItem('ch_user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('ch_token')
    localStorage.removeItem('ch_user')
    setUser(null)
  }

  const refreshUser = async () => {
    try {
      const { data } = await api.get('/users/me')
      localStorage.setItem('ch_user', JSON.stringify(data))
      setUser(data)
    } catch {}
  }

  return (
    <AuthCtx.Provider value={{ user, login, logout, refreshUser, loading }}>
      {children}
    </AuthCtx.Provider>
  )
}

export const useAuth = () => useContext(AuthCtx)
