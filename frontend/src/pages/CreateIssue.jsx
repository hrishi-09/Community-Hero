import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Image, Video, X, MapPin, Send } from 'lucide-react'
import api from '../api'
import './CreateIssue.css'

const CATEGORIES = ['Pothole', 'Water Leakage', 'Streetlight', 'Garbage / Waste', 'Drainage Blockage', 'Road Damage', 'Illegal Parking', 'Tree Fall', 'Electricity Issue', 'Other']

export default function CreateIssue() {
  const navigate = useNavigate()
  const fileRef = useRef()
  const [pincodes, setPincodes] = useState([])
  const [loading, setLoading] = useState(false)
  const [mediaFiles, setMediaFiles] = useState([])
  const [mediaPreviews, setMediaPreviews] = useState([])
  const [form, setForm] = useState({ title: '', description: '', category: '', pincode: '', location_description: '' })

  useEffect(() => {
    api.get('/otp/pincodes').then(({ data }) => setPincodes(data.pincodes)).catch(() => {})
  }, [])

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleFiles = (e) => {
    const files = Array.from(e.target.files)
    if (mediaFiles.length + files.length > 4) return toast.error('Maximum 4 media files allowed')
    const newFiles = [...mediaFiles, ...files]
    setMediaFiles(newFiles)
    const previews = newFiles.map(f => ({ url: URL.createObjectURL(f), type: f.type, name: f.name }))
    setMediaPreviews(previews)
  }

  const removeMedia = (idx) => {
    const newFiles = mediaFiles.filter((_, i) => i !== idx)
    setMediaFiles(newFiles)
    setMediaPreviews(newFiles.map(f => ({ url: URL.createObjectURL(f), type: f.type })))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) return toast.error('Please add a title')
    if (!form.category) return toast.error('Please select a category')
    if (!form.pincode) return toast.error('Please select a pincode')

    setLoading(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => fd.append(k, v))
      mediaFiles.forEach(f => fd.append('files', f))
      const { data } = await api.post('/issues/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      toast.success('Issue reported! 🎉 You earned 10 points.')
      navigate(`/issues/${data.id}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to post issue')
    } finally {
      setLoading(false)
    }
  }

  const selectedPincode = pincodes.find(p => p.pincode === form.pincode)

  return (
    <div className="create-page">
      <div className="create-container page-container">
        <div className="create-header">
          <h2>Report an Issue</h2>
          <p>Help your community by reporting local problems</p>
        </div>

        <form onSubmit={handleSubmit} className="create-form card">
          <div className="input-group">
            <label>Issue Title *</label>
            <input className="input-field" type="text" placeholder="e.g. Large pothole on main road near market" value={form.title} onChange={set('title')} maxLength={200} required />
          </div>

          <div className="input-group">
            <label>Description</label>
            <textarea className="input-field" rows={4} placeholder="Describe the issue in detail — how long has it been there, severity, risk to public, etc." value={form.description} onChange={set('description')} />
          </div>

          <div className="form-row">
            <div className="input-group">
              <label>Category *</label>
              <select className="input-field" value={form.category} onChange={set('category')} required>
                <option value="">Select category</option>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div className="input-group">
              <label>Kolkata Pincode *</label>
              <select className="input-field" value={form.pincode} onChange={set('pincode')} required>
                <option value="">Select pincode</option>
                {pincodes.map(p => <option key={p.pincode} value={p.pincode}>{p.pincode} — {p.area}</option>)}
              </select>
            </div>
          </div>

          {selectedPincode && (
            <div className="station-badge fade-in">
              <MapPin size={14} />
              <span>Will be sent to: <strong>{selectedPincode.police_station}</strong></span>
            </div>
          )}

          <div className="input-group">
            <label>Exact Location (optional)</label>
            <input className="input-field" type="text" placeholder="e.g. Near Salt Lake City Centre, opposite gate 3" value={form.location_description} onChange={set('location_description')} />
          </div>

          {/* Media upload */}
          <div className="media-upload-section">
            <div className="media-upload-header">
              <span className="media-upload-label">Photos / Videos</span>
              <span className="media-count">{mediaFiles.length}/4</span>
            </div>

            {mediaPreviews.length > 0 && (
              <div className="media-preview-grid">
                {mediaPreviews.map((m, i) => (
                  <div key={i} className="media-preview-item">
                    {m.type?.startsWith('video')
                      ? <video src={m.url} muted />
                      : <img src={m.url} alt="Preview" />
                    }
                    <button type="button" className="media-remove" onClick={() => removeMedia(i)}>
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="media-actions">
              <button type="button" className="media-btn" onClick={() => { fileRef.current.accept = 'image/*'; fileRef.current.click() }}>
                <Image size={16} /> Add Photos
              </button>
              <button type="button" className="media-btn" onClick={() => { fileRef.current.accept = 'video/*'; fileRef.current.click() }}>
                <Video size={16} /> Add Video
              </button>
              <input ref={fileRef} type="file" multiple hidden onChange={handleFiles} />
            </div>
          </div>

          <div className="form-submit">
            <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading}>
              {loading ? <><span className="spinner" /> Posting...</> : <><Send size={18} /> Post Issue</>}
            </button>
            <p className="points-hint">💡 Earn 10 points for each issue you report!</p>
          </div>
        </form>
      </div>
    </div>
  )
}
