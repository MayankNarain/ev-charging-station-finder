# ⚡ EV Smart Charge App

A progressive, mobile-first web application that helps Electric Vehicle (EV) owners find the **optimal charging station** nearby using real-time data, smart scoring algorithms, and live traffic-aware recommendations.

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🌟 Features

### 🔐 Authentication
- Email, Vehicle Number & Unique ID based login
- CAPTCHA verification with refresh capability
- Personalized experience using email-derived username

### 🚗 Vehicle Onboarding
- Support for **6 major EV brands**: Tata, MG, Hyundai, Mahindra, Kia, BYD
- Model-specific range data for accurate estimations
- Searchable vehicle catalog with brand logos

### 🗺️ Interactive Map
- **Live GPS tracking** with real-time position updates
- Dynamic **range circle** based on battery level & vehicle specs
- OpenStreetMap tiles via Leaflet.js
- Smooth pan, zoom, and tile rendering

### 📍 Smart Station Discovery
- **Color-coded pin system**:

  | Pin Color | Meaning |
  |-----------|---------|
  | 🟢 Green | Available — connectors operational |
  | 🟡 Gold (★) | **Smart Choice** — best score for distance + availability |
  | 🟠 Orange (⚠) | High inbound traffic warning |
  | ⚫ Gray | Busy / Offline |

### 🧠 Smart Scoring Algorithm
The app ranks every station using a proprietary scoring formula:
- **Distance Factor**: Closer stations score higher
- **Availability Factor**: More free connectors = higher score
- **Congestion Penalty**: More inbound drivers = lower score
- The station with the **highest score** gets the ⭐ **Smart Choice** badge

### 🧭 Turn-by-Turn Navigation
- In-app routing powered by **Leaflet Routing Machine**
- Blue route line with auto-fit to viewport
- Sliding info panel that repositions during navigation
- One-tap route clearing

### 📊 Station Details
- Station name, address, distance, and live status
- **Connector breakdown**: type, speed (kW), price, and availability
- **Traffic metrics**: estimated wait time & inbound user count
- Amenity listings (Restroom, Cafe, etc.)
- Smart Choice / High Traffic banners

### 📡 Offline Detection
- Automatic network status monitoring
- Full-screen overlay popup when connection is lost
- Auto-recovery when connection is restored

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **HTML5** | App structure & semantics |
| **Tailwind CSS** (CDN) | Utility-first responsive styling |
| **Vanilla JavaScript** | App logic, state management, API calls |
| **Leaflet.js** | Interactive map rendering |
| **Leaflet Routing Machine** | Turn-by-turn directions |
| **OpenChargeMap API** | Real-time EV charging station data |
| **OpenStreetMap** | Map tile provider |

---

Future Roadmap
 Backend Integration — Real inbound user tracking with Firebase/Supabase
 User Accounts — Persistent login with OAuth (Google Sign-In)
 Payment Gateway — In-app charging session payments
 Slot Booking — Reserve a charger ahead of arrival
 Push Notifications — Alerts when a nearby station becomes free
 Battery Estimation AI — ML-based range prediction using driving patterns
 Multi-language Support — Hindi, Tamil, Telugu, and more
 Dark Mode — Eye-friendly night theme
 PWA Support — Install as a native-like app on mobile
