# WoWYashus - Ways of Working Assessment Tool

**A gamified SPA for marketing assessment and AI-powered roadmap generation**

## 🎯 Project Overview

WoWYashus is a professional Single Page Application (SPA) that guides users through a 9-milestone marketing assessment journey, visualized as a Monopoly-style game board. The application collects business data, analyzes it using AI, and generates a personalized marketing roadmap.

### Key Features

- **🎮 Gamified Experience:** Monopoly-style board with 9 milestone properties
- **📝 9-Step Assessment:** Comprehensive marketing evaluation wizard
- **🤖 AI Analysis:** Groq API integration for intelligent insights
- **📊 Statistical Modeling:** Benchmark scoring and market analysis
- **🎯 Actionable Roadmap:** Prioritized recommendations based on user data
- **📧 Email Delivery:** Send personalized reports to users

## 🏗️ Architecture

### Frontend (Vanilla JS SPA)
- **Landing Page:** Value proposition with call-to-action
- **Monopoly Board:** Visual progress tracking with 9 milestone properties
- **Wizard Forms:** 9 milestone assessment forms
- **Dashboard:** AI insights, statistics charts, and roadmap

### Backend (Python FastAPI)
- **REST API:** Milestone submission, analysis, email delivery
- **Mock AI Engine:** Placeholder for Groq API integration
- **In-memory Storage:** (Replace with SQLite/PostgreSQL in production)

### Design System
- **Colors:** Golden theme (#fbbf24, #f59e0b, #fb923c)
- **Effects:** Glassmorphism, 3D transforms, shimmer animations
- **Typography:** Bold weights, gradient text effects
- **Responsive:** Mobile-first with breakpoints

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Modern web browser

### Installation

1. **Clone and Navigate:**
```bash
cd /workspaces/TeamAI/WoWYashus
```

2. **Install Backend Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start Backend Server:**
```bash
python main.py
# Runs on http://localhost:8000
```

4. **Start Frontend Server:**
```bash
cd ../frontend
python3 -m http.server 8082
# Runs on http://localhost:8082
```

5. **Open in Browser:**
```
http://localhost:8082
```

## 📁 Project Structure

```
WoWYashus/
├── frontend/
│   ├── index.html              # Main SPA structure (12 panes)
│   ├── css/
│   │   ├── base.css            # Global styles, theme, typography
│   │   ├── monopoly.css        # Board layout, properties, corners
│   │   └── wizard.css          # Forms, dashboard, transitions
│   ├── js/
│   │   ├── app.js              # State management, API calls
│   │   ├── wizard.js           # Navigation, form handling
│   │   └── monopoly.js         # Board interactions, animations
│   └── assets/                 # Images, icons (future)
├── backend/
│   ├── main.py                 # FastAPI application
│   └── requirements.txt        # Python dependencies
├── database/                   # SQLite schema (future)
└── README.md                   # This file
```

## 🎨 Design Highlights

### Landing Page
- Hero section with brand logo ("Yashus WoW")
- 3 value cards (AI Analysis, Statistics, Roadmap)
- Call-to-action button to start journey

### Monopoly Board
- **4 Corners:** START, INSIGHTS, ANALYSIS, FINISH
- **9 Properties:** Color-coded milestone cards
- **Center:** WoW logo + progress tracker (0/9 → 9/9)
- **Interactions:** Click properties to navigate, hover for tooltips

### Milestone Forms
- Industry selection dropdown
- Product description textarea (500 char limit)
- Target audience input
- Character counters
- Auto-save to localStorage
- Skip option for flexibility

### Dashboard
- **AI Insights:** 3-5 personalized recommendations
- **Statistics Chart:** 4 benchmark scores (bar graphs)
- **Roadmap:** 5-7 prioritized action items
- **Email Form:** Capture lead and send report

## 🔌 API Endpoints

### Backend Routes

#### `GET /`
Health check endpoint
```json
{
  "message": "WoWYashus API",
  "version": "1.0.0",
  "status": "running"
}
```

#### `POST /api/milestones/{milestone_number}`
Submit milestone form data
```json
{
  "milestone_number": 1,
  "data": {
    "m1-industry": "SaaS",
    "m1-product": "AI-powered analytics platform",
    "m1-target": "B2B marketers"
  }
}
```

#### `POST /api/analyze`
Generate AI analysis from all milestones
```json
{
  "milestones": {
    "1": { "m1-industry": "SaaS", ... },
    "2": { "m2-market": "Enterprise", ... }
  }
}
```

#### `POST /api/send-report`
Email personalized report to user
```json
{
  "email": "user@example.com",
  "milestones": { ... },
  "analysis": { ... }
}
```

## 🧪 Testing

### Manual Testing Workflow

1. **Landing Page:**
   - Verify hero text and value cards display
   - Click "Start Journey" button

2. **Monopoly Board:**
   - Confirm 4 corners + 9 properties render
   - Check center WoW logo and 0/9 progress
   - Click property 1 to navigate

3. **Milestone 1 Form:**
   - Fill industry, product, target fields
   - Verify character counter updates
   - Submit form and confirm navigation to Milestone 2

4. **Complete All 9 Milestones:**
   - Fill all forms (or skip some)
   - Return to Monopoly board
   - Verify completed properties show checkmark
   - Progress bar should update

5. **Dashboard:**
   - Check AI insights render
   - Verify statistics bars animate
   - Confirm roadmap items display
   - Enter email and click "Send Report"

### Frontend-Only Testing
The app works 100% offline using:
- LocalStorage for data persistence
- Mock API responses in `app.js`
- No backend required for basic functionality

## 🚧 Future Enhancements

### Phase 2 (Backend Integration)
- [ ] SQLite database schema
- [ ] Groq API integration for real AI insights
- [ ] Statistical models (scipy, statsmodels)
- [ ] Monte Carlo simulations
- [ ] Email delivery (SMTP/SendGrid)

### Phase 3 (Advanced Features)
- [ ] User authentication
- [ ] Save/resume sessions
- [ ] Export PDF reports
- [ ] Admin dashboard
- [ ] A/B testing framework
- [ ] Multi-language support

### Phase 4 (Production Readiness)
- [ ] Unit tests (Jest, pytest)
- [ ] E2E tests (Playwright)
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] Azure deployment
- [ ] CDN for static assets
- [ ] Analytics tracking

## 🎯 Business Value

### For Yashus (Company)
- **Lead Generation:** Email capture at end of assessment
- **Differentiation:** Unique "Ways of Working" assessment
- **Credibility:** AI-powered insights demonstrate expertise
- **Scalability:** Self-service tool reduces sales cycle time

### For Users (Marketing Teams)
- **Free Assessment:** No payment required for insights
- **Immediate Value:** Personalized roadmap in minutes
- **Engaging UX:** Game-like experience vs boring forms
- **Actionable Output:** Clear next steps, not generic advice

## 📊 Success Metrics

- **Completion Rate:** % of users finishing all 9 milestones
- **Time to Complete:** Average duration (target: 15-20 minutes)
- **Email Capture Rate:** % providing email for report
- **Bounce Rate:** % leaving without starting assessment
- **Return Visits:** % coming back to finish incomplete assessment

## 🤝 Contributing

This is a demo/MVP project. For production use:
1. Replace mock API with real Groq integration
2. Add proper database (PostgreSQL recommended)
3. Implement email service
4. Add unit tests
5. Set up CI/CD pipeline

## 📝 License

MIT License - See LICENSE file

## 🙋 Support

For questions or issues:
- Open an issue in GitHub
- Contact: Yashus team

---

**Built with ❤️ by Yashus - Demonstrating Ways of Working (WoW)**
