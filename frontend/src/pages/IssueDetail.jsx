import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ThumbsUp, MapPin, Clock, Send, ArrowLeft, CheckCircle } from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import api from '../api'
import { useAuth } from '../hooks/useAuth'
import './IssueDetail.css'

export default function IssueDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [issue, setIssue] = useState(null)
  const [loading, setLoading] = useState(true)
  const [comment, setComment] = useState('')
  const [commenting, setCommenting] = useState(false)

  useEffect(() => {
    api.get(`/issues/${id}`).then(({ data }) => { setIssue(data); setLoading(false) }).catch(() => setLoading(false))
  }, [id])

  const handleUpvote = async () => {
    if (!user) return toast.error('Login to upvote')
    const { data } = await api.post(`/issues/${id}/upvote`)
    setIssue(i => ({ ...i, upvotes: data.upvotes, upvoted_by_me: data.upvoted }))
  }

  const handleComment = async (e) => {
    e.preventDefault()
    if (!comment.trim()) return
    setCommenting(true)
    try {
      const { data } = await api.post(`/issues/${id}/comment`, { content: comment })
      setIssue(i => ({ ...i, comments: [...(i.comments || []), data] }))
      setComment('')
    } catch { toast.error('Failed to post comment') }
    finally { setCommenting(false) }
  }

  if (loading) return <div className="detail-loading"><span className="spinner spinner-dark" /></div>
  if (!issue) return <div className="detail-loading"><p>Issue not found.</p><Link to="/feed">Go to Feed</Link></div>

  const media = issue.media_urls || []
  const resolvedProofs = issue.actions?.filter(a => a.action === 'resolved_proof').flatMap(a => a.proof_urls || []) || []

  return (
    <div className="detail-page">
      <div className="detail-container page-container">
        <Link to="/feed" className="back-link"><ArrowLeft size={16} /> Back to Feed</Link>

        <div className="detail-main card fade-in">
          <div className="detail-header">
            <div className="detail-meta-row">
              <span className={`badge badge-${issue.status}`}>
                {issue.status === 'pending' ? '🔴' : issue.status === 'in_progress' ? '🟡' : '🟢'}
                {' '}{issue.status.replace('_', ' ')}
              </span>
              <span className="detail-category">{issue.category}</span>
            </div>
            <h1 className="detail-title">{issue.title}</h1>
            <div className="detail-reporter">
              <div className="reporter-avatar sm">
                {issue.reporter?.avatar_url
                  ? <img src={issue.reporter.avatar_url} alt="" />
                  : <span>{issue.reporter?.name?.[0]?.toUpperCase() || '?'}</span>
                }
              </div>
              <span><strong>{issue.reporter?.name}</strong> · <MapPin size={12} /> {issue.area || issue.pincode} · <Clock size={12} /> {formatDistanceToNow(new Date(issue.created_at), { addSuffix: true })}</span>
            </div>
          </div>

          {issue.description && (
            <div className="detail-description">{issue.description}</div>
          )}

          {issue.location_description && (
            <div className="detail-location">
              <MapPin size={14} /> {issue.location_description}
            </div>
          )}

          {media.length > 0 && (
            <div className={`media-grid ${media.length > 1 ? 'cols-2' : ''}`} style={{ padding: '0 20px' }}>
              {media.map((url, i) =>
                url.match(/\.(mp4|webm|mov)$/i)
                  ? <video key={i} src={url} controls />
                  : <img key={i} src={url} alt="Issue media" />
              )}
            </div>
          )}

          <div className="detail-actions">
            <button className={`action-btn ${issue.upvoted_by_me ? 'upvoted' : ''}`} onClick={handleUpvote}>
              <ThumbsUp size={16} /> {issue.upvotes} Upvotes
            </button>
            <span className="detail-views">👁 {issue.views} views</span>
            <div className="detail-police">
              🚔 <strong>{issue.police_station}</strong>
            </div>
          </div>
        </div>

        {/* Resolution proof */}
        {issue.status === 'resolved' && resolvedProofs.length > 0 && (
          <div className="resolved-section card fade-in">
            <div className="resolved-header">
              <CheckCircle size={20} color="var(--green)" />
              <h3>Issue Resolved — Admin Proof</h3>
            </div>
            <div className={`media-grid ${resolvedProofs.length > 1 ? 'cols-2' : ''}`}>
              {resolvedProofs.map((url, i) => <img key={i} src={url} alt="Resolution proof" />)}
            </div>
          </div>
        )}

        {/* Timeline */}
        {issue.actions?.length > 0 && (
          <div className="timeline card fade-in">
            <h3>Activity Timeline</h3>
            {issue.actions.map(a => (
              <div key={a.id} className="timeline-item">
                <div className="timeline-dot" style={{ background: a.new_status === 'resolved' ? 'var(--green)' : a.new_status === 'in_progress' ? 'var(--yellow)' : 'var(--brand)' }} />
                <div className="timeline-content">
                  <span className="timeline-action">
                    {a.action === 'status_change' ? `Status changed to "${a.new_status?.replace('_', ' ')}"` : 'Resolution proof uploaded'}
                  </span>
                  {a.note && <p className="timeline-note">{a.note}</p>}
                  <span className="timeline-by">by {a.admin?.name} · {format(new Date(a.created_at), 'dd MMM yyyy, h:mm a')}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Comments */}
        <div className="comments-section card fade-in">
          <h3>Comments ({issue.comments?.length || 0})</h3>

          {user && (
            <form className="comment-form" onSubmit={handleComment}>
              <div className="comment-input-row">
                <div className="reporter-avatar sm">
                  <span>{user.name?.[0]?.toUpperCase()}</span>
                </div>
                <input
                  className="input-field"
                  placeholder="Write a comment..."
                  value={comment}
                  onChange={e => setComment(e.target.value)}
                />
                <button type="submit" className="btn btn-primary btn-sm" disabled={commenting || !comment.trim()}>
                  <Send size={14} />
                </button>
              </div>
            </form>
          )}

          <div className="comments-list">
            {issue.comments?.length === 0 && (
              <p className="no-comments">No comments yet. Be the first!</p>
            )}
            {issue.comments?.map(c => (
              <div key={c.id} className="comment">
                <div className="reporter-avatar sm">
                  {c.user?.avatar_url
                    ? <img src={c.user.avatar_url} alt="" />
                    : <span>{c.user?.name?.[0]?.toUpperCase()}</span>
                  }
                </div>
                <div className="comment-body">
                  <span className="comment-author">{c.user?.name}</span>
                  <span className="comment-time">{formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}</span>
                  <p>{c.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
