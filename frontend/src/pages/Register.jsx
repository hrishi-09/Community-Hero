import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'
import api from '../api'
import './Auth.css'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1=form, 2=otp
  const [pincodes, setPincodes] = useState([])
  const [loading, setLoading] = useState(false)
  const [otpLoading, setOtpLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [form, setForm] = useState({ name: '', email: '', phone: '', password: '', pincode: '', otp_code: '' })

  useEffect(() => {
    api.get('/otp/pincodes').then(({ data }) => setPincodes(data.pincodes)).catch(() => {})
  }, [])

  useEffect(() => {
    if (countdown > 0) {
      const t = setTimeout(() => setCountdown(c => c - 1), 1000)
      return () => clearTimeout(t)
    }
  }, [countdown])

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const sendOtp = async () => {
    if (!form.phone || form.phone.length < 10) return toast.error('Enter a valid phone number')
    setOtpLoading(true)
    try {
      await api.post('/otp/send', { phone: form.phone })
      toast.success('OTP sent to your phone!')
      setStep(2)
      setCountdown(60)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to send OTP')
    } finally {
      setOtpLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.otp_code) return toast.error('Enter the OTP sent to your phone')
    if (!form.pincode) return toast.error('Please select your Kolkata pincode')
    if (form.password.length < 6) return toast.error('Password must be at least 6 characters')
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', form)
      login(data.access_token, data.user)
      toast.success(`Welcome to Community Hero, ${data.user.name}!`)
      navigate('/feed')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card card fade-in" style={{ maxWidth: 480 }}>
        <div className="auth-header">
          <div className="auth-emoji">🏙️</div>
          <h1>Join Community Hero</h1>
          <p>Help make Kolkata a better city</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label>Full Name</label>
            <input className="input-field" type="text" placeholder="Rahul Banerjee" value={form.name} onChange={set('name')} required />
          </div>

          <div className="input-group">
            <label>Email Address</label>
            <input className="input-field" type="email" placeholder="rahul@email.com" value={form.email} onChange={set('email')} required />
          </div>

          <div className="input-group">
            <label>Phone Number</label>
            <div className="phone-row">
              <span className="phone-prefix">+91</span>
              <input
                className="input-field"
                type="tel"
                placeholder="9876543210"
                value={form.phone}
                onChange={set('phone')}
                maxLength={10}
                required
              />
              <button type="button" className="btn btn-outline btn-sm" onClick={sendOtp} disabled={otpLoading || countdown > 0}>
                {otpLoading ? <span className="spinner spinner-dark" style={{ width: 14, height: 14 }} /> : countdown > 0 ? `${countdown}s` : step === 2 ? 'Resend' : 'Send OTP'}
              </button>
            </div>
          </div>

          {step === 2 && (
            <div className="input-group fade-in">
              <label>OTP Code <span className="otp-hint">(sent to +91 {form.phone})</span></label>
              <input className="input-field otp-input" type="text" placeholder="6-digit OTP" value={form.otp_code} onChange={set('otp_code')} maxLength={6} inputMode="numeric" />
            </div>
          )}

          <div className="input-group">
            <label>Kolkata Pincode</label>
            <select className="input-field" value={form.pincode} onChange={set('pincode')} required>
              <option value="">— Select your area pincode —</option>
              {pincodes.map(p => (
                <option key={p.pincode} value={p.pincode}>
                  {p.pincode} — {p.area}
                </option>
              ))}
            </select>
          </div>

          {form.pincode && (
            <div className="pincode-info fade-in">
              📍 Your reports will go to: <strong>
                {pincodes.find(p => p.pincode === form.pincode)?.police_station}
              </strong>
            </div>
          )}

          <div className="input-group">
            <label>Password</label>
            <input className="input-field" type="password" placeholder="Min 6 characters" value={form.password} onChange={set('password')} required minLength={6} />
          </div>

          <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading || step !== 2}>
            {loading ? <span className="spinner" /> : 'Create Account'}
          </button>

          {step !== 2 && (
            <p className="otp-note">Verify your phone number with OTP before creating your account.</p>
          )}
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}
