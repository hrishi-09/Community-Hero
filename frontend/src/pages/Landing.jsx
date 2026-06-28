import { Link } from 'react-router-dom'
import { MapPin, AlertTriangle, CheckCircle, Users, TrendingUp } from 'lucide-react'
import './Landing.css'

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-inner page-container">
          <div className="hero-badge"><MapPin size={14} /> Kolkata Only</div>
          <h1>Your City. Your Voice.<br /><span>Fix It Together.</span></h1>
          <p>Report potholes, water leakages, damaged streetlights, and other community issues directly to your local police station — with photos, location, and real-time tracking.</p>
          <div className="hero-actions">
            <Link to="/register" className="btn btn-primary btn-lg">Get Started Free</Link>
            <Link to="/login" className="btn btn-outline btn-lg">Already a member?</Link>
          </div>
        </div>
      </section>

      <section className="features page-container">
        <div className="features-grid">
          {[
            { icon: <AlertTriangle size={28} color="#dc2626" />, title: "Report Issues", desc: "Post photos, videos & text about local problems. Select your Kolkata pincode before posting." },
            { icon: <MapPin size={28} color="#1a56db" />, title: "Pincode-Based", desc: "Issues are routed to the correct police station for your area automatically." },
            { icon: <CheckCircle size={28} color="#16a34a" />, title: "Track Resolution", desc: "Watch your report go from Pending 🔴 to Resolved 🟢 with admin proof photos." },
            { icon: <Users size={28} color="#7c3aed" />, title: "Community Upvotes", desc: "Neighbours can upvote issues to push urgent problems to the top." },
          ].map((f, i) => (
            <div key={i} className="feature-card card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="cta page-container">
        <div className="cta-inner card">
          <TrendingUp size={36} color="var(--brand)" />
          <h2>Making Kolkata Better, One Report at a Time</h2>
          <p>Join citizens across all 80+ Kolkata pincodes to create a cleaner, safer, better-maintained city.</p>
          <Link to="/register" className="btn btn-primary btn-lg">Join the Community</Link>
        </div>
      </section>
    </div>
  )
}
