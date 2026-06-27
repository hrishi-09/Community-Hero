import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Home, PlusCircle, User, Shield, LogOut, MapPin } from 'lucide-react'
import './Navbar.css'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav className="navbar">
      <div className="navbar-inner page-container-wide">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">🏙️</div>
          <div className="brand-text">
            <span className="brand-name">Community Hero</span>
            <span className="brand-city">
              <MapPin size={10} /> Kolkata
            </span>
          </div>
        </Link>

        {user && (
          <div className="navbar-links">
            <Link to="/feed" className={`nav-link ${isActive('/feed') || isActive('/') ? 'active' : ''}`}>
              <Home size={18} /> <span>Feed</span>
            </Link>
            <Link to="/post" className={`nav-link ${isActive('/post') ? 'active' : ''}`}>
              <PlusCircle size={18} /> <span>Report</span>
            </Link>
            {['admin', 'police'].includes(user.role) && (
              <Link to="/admin" className={`nav-link ${isActive('/admin') ? 'active' : ''}`}>
                <Shield size={18} /> <span>Admin</span>
              </Link>
            )}
            <Link to="/profile" className={`nav-link ${isActive('/profile') ? 'active' : ''}`}>
              {user.avatar_url
                ? <img src={user.avatar_url} alt="" className="nav-avatar" />
                : <div className="nav-avatar-placeholder">{user.name?.[0]?.toUpperCase()}</div>
              }
              <span>Profile</span>
            </Link>
            <button onClick={handleLogout} className="nav-link nav-logout" title="Logout">
              <LogOut size={18} />
            </button>
          </div>
        )}

        {!user && (
          <div className="navbar-links">
            <Link to="/login" className="btn btn-outline btn-sm">Log In</Link>
            <Link to="/register" className="btn btn-primary btn-sm">Sign Up</Link>
          </div>
        )}
      </div>
    </nav>
  )
}
