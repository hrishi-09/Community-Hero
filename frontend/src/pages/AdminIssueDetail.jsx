import { useState, useEffect, useRef } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ArrowLeft, Upload, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import api from '../api'
import './AdminIssueDetail.css'

export default function AdminIssueDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const proofRef = useRef()
  const [issue, setIssue] = useState(null)
  const [loading, setLoading] = useState(true)
  const [statusNote, setStatusNote] = useState('')
  const [proofFiles, setProofFiles] = useState([])
  const [proofPreviews, setProofPreviews] = useState([])
  const [updating, setUpdating] = useState(false)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    api.get(`/issues/${id}`).then(({ data }) => { setIssue(data); setLoading(false) }).catch(() => setLoading(false))
  }, [id])

  const updateStatus = async (newStatus) => {
    setUpdating(true)
    try {
      await api.patch(`/admin/issues/${id}/status`, { status: newStatus, note: statusNote })
      toast.success(`Status updated to "${newStatus.replace('_', ' ')}"`)
      setIssue(i => ({ ...i, status: newStatus }))
      setStatusNote('')
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed') }
    finally { setUpdating(false) }
  }

  const handleProofFiles = (e) => {
    const files = Array.from(e.target.files)
    setProofFiles(files)
    setProofPreviews(files.map(f => URL.createObjectURL(f)))
  }

  const uploadProof = async () => {
    if (proofFiles.length === 0) return toast.error('Please select proof photos')
    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('note', statusNote || 'Issue resolved by admin')
      proofFiles.forEach(f => fd.append('files', f))
      await api.post(`/admin/issues/${id}/resolve-proof`, fd)
      toast.success('Issue resolved with proof uploaded! 🎉')
      navigate('/admin')
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to upload proof') }
    finally { setUploading(false) }
  }

  if (loading) return <div className="adi-loading"><span className="spinner spinner-dark" /></div>
  if (!issue) return <div className="adi-loading"><p>Issue not found.</p></div>

  const media = issue.media_urls || []
  const isResolved = issue.status === 'resolved'

  return (
    <div className="adi-page">
      <div className="adi-container page-container">
        <Link to="/admin" className="back-link"><ArrowLeft size={16} /> Back to Dashboard</Link>

        <div className="adi-grid">
          {/* Left: Issue Info */}
          <div className="adi-left">
            <div className="card adi-issue-card fade-in">
              <div className="adi-issue-header">
                <div className="adi-badges">
                  <span className={`badge badge-${issue.status}`}>
                    {issue.status === 'pending' ? '🔴' : issue.status === 'in_progress' ? '🟡' : '🟢'}
                    {' '}{issue.status.replace('_', ' ')}
                  </span>
                  <span className="cat-tag-lg">{issue.category}</span>
                </div>
                <h2>{issue.title}</h2>
                <div className="adi-reporter-info">
                  <div className="adi-reporter-row">
                    <span>👤 <strong>{issue.reporter?.name}</strong></span>
                    <span>📞 {issue.reporter?.phone}</span>
                    <span>📧 {issue.reporter?.email}</span>
                  </div>
                  <div className="adi-location">
                    📍 {issue.area || issue.pincode} ({issue.pincode})
                    {issue.location_description && <span> · {issue.location_description}</span>}
                  </div>
                  <div className="adi-time">
                    🕐 Reported {formatDistanceToNow(new Date(issue.created_at), { addSuffix: true })}
                    · {format(new Date(issue.created_at), 'dd MMM yyyy, h:mm a')}
                  </div>
                  <div>👍 {issue.upvotes} upvotes · 👁 {issue.views} views</div>
                </div>
              </div>

              {issue.description && (
                <div className="adi-desc">
                  <h4>Description</h4>
                  <p>{issue.description}</p>
                </div>
              )}

              {media.length > 0 && (
                <div className="adi-media">
                  <h4>Submitted Media</h4>
                  <div className={`media-grid ${media.length > 1 ? 'cols-2' : ''}`}>
                    {media.map((url, i) =>
                      url.match(/\.(mp4|webm|mov)$/i)
                        ? <video key={i} src={url} controls />
                        : <img key={i} src={url} alt="Issue media" />
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Timeline */}
            {issue.actions?.length > 0 && (
              <div className="card adi-timeline fade-in">
                <h4>Activity Log</h4>
                {issue.actions.map(a => (
                  <div key={a.id} className="adi-titem">
                    <div className="adi-tdot" style={{ background: a.new_status === 'resolved' ? 'var(--green)' : a.new_status === 'in_progress' ? 'var(--yellow)' : 'var(--brand)' }} />
                    <div>
                      <strong>{a.action === 'status_change' ? `Status → "${a.new_status?.replace('_', ' ')}"` : '📸 Resolution proof uploaded'}</strong>
                      {a.note && <p style={{ fontSize: '0.83rem', color: 'var(--gray-500)', marginTop: 2 }}>{a.note}</p>}
                      <span style={{ fontSize: '0.75rem', color: 'var(--gray-400)' }}>
                        by {a.admin?.name} · {format(new Date(a.created_at), 'dd MMM yyyy, h:mm a')}
                      </span>
                      {a.proof_urls?.length > 0 && (
                        <div className="media-grid cols-2" style={{ marginTop: 8 }}>
                          {a.proof_urls.map((u, i) => <img key={i} src={u} alt="Proof" />)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right: Admin Actions */}
          <div className="adi-right">
            <div className="card adi-actions-panel fade-in">
              <h3>Admin Actions</h3>

              <div className="input-group">
                <label>Note / Remark (optional)</label>
                <textarea
                  className="input-field"
                  rows={3}
                  placeholder="Add a note about this status change..."
                  value={statusNote}
                  onChange={e => setStatusNote(e.target.value)}
                />
              </div>

              {!isResolved && (
                <div className="action-buttons">
                  {issue.status !== 'in_progress' && (
                    <button
                      className="action-status-btn in-progress"
                      onClick={() => updateStatus('in_progress')}
                      disabled={updating}
                    >
                      <Clock size={18} />
                      <div>
                        <div className="asb-title">Mark In Progress</div>
                        <div className="asb-desc">Police is working on it</div>
                      </div>
                    </button>
                  )}

                  <button
                    className="action-status-btn resolved"
                    onClick={() => updateStatus('resolved')}
                    disabled={updating}
                  >
                    <CheckCircle size={18} />
                    <div>
                      <div className="asb-title">Mark Resolved</div>
                      <div className="asb-desc">Without uploading proof</div>
                    </div>
                  </button>
                </div>
              )}

              {/* Proof Upload */}
              <div className="proof-section">
                <h4>
                  <Upload size={16} />
                  {isResolved ? 'Add More Proof Photos' : 'Resolve with Proof Photos'}
                </h4>
                <p className="proof-hint">Upload photos showing the issue has been fixed</p>

                {proofPreviews.length > 0 && (
                  <div className={`media-grid ${proofPreviews.length > 1 ? 'cols-2' : ''}`} style={{ margin: '12px 0' }}>
                    {proofPreviews.map((url, i) => <img key={i} src={url} alt="Proof preview" />)}
                  </div>
                )}

                <button className="proof-select-btn" onClick={() => proofRef.current.click()}>
                  <Upload size={16} /> Select Proof Photos
                </button>
                <input ref={proofRef} type="file" multiple hidden accept="image/*" onChange={handleProofFiles} />

                {proofFiles.length > 0 && (
                  <button className="btn btn-green btn-full" onClick={uploadProof} disabled={uploading} style={{ marginTop: 12 }}>
                    {uploading ? <span className="spinner" /> : <><CheckCircle size={16} /> Resolve & Upload Proof</>}
                  </button>
                )}
              </div>

              {isResolved && (
                <div className="resolved-badge">
                  <CheckCircle size={20} color="var(--green)" />
                  <span>This issue is marked as <strong>Resolved</strong></span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
