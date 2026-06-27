import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, CheckCircle, Clock, BarChart2, Filter } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import toast from 'react-hot-toast'
import api from '../api'
import { useAuth } from '../hooks/useAuth'
import './AdminDashboard.css'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ status: '', category: '' })
  const [pincodes, setPincodes] = useState([])

  useEffect(() => {
    api.get('/otp/pincodes').then(({ data }) => setPincodes(data.pincodes))
    api.get('/admin/stats').then(({ data }) => setStats(data))
    fetchIssues()
  }, [])

  useEffect(() => { fetchIssues() }, [filter])

  const fetchIssues = async () => {
    try {
      const params = Object.fromEntries(Object.entries(filter).filter(([, v]) => v))
      const { data } = await api.get('/admin/issues', { params: { ...params, limit: 50 } })
      setIssues(data.issues)
    } catch { toast.error('Failed to load issues') }
    finally { setLoading(false) }
  }

  const quickStatus = async (issueId, newStatus) => {
    try {
      await api.patch(`/admin/issues/${issueId}/status`, { status: newStatus })
      toast.success(`Marked as ${newStatus.replace('_', ' ')}`)
      setIssues(prev => prev.map(i => i.id === issueId ? { ...i, status: newStatus } : i))
      api.get('/admin/stats').then(({ data }) => setStats(data))
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to update') }
  }

  const policeStation = stats?.police_station || 'All Stations'
  const pincode = user?.pincode

  return (
    <div className="admin-page">
      <div className="admin-container page-container-wide">
        <div className="admin-header">
          <div>
            <h2>Admin Dashboard</h2>
            <p className="admin-subtitle">
              🚔 {policeStation}
              {pincode && <span> · Pincode {pincode}</span>}
              {user?.role === 'admin' && <span className="super-badge">Super Admin</span>}
            </p>
          </div>
          {user?.role === 'admin' && (
            <Link to="/admin/create-admin" className="btn btn-primary btn-sm">+ Add Admin</Link>
          )}
        </div>

        {/* Stats */}
        {stats && (
          <div className="admin-stats">
            <div className="stat-card total">
              <BarChart2 size={22} />
              <div className="stat-num">{stats.total}</div>
              <div className="stat-lbl">Total Issues</div>
            </div>
            <div className="stat-card pending">
              <AlertCircle size={22} />
              <div className="stat-num">{stats.pending}</div>
              <div className="stat-lbl">Pending</div>
            </div>
            <div className="stat-card progress">
              <Clock size={22} />
              <div className="stat-num">{stats.in_progress}</div>
              <div className="stat-lbl">In Progress</div>
            </div>
            <div className="stat-card resolved">
              <CheckCircle size={22} />
              <div className="stat-num">{stats.resolved}</div>
              <div className="stat-lbl">Resolved</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="admin-filters card">
          <Filter size={16} />
          <select className="input-field" value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
            <option value="">All Status</option>
            <option value="pending">🔴 Pending</option>
            <option value="in_progress">🟡 In Progress</option>
            <option value="resolved">🟢 Resolved</option>
          </select>
          <select className="input-field" value={filter.category} onChange={e => setFilter(f => ({ ...f, category: e.target.value }))}>
            <option value="">All Categories</option>
            {['Pothole','Water Leakage','Streetlight','Garbage / Waste','Drainage Blockage','Road Damage','Illegal Parking','Tree Fall','Electricity Issue','Other'].map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <button className="btn btn-outline btn-sm" onClick={() => setFilter({ status: '', category: '' })}>Clear</button>
        </div>

        {/* Issues Table */}
        <div className="admin-issues">
          {loading ? (
            <div className="admin-loading"><span className="spinner spinner-dark" /></div>
          ) : issues.length === 0 ? (
            <div className="empty-state card"><div style={{ fontSize: '2.5rem' }}>✅</div><h3>No issues found</h3></div>
          ) : (
            <div className="issues-table">
              {issues.map(issue => (
                <AdminIssueRow
                  key={issue.id}
                  issue={issue}
                  onQuickStatus={quickStatus}
                  pincodes={pincodes}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function AdminIssueRow({ issue, onQuickStatus, pincodes }) {
  const pinInfo = pincodes.find(p => p.pincode === issue.pincode)

  return (
    <div className={`admin-issue-row card ${issue.status}`}>
      <div className="arow-left">
        {issue.media_urls?.[0] && (
          <img src={issue.media_urls[0]} alt="" className="arow-thumb" />
        )}
        <div className="arow-info">
          <div className="arow-badges">
            <span className={`badge badge-${issue.status}`}>
              {issue.status === 'pending' ? '🔴' : issue.status === 'in_progress' ? '🟡' : '🟢'}
              {' '}{issue.status.replace('_', ' ')}
            </span>
            <span className="cat-tag">{issue.category}</span>
          </div>
          <Link to={`/admin/issues/${issue.id}`} className="arow-title">{issue.title}</Link>
          <div className="arow-meta">
            📍 {issue.area || issue.pincode} · 
            👤 {issue.reporter?.name} ({issue.reporter?.phone}) · 
            🕐 {formatDistanceToNow(new Date(issue.created_at), { addSuffix: true })} ·
            👍 {issue.upvotes}
          </div>
        </div>
      </div>

      <div className="arow-actions">
        {issue.status !== 'in_progress' && issue.status !== 'resolved' && (
          <button className="btn btn-sm" style={{ background: 'var(--yellow-light)', color: 'var(--yellow)', border: '1px solid #fcd34d' }}
            onClick={() => onQuickStatus(issue.id, 'in_progress')}>
            🟡 In Progress
          </button>
        )}
        {issue.status !== 'resolved' && (
          <button className="btn btn-green btn-sm" onClick={() => onQuickStatus(issue.id, 'resolved')}>
            🟢 Resolve
          </button>
        )}
        <Link to={`/admin/issues/${issue.id}`} className="btn btn-outline btn-sm">View Details</Link>
      </div>
    </div>
  )
}
