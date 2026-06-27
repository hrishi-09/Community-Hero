import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Camera, Edit3, Save, Award, FileText, CheckCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import api from '../api'
import { useAuth } from '../hooks/useAuth'
import './Profile.css'

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const [profile, setProfile] = useState(null)
  const [myIssues, setMyIssues] = useState([])
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ name: '', bio: '' })
  const [saving, setSaving] = useState(false)
  const avatarRef = useRef()

  useEffect(() => {
    api.get('/users/me').then(({ data }) => {
      setProfile(data)
      setForm({ name: data.name, bio: data.bio || '' })
    })
    api.get('/users/me/issues').then(({ data }) => setMyIssues(data.issues))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.patch('/users/me', form)
      toast.success('Profile updated!')
      setEditing(false)
      await refreshUser()
      const { data } = await api.get('/users/me')
      setProfile(data)
    } catch { toast.error('Failed to update profile') }
    finally { setSaving(false) }
  }

  const handleAvatar = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      await api.post('/users/me/avatar', fd)
      toast.success('Avatar updated!')
      await refreshUser()
      const { data } = await api.get('/users/me')
      setProfile(data)
    } catch { toast.error('Failed to upload avatar') }
  }

  if (!profile) return <div className="profile-loading"><span className="spinner spinner-dark" /></div>

  const levelLabel = profile.points >= 500 ? '🏆 Champion' : profile.points >= 200 ? '⭐ Hero' : profile.points >= 50 ? '🌟 Activist' : '🌱 Newcomer'

  return (
    <div className="profile-page">
      <div className="profile-container page-container">
        <div className="profile-card card fade-in">
          <div className="profile-cover" />
          <div className="profile-body">
            <div className="avatar-wrap">
              <div className="profile-avatar">
                {profile.avatar_url
                  ? <img src={profile.avatar_url} alt={profile.name} />
                  : <span>{profile.name?.[0]?.toUpperCase()}</span>
                }
              </div>
              <button className="avatar-edit-btn" onClick={() => avatarRef.current.click()} title="Change photo">
                <Camera size={14} />
              </button>
              <input ref={avatarRef} type="file" accept="image/*" hidden onChange={handleAvatar} />
            </div>

            <div className="profile-info">
              {editing ? (
                <div className="edit-form">
                  <input
                    className="input-field"
                    value={form.name}
                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                    placeholder="Your name"
                  />
                  <textarea
                    className="input-field"
                    rows={2}
                    value={form.bio}
                    onChange={e => setForm(f => ({ ...f, bio: e.target.value }))}
                    placeholder="Tell your community about yourself..."
                  />
                  <div className="edit-actions">
                    <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
                      {saving ? <span className="spinner" /> : <><Save size={14} /> Save</>}
                    </button>
                    <button className="btn btn-outline btn-sm" onClick={() => setEditing(false)}>Cancel</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="profile-name-row">
                    <h2>{profile.name}</h2>
                    {profile.is_verified && <span className="verified-badge">✓ Verified</span>}
                    <button className="edit-btn" onClick={() => setEditing(true)}><Edit3 size={15} /></button>
                  </div>
                  <p className="profile-email">{profile.email} · +91 {profile.phone}</p>
                  {profile.area && <p className="profile-area">📍 {profile.area} ({profile.pincode})</p>}
                  {profile.bio && <p className="profile-bio">{profile.bio}</p>}
                </>
              )}
            </div>

            {/* Stats */}
            <div className="profile-stats">
              <div className="stat-box">
                <div className="stat-icon"><Award size={20} color="var(--brand)" /></div>
                <div className="stat-value">{profile.points}</div>
                <div className="stat-label">Points</div>
                <div className="stat-level">{levelLabel}</div>
              </div>
              <div className="stat-box">
                <div className="stat-icon"><FileText size={20} color="var(--yellow)" /></div>
                <div className="stat-value">{profile.stats?.total_issues || 0}</div>
                <div className="stat-label">Reported</div>
              </div>
              <div className="stat-box">
                <div className="stat-icon"><CheckCircle size={20} color="var(--green)" /></div>
                <div className="stat-value">{profile.stats?.resolved_issues || 0}</div>
                <div className="stat-label">Resolved</div>
              </div>
            </div>
          </div>
        </div>

        {/* My Issues */}
        <div className="my-issues">
          <h3 className="section-title">My Reports</h3>
          {myIssues.length === 0 ? (
            <div className="empty-state card">
              <div style={{ fontSize: '2.5rem' }}>📋</div>
              <h3>No reports yet</h3>
              <p>Start contributing to your community!</p>
              <Link to="/post" className="btn btn-primary" style={{ marginTop: 12 }}>Report an Issue</Link>
            </div>
          ) : (
            <div className="my-issues-grid">
              {myIssues.map(issue => (
                <Link key={issue.id} to={`/issues/${issue.id}`} className="my-issue-card card">
                  {issue.media_urls?.[0] && (
                    <img src={issue.media_urls[0]} alt="" className="my-issue-thumb" />
                  )}
                  <div className="my-issue-body">
                    <span className={`badge badge-${issue.status}`}>
                      {issue.status === 'pending' ? '🔴' : issue.status === 'in_progress' ? '🟡' : '🟢'}
                      {' '}{issue.status.replace('_', ' ')}
                    </span>
                    <p className="my-issue-title">{issue.title}</p>
                    <p className="my-issue-meta">{issue.area || issue.pincode} · {formatDistanceToNow(new Date(issue.created_at), { addSuffix: true })}</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
