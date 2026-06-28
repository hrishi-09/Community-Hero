import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { ThumbsUp, MessageCircle, Eye, MapPin, Filter, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api'
import { useAuth } from '../hooks/useAuth'
import { formatDistanceToNow } from 'date-fns'
import './Feed.css'

const CATEGORIES = ['', 'Pothole', 'Water Leakage', 'Streetlight', 'Garbage / Waste', 'Drainage Blockage', 'Road Damage', 'Illegal Parking', 'Tree Fall', 'Electricity Issue', 'Other']
const STATUSES = ['', 'pending', 'in_progress', 'resolved']

export default function Feed() {
  const { user } = useAuth()
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ pincode: '', category: '', status: '' })
  const [pincodes, setPincodes] = useState([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    api.get('/otp/pincodes').then(({ data }) => setPincodes(data.pincodes)).catch(() => {})
  }, [])

  const fetchIssues = useCallback(async (pg = 1, reset = false) => {
    try {
      setLoading(true)
      const params = { page: pg, limit: 10, ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)) }
      const { data } = await api.get('/issues/', { params })
      setTotal(data.total)
      setIssues(prev => reset || pg === 1 ? data.issues : [...prev, ...data.issues])
      setPage(pg)
    } catch {
      toast.error('Failed to load feed')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetchIssues(1, true) }, [filters])

  const handleUpvote = async (issueId, e) => {
    e.preventDefault()
    if (!user) return toast.error('Login to upvote')
    try {
      const { data } = await api.post(`/issues/${issueId}/upvote`)
      setIssues(prev => prev.map(i => i.id === issueId ? { ...i, upvotes: data.upvotes, upvoted_by_me: data.upvoted } : i))
    } catch { toast.error('Failed to upvote') }
  }

  const setFilter = (k) => (e) => setFilters(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="feed-page">
      <div className="feed-container page-container">
        <div className="feed-header">
          <div>
            <h2>Community Feed</h2>
            <p className="feed-subtitle">{total} issues reported across Kolkata</p>
          </div>
          <div className="feed-header-actions">
            <button className="btn btn-outline btn-sm" onClick={() => setShowFilters(f => !f)}>
              <Filter size={15} /> Filter
            </button>
            <button className="btn btn-outline btn-sm" onClick={() => fetchIssues(1, true)}>
              <RefreshCw size={15} />
            </button>
            {user && <Link to="/post" className="btn btn-primary btn-sm">+ Report Issue</Link>}
          </div>
        </div>

        {showFilters && (
          <div className="feed-filters card fade-in">
            <select className="input-field" value={filters.pincode} onChange={setFilter('pincode')}>
              <option value="">All Pincodes</option>
              {pincodes.map(p => <option key={p.pincode} value={p.pincode}>{p.pincode} — {p.area}</option>)}
            </select>
            <select className="input-field" value={filters.category} onChange={setFilter('category')}>
              {CATEGORIES.map(c => <option key={c} value={c}>{c || 'All Categories'}</option>)}
            </select>
            <select className="input-field" value={filters.status} onChange={setFilter('status')}>
              {STATUSES.map(s => <option key={s} value={s}>{s ? s.replace('_', ' ') : 'All Status'}</option>)}
            </select>
            <button className="btn btn-outline btn-sm" onClick={() => setFilters({ pincode: '', category: '', status: '' })}>Clear</button>
          </div>
        )}

        <div className="issues-list">
          {loading && issues.length === 0 ? (
            <div className="feed-loading">
              {[1,2,3].map(i => <div key={i} className="skeleton-card card" />)}
            </div>
          ) : issues.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem' }}>🏙️</div>
              <h3>No issues found</h3>
              <p>Be the first to report an issue in your area!</p>
              <Link to="/post" className="btn btn-primary" style={{ marginTop: 16 }}>Report an Issue</Link>
            </div>
          ) : (
            issues.map(issue => (
              <IssueCard key={issue.id} issue={issue} onUpvote={handleUpvote} />
            ))
          )}
        </div>

        {issues.length < total && !loading && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <button className="btn btn-outline" onClick={() => fetchIssues(page + 1)}>Load More</button>
          </div>
        )}
      </div>
    </div>
  )
}

function IssueCard({ issue, onUpvote }) {
  const media = issue.media_urls || []
  const timeAgo = formatDistanceToNow(new Date(issue.created_at), { addSuffix: true })

  return (
    <Link to={`/issues/${issue.id}`} className="issue-card card fade-in">
      <div className="issue-card-header">
        <div className="reporter-info">
          <div className="reporter-avatar">
            {issue.reporter?.avatar_url
              ? <img src={issue.reporter.avatar_url} alt="" />
              : <span>{issue.reporter?.name?.[0]?.toUpperCase() || '?'}</span>
            }
          </div>
          <div>
            <div className="reporter-name">{issue.reporter?.name || 'Anonymous'}</div>
            <div className="issue-meta">
              <MapPin size={11} /> {issue.area || issue.pincode} · {timeAgo}
            </div>
          </div>
        </div>
        <span className={`badge badge-${issue.status}`}>
          {issue.status === 'pending' ? '🔴' : issue.status === 'in_progress' ? '🟡' : '🟢'}
          {' '}{issue.status.replace('_', ' ')}
        </span>
      </div>

      <div className="issue-card-body">
        <div className="issue-category-tag">{issue.category}</div>
        <h3 className="issue-title">{issue.title}</h3>
        {issue.description && <p className="issue-desc">{issue.description.slice(0, 160)}{issue.description.length > 160 ? '…' : ''}</p>}
      </div>

      {media.length > 0 && (
        <div className={`media-grid ${media.length >= 2 ? 'cols-2' : ''}`} style={{ padding: '0 16px' }}>
          {media.slice(0, 4).map((url, i) => (
            url.match(/\.(mp4|webm|mov)$/i)
              ? <video key={i} src={url} muted />
              : <img key={i} src={url} alt="Issue" loading="lazy" />
          ))}
        </div>
      )}

      <div className="issue-card-footer">
        <button
          className={`action-btn ${issue.upvoted_by_me ? 'upvoted' : ''}`}
          onClick={(e) => onUpvote(issue.id, e)}
        >
          <ThumbsUp size={15} /> {issue.upvotes}
        </button>
        <span className="action-btn"><MessageCircle size={15} /> Comments</span>
        <span className="action-btn"><Eye size={15} /> {issue.views}</span>
        <span className="police-tag">
          🚔 {issue.police_station?.replace(' Police Station', '')}
        </span>
      </div>
    </Link>
  )
}
