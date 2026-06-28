"""
Kolkata pincode + police-station reference data for Community Hero.

NOTE ON ACCURACY (please read before going live):
- Pincode -> area names are compiled from public India Post pincode directories.
- The "police_station" label is an INDICATIVE, pincode-keyed name generated for
  this MVP so that every pincode has exactly one admin account to route reports
  to. It has NOT been verified turn-by-turn against official Kolkata Police
  jurisdiction boundaries, which can differ from postal pincode boundaries.
  Before any real deployment, cross-check and correct this list against
  https://www.kolkatapolice.gov.in (or your local police HQ) and treat this
  file as a starting seed, not a legal source of truth.
"""

KOLKATA_PINCODES = [
    # (pincode, area / locality label, indicative police station label)
    ("700001", "BBD Bagh / Lalbazar", "Hare Street Police Station"),
    ("700007", "Barabazar", "Jorabagan Police Station"),
    ("700008", "Barisha", "Behala Police Station"),
    ("700009", "Raja Ram Mohan Sarani", "Jorasanko Police Station"),
    ("700010", "Beleghata", "Beleghata Police Station"),
    ("700011", "Narkeldanga", "Phoolbagan Police Station"),
    ("700012", "Bowbazar", "Bowbazar Police Station"),
    ("700013", "Dharmatala", "New Market Police Station"),
    ("700014", "Sealdah / Taltala", "Taltala Police Station"),
    ("700015", "Tangra", "Tangra Police Station"),
    ("700016", "Park Street", "Park Street Police Station"),
    ("700017", "Park Circus", "Beniapukur Police Station"),
    ("700018", "Bartala / Rabindra Nagar", "Ekbalpore Police Station"),
    ("700019", "Ballygunge", "Ballygunge Police Station"),
    ("700020", "A.J.C. Bose Road", "Karaya Police Station"),
    ("700021", "Fort William", "Maidan Police Station"),
    ("700022", "Hastings", "Hastings Police Station"),
    ("700023", "Khidirpore", "Watgunge Police Station"),
    ("700024", "Garden Reach", "Garden Reach Police Station"),
    ("700025", "Bhawanipore", "Bhawanipore Police Station"),
    ("700026", "Kalighat", "Kalighat Police Station"),
    ("700027", "Alipore / Chetla", "Alipore Police Station"),
    ("700028", "Dum Dum", "Dum Dum Police Station"),
    ("700029", "Lake Market / Dover Lane", "Lake Police Station"),
    ("700031", "Dhakuria", "Lake Police Station"),
    ("700032", "Jadavpur", "Jadavpur Police Station"),
    ("700033", "Tollygunge", "Tollygunge Police Station"),
    ("700034", "Behala", "Behala Police Station"),
    ("700038", "Sahapur", "Tollygunge Police Station"),
    ("700039", "Tiljala", "Tiljala Police Station"),
    ("700040", "Regent Park / Russa", "Regent Park Police Station"),
    ("700041", "Paschim Putiari", "Haridevpur Police Station"),
    ("700042", "Kasba", "Kasba Police Station"),
    ("700043", "Sonai", "Garden Reach Police Station"),
    ("700044", "Badartala", "Garden Reach Police Station"),
    ("700045", "Lake Gardens", "Lake Police Station"),
    ("700046", "Topsia / Gobinda Khatick Road", "Topsia Police Station"),
    ("700047", "Naktala / Garia", "Netaji Nagar Police Station"),
    ("700053", "New Alipore", "New Alipore Police Station"),
    ("700054", "Kankurgachi / Phulbagan", "Phoolbagan Police Station"),
    ("700060", "Parnasree", "Parnasree Police Station"),
    ("700061", "Sarsoona", "Behala Police Station"),
    ("700062", "Governor's Camp Area", "Hastings Police Station"),
    ("700063", "Thakurpukur", "Thakurpukur Police Station"),
    ("700064", "Salt Lake City (Bidhannagar)", "Bidhannagar (North) Police Station"),
    ("700066", "Bidhangarh", "Netaji Nagar Police Station"),
    ("700067", "Ultadanga", "Ultadanga Police Station"),
    ("700068", "Jodhpur Park", "Lake Police Station"),
    ("700069", "Esplanade", "New Market Police Station"),
    ("700071", "Russell Street", "Park Street Police Station"),
    ("700072", "Princep Street", "Hare Street Police Station"),
    ("700073", "Chittaranjan Avenue / Tiretta Bazar", "Jorabagan Police Station"),
    ("700075", "Santoshpur", "Survey Park Police Station"),
    ("700078", "Haltu / Jadavgarh", "Survey Park Police Station"),
    ("700082", "Haridevpur", "Haridevpur Police Station"),
    ("700084", "Garia", "Garia Police Station"),
    ("700085", "K.G. Bose Sarani", "Topsia Police Station"),
    ("700086", "Baghajatin", "Patuli Police Station"),
    ("700087", "New Market", "New Market Police Station"),
    ("700088", "Taratala", "Taratala Police Station"),
    ("700089", "Kalindi Housing Estate", "Phoolbagan Police Station"),
    ("700091", "Jadavpur (Garia side)", "Garia Police Station"),
    ("700092", "Regent Estate", "Netaji Nagar Police Station"),
    ("700094", "Panchasayar", "Purba Jadavpur Police Station"),
    ("700095", "Golf Green", "Tollygunge Police Station"),
    ("700099", "Mukundapur / Kalikapur", "Purba Jadavpur Police Station"),
    ("700102", "New Town (Action Area I)", "New Town Police Station"),
    ("700107", "East Kolkata Township (E.K.T.)", "Kasba Police Station"),
    ("700135", "Rajarhat", "Rajarhat Police Station"),
    ("700136", "New Town (Action Area II)", "New Town Police Station"),
    ("700141", "Daulatpur", "Garden Reach Police Station"),
    ("700156", "New Town (Action Area III)", "New Town Police Station"),
]
