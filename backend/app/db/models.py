"""
Database models for Community Hero
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, Boolean,
    ForeignKey, Float, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from backend.app.db.database import Base


class UserRole(str, enum.Enum):
    citizen = "citizen"
    admin = "admin"
    police = "police"


class IssueStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"


class IssueCategory(str, enum.Enum):
    pothole = "Pothole"
    water_leakage = "Water Leakage"
    streetlight = "Streetlight"
    garbage = "Garbage / Waste"
    drainage = "Drainage Blockage"
    road_damage = "Road Damage"
    illegal_parking = "Illegal Parking"
    tree_fall = "Tree Fall"
    electricity = "Electricity Issue"
    other = "Other"


# Kolkata Pin Codes with police station mappings
KOLKATA_PINCODES = [
    {"pincode": "700001", "area": "BBD Bag / Dalhousie", "police_station": "Hare Street Police Station"},
    {"pincode": "700002", "area": "Shyambazar / Shobhabazar", "police_station": "Shyambazar Police Station"},
    {"pincode": "700003", "area": "Chitpur / Jorasanko", "police_station": "Jorasanko Police Station"},
    {"pincode": "700004", "area": "Sovabazar", "police_station": "Sovabazar Police Station"},
    {"pincode": "700005", "area": "Manicktala", "police_station": "Manicktala Police Station"},
    {"pincode": "700006", "area": "Entally / Beniapukur", "police_station": "Entally Police Station"},
    {"pincode": "700007", "area": "Amherst Street / Bowbazar", "police_station": "Bowbazar Police Station"},
    {"pincode": "700008", "area": "Tiretti Bazaar / Burrabazar", "police_station": "Jorabagan Police Station"},
    {"pincode": "700009", "area": "Girish Park / Shyampukur", "police_station": "Shyampukur Police Station"},
    {"pincode": "700010", "area": "Kasba / Gariahat", "police_station": "Gariahat Police Station"},
    {"pincode": "700011", "area": "Taltala / Sealdah", "police_station": "Taltala Police Station"},
    {"pincode": "700012", "area": "College Street / Hedua", "police_station": "College Street Police Station"},
    {"pincode": "700013", "area": "Beliaghata", "police_station": "Beliaghata Police Station"},
    {"pincode": "700014", "area": "Rajabazar / Narkeldanga", "police_station": "Narkeldanga Police Station"},
    {"pincode": "700015", "area": "Bhowanipore / Hazra", "police_station": "Bhowanipore Police Station"},
    {"pincode": "700016", "area": "Rashbehari / Ballygunge", "police_station": "Ballygunge Police Station"},
    {"pincode": "700017", "area": "Park Street / Camac Street", "police_station": "Park Street Police Station"},
    {"pincode": "700018", "area": "Kalighat / Chetla", "police_station": "Kalighat Police Station"},
    {"pincode": "700019", "area": "Alipore / Zoo", "police_station": "Alipore Police Station"},
    {"pincode": "700020", "area": "Ekbalpore / Metiabruz", "police_station": "Metiabruz Police Station"},
    {"pincode": "700022", "area": "Tollygunge / Regent Park", "police_station": "Tollygunge Police Station"},
    {"pincode": "700023", "area": "Elgin / New Alipore", "police_station": "New Alipore Police Station"},
    {"pincode": "700024", "area": "Watgunge / Khidderpore", "police_station": "Watgunge Police Station"},
    {"pincode": "700025", "area": "Garden Reach", "police_station": "Garden Reach Police Station"},
    {"pincode": "700026", "area": "Naktala / Regent Estate", "police_station": "Naktala Police Station"},
    {"pincode": "700027", "area": "Netaji Nagar / Jadavpur", "police_station": "Jadavpur Police Station"},
    {"pincode": "700028", "area": "Dhakuria / Lake Gardens", "police_station": "Lake Police Station"},
    {"pincode": "700029", "area": "Kidderpore / Shibpur", "police_station": "Kidderpore Police Station"},
    {"pincode": "700030", "area": "Behala Chowrasta", "police_station": "Behala Police Station"},
    {"pincode": "700031", "area": "Sarsuna / Barisha", "police_station": "Sarsuna Police Station"},
    {"pincode": "700032", "area": "Parnasree / Joka", "police_station": "Joka Police Station"},
    {"pincode": "700033", "area": "Thakurpukur", "police_station": "Thakurpukur Police Station"},
    {"pincode": "700034", "area": "New Town / Rajarhat", "police_station": "Rajarhat Police Station"},
    {"pincode": "700035", "area": "Phoolbagan / Ultadanga", "police_station": "Phoolbagan Police Station"},
    {"pincode": "700036", "area": "Baguiati / VIP Road", "police_station": "Baguiati Police Station"},
    {"pincode": "700037", "area": "Tangra / Tiljala", "police_station": "Tiljala Police Station"},
    {"pincode": "700039", "area": "Santoshpur", "police_station": "Santoshpur Police Station"},
    {"pincode": "700040", "area": "Narendrapur", "police_station": "Narendrapur Police Station"},
    {"pincode": "700041", "area": "Garia / Panchasayar", "police_station": "Garia Police Station"},
    {"pincode": "700042", "area": "Sonarpur", "police_station": "Sonarpur Police Station"},
    {"pincode": "700043", "area": "Dum Dum / Airport", "police_station": "Dum Dum Airport Police Station"},
    {"pincode": "700044", "area": "Dum Dum Cantonment", "police_station": "Dum Dum Police Station"},
    {"pincode": "700045", "area": "Noapara / Baranagar", "police_station": "Baranagar Police Station"},
    {"pincode": "700046", "area": "Dunlop / Bonhooghly", "police_station": "Bonhooghly Police Station"},
    {"pincode": "700047", "area": "Shyamnagar / Sinthee", "police_station": "Sinthee Police Station"},
    {"pincode": "700048", "area": "Bidhannagar / Salt Lake", "police_station": "Bidhannagar Police Station"},
    {"pincode": "700052", "area": "Belgharia", "police_station": "Belgharia Police Station"},
    {"pincode": "700053", "area": "Agarpara", "police_station": "Agarpara Police Station"},
    {"pincode": "700054", "area": "Khardah", "police_station": "Khardah Police Station"},
    {"pincode": "700055", "area": "Sodepur", "police_station": "Sodepur Police Station"},
    {"pincode": "700056", "area": "Panihati", "police_station": "Panihati Police Station"},
    {"pincode": "700057", "area": "Titagarh", "police_station": "Titagarh Police Station"},
    {"pincode": "700058", "area": "Kamarhati", "police_station": "Kamarhati Police Station"},
    {"pincode": "700059", "area": "Madhyamgram", "police_station": "Madhyamgram Police Station"},
    {"pincode": "700060", "area": "Barasat", "police_station": "Barasat Police Station"},
    {"pincode": "700063", "area": "Lake Town / Kestopur", "police_station": "Lake Town Police Station"},
    {"pincode": "700064", "area": "Kaikhali / Dum Dum Park", "police_station": "Kaikhali Police Station"},
    {"pincode": "700065", "area": "Bangur / Nagerbazar", "police_station": "Nagerbazar Police Station"},
    {"pincode": "700067", "area": "Belur Math / Liluah", "police_station": "Liluah Police Station"},
    {"pincode": "700068", "area": "Shibpur / Howrah", "police_station": "Shibpur Police Station"},
    {"pincode": "700070", "area": "Topsia / Tiljala", "police_station": "Topsia Police Station"},
    {"pincode": "700071", "area": "Giridhari / Kasba", "police_station": "Kasba Police Station"},
    {"pincode": "700072", "area": "Mukundapur / EM Bypass", "police_station": "Mukundapur Police Station"},
    {"pincode": "700073", "area": "Science City / Action Area", "police_station": "New Town Police Station"},
    {"pincode": "700075", "area": "Pattipukur / Nimta", "police_station": "Nimta Police Station"},
    {"pincode": "700078", "area": "Patuli / Anandapur", "police_station": "Purba Jadavpur Police Station"},
    {"pincode": "700080", "area": "Barisha / Behala", "police_station": "Barisha Police Station"},
    {"pincode": "700082", "area": "Dum Dum Park / Bangur", "police_station": "Dum Dum Park Police Station"},
    {"pincode": "700084", "area": "Kankurgachi / Ultadanga", "police_station": "Ultadanga Police Station"},
    {"pincode": "700086", "area": "Golfgreen / Naktala", "police_station": "Golfgreen Police Station"},
    {"pincode": "700088", "area": "Bansdroni / Regent Park", "police_station": "Bansdroni Police Station"},
    {"pincode": "700089", "area": "Bosepukur / Kasba", "police_station": "Bosepukur Police Station"},
    {"pincode": "700090", "area": "Andul Road / Santragachi", "police_station": "Santragachi Police Station"},
    {"pincode": "700091", "area": "Subhasgram / Baruipur", "police_station": "Baruipur Police Station"},
    {"pincode": "700092", "area": "Baghajatin / Jodhpur Park", "police_station": "Jodhpur Park Police Station"},
    {"pincode": "700094", "area": "Beleghata / Lake Town", "police_station": "Beleghata Police Station"},
    {"pincode": "700095", "area": "Hridaypur / Barasat", "police_station": "Hridaypur Police Station"},
    {"pincode": "700097", "area": "New Alipore / Behala", "police_station": "New Alipore Police Station"},
    {"pincode": "700099", "area": "Paschim Putiari", "police_station": "Paschim Putiari Police Station"},
    {"pincode": "700101", "area": "Action Area I / New Town", "police_station": "New Town Police Station"},
    {"pincode": "700102", "area": "Action Area II / Rajarhat", "police_station": "Rajarhat New Town Police Station"},
    {"pincode": "700103", "area": "Action Area III / Eco Park", "police_station": "Eco Park Police Station"},
    {"pincode": "700104", "area": "Joka / Thakurpukur (South)", "police_station": "Joka Police Station"},
    {"pincode": "700105", "area": "Subhashgram / Rajpur", "police_station": "Rajpur Police Station"},
    {"pincode": "700107", "area": "Narayanpur / Haridevpur", "police_station": "Haridevpur Police Station"},
    {"pincode": "700108", "area": "Maheshtala / Budge Budge", "police_station": "Maheshtala Police Station"},
]


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.citizen, nullable=False)
    pincode = Column(String(10), nullable=True)  # Admin's assigned pincode
    area = Column(String(200), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    is_verified = Column(Boolean, default=False)  # Phone verified
    is_active = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    points = Column(Integer, default=0)  # Gamification
    created_at = Column(DateTime, default=datetime.utcnow)

    issues = relationship("Issue", back_populates="reporter", foreign_keys="Issue.reporter_id")
    admin_actions = relationship("IssueAction", back_populates="admin")


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(15), nullable=False)
    otp_code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Issue(Base):
    __tablename__ = "issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    status = Column(SAEnum(IssueStatus), default=IssueStatus.pending, nullable=False)
    pincode = Column(String(10), nullable=False)
    area = Column(String(200), nullable=True)
    police_station = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_description = Column(String(500), nullable=True)
    media_urls = Column(Text, nullable=True)  # JSON array of URLs
    upvotes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter = relationship("User", back_populates="issues", foreign_keys=[reporter_id])
    actions = relationship("IssueAction", back_populates="issue")
    comments = relationship("Comment", back_populates="issue")
    upvote_records = relationship("IssueUpvote", back_populates="issue")


class IssueAction(Base):
    __tablename__ = "issue_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(String(36), ForeignKey("issues.id"), nullable=False)
    admin_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # "status_change", "comment", "resolved_proof"
    note = Column(Text, nullable=True)
    proof_urls = Column(Text, nullable=True)  # JSON array of proof image URLs
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="actions")
    admin = relationship("User", back_populates="admin_actions")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(String(36), ForeignKey("issues.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="comments")
    user = relationship("User")


class IssueUpvote(Base):
    __tablename__ = "issue_upvotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(String(36), ForeignKey("issues.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="upvote_records")
