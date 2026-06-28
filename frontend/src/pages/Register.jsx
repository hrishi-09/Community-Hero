import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'
import api from '../api'
import './Auth.css'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [pincodes, setPincodes] = useState([])
  const [loading, setLoading] = useState(false)

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    pincode: '',
  })

  useEffect(() => {
    const fetchPincodes = async () => {
      try {
        const { data } = await api.get('/otp/pincodes')
        setPincodes(data.pincodes || [])
      } catch (err) {
        console.error(err)
        toast.error('Failed to load Kolkata pincodes')
      }
    }

    fetchPincodes()
  }, [])

  const set = (key) => (e) =>
    setForm((prev) => ({
      ...prev,
      [key]: e.target.value,
    }))

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!form.name.trim()) {
      return toast.error('Please enter your full name')
    }

    if (!form.email.trim()) {
      return toast.error('Please enter your email')
    }

    if (!form.phone || form.phone.length !== 10) {
      return toast.error('Please enter a valid phone number')
    }

    if (!form.pincode) {
      return toast.error('Please select your Kolkata pincode')
    }

    if (form.password.length < 6) {
      return toast.error('Password must be at least 6 characters')
    }

    setLoading(true)

    try {
      const { data } = await api.post('/auth/register', {
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: form.password,
        pincode: form.pincode,
      })

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
      <div
        className="auth-card card fade-in"
        style={{ maxWidth: 480 }}
      >
        <div className="auth-header">
          <div className="auth-emoji">🏙️</div>

          <h1>Join Community Hero</h1>

          <p>Help make Kolkata a better city</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="auth-form"
        >
          <div className="input-group">
            <label>Full Name</label>

            <input
              className="input-field"
              type="text"
              placeholder="Rahul Banerjee"
              value={form.name}
              onChange={set('name')}
              required
            />
          </div>

          <div className="input-group">
            <label>Email Address</label>

            <input
              className="input-field"
              type="email"
              placeholder="rahul@email.com"
              value={form.email}
              onChange={set('email')}
              required
            />
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
            </div>
          </div>

          <div className="input-group">
            <label>Kolkata Pincode</label>

            <select
              className="input-field"
              value={form.pincode}
              onChange={set('pincode')}
              required
            >
              <option value="">
                — Select your area pincode —
              </option>

              {pincodes.map((p) => (
                <option
                  key={p.pincode}
                  value={p.pincode}
                >
                  {p.pincode} — {p.area}
                </option>
              ))}
            </select>
          </div>

          {form.pincode && (
            <div className="pincode-info fade-in">
              📍 Your reports will go to:{' '}
              <strong>
                {
                  pincodes.find(
                    (p) => p.pincode === form.pincode
                  )?.police_station
                }
              </strong>
            </div>
          )}

          <div className="input-group">
            <label>Password</label>

            <input
              className="input-field"
              type="password"
              placeholder="Minimum 6 characters"
              value={form.password}
              onChange={set('password')}
              minLength={6}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={loading}
          >
            {loading ? (
              <span className="spinner" />
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}
