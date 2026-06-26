# ClimateTwin India 🌏
## AI-Powered Digital Twin of India's Climate System

[![ISRO Hackathon](https://img.shields.io/badge/ISRO-Bharatiya_Antariksh_Hackathon_2024-orange)](https://www.isro.gov.in)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black)](https://nextjs.org)
[![PyTorch](https://img.shields.io/badge/AI-PyTorch_+_scikit--learn-EE4C2C)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

> A continuously evolving virtual replica of India's climate system — integrating IMD, INSAT-3D, and MOSDAC satellite data with deep learning AI to predict, simulate, and visualize climate conditions across all 30 Indian states in real time.

---

## 📸 Dashboard Preview

| Feature | Description |
|---------|-------------|
| 🖥️ **Mission Dashboard** | Real-time overview of all Indian states with KPIs and alert panel |
| 📡 **Live Climate Monitor** | Sortable table of current climate parameters across all regions |
| 🗺️ **GIS Map** | Interactive Leaflet map with temperature, rainfall, flood risk, and drought layers |
| 🔭 **AI Forecast** | 1/3/7-day climate forecasts with confidence intervals from LSTM models |
| ⏪ **Historical Replay** | Animated time-series playback with statistical summary |
| 🧪 **What-if Simulator** | IPCC-aligned scenario simulation with cascading effect computation |
| 🤖 **AI Predictions** | Model performance dashboard with architecture details |
| 📊 **Analytics** | Model comparison, regional analysis, and trend charts |
| 💬 **AI Assistant** | Natural language climate Q&A (LLM-ready plug-in point) |
| 🗄️ **Dataset Catalog** | Browse integrated national data sources with metadata |

---

## 🏗️ Architecture

```
ClimateTwin India
├── backend/                     # FastAPI + Async SQLAlchemy + PostGIS
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── core/                # Config, security, logging
│   │   ├── db/                  # Session, models (PostGIS-enabled)
│   │   ├── routes/              # API endpoints (9 modules)
│   │   ├── services/            # Digital Twin Engine, Mock Data, Scheduler
│   │   └── repositories/       # DB operations per domain
│   └── alembic/                 # DB migrations
│
├── ai/                          # AI/ML module
│   ├── datasets/                # IMD, INSAT, MOSDAC loaders (with plug-in points)
│   ├── preprocessing/           # Feature engineering, normalization
│   ├── models/                  # LSTM, GRU, Random Forest models
│   ├── training/                # Training pipelines with early stopping
│   └── evaluation/              # Metrics (MAE, RMSE, R², Skill Score)
│
├── frontend/                    # Next.js 14 + Tailwind CSS
│   └── src/
│       ├── app/                 # App router pages (9 dashboard pages)
│       ├── components/          # Reusable UI components
│       └── lib/                 # API client, design constants
│
└── docker-compose.yml           # Full infrastructure (DB, Redis, API, Frontend)
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker + Docker Compose (optional, for full stack)

### Option 1: Full Stack with Docker

```bash
# Clone and start everything
git clone <repo>
cd ClimateTwin

# Copy environment variables
cp .env.example .env

# Start all services (PostgreSQL, Redis, Backend API, Frontend)
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env

# Run backend (development mode — no DB required, uses mock data)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Access at: http://localhost:3000

---

## 🔌 Connecting Real Data Sources

### IMD Data (NetCDF)
```python
# In ai/datasets/imd_loader.py
loader = IMDDataLoader(
    source="netcdf",               # Switch from "mock"
    data_path=Path("/data/imd/")   # Directory with .nc files
)
```

### INSAT-3D / MOSDAC (HDF5)
```python
# In ai/datasets/insat_loader.py
loader = INSATDataLoader(
    source="hdf5",
    data_path=Path("/data/mosdac/"),   # Directory with 3RIMG_*.h5 files
    mosdac_token="your-mosdac-token"
)
```

### AI Assistant → Real LLM
```python
# In backend/app/services/ai_assistant_service.py
# Replace _mock_response() with:
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
response = model.generate_content(prompt)
```

---

## 🤖 AI Models

### LSTM Climate Prediction
- **Input:** 30-day sequence of IMD climate parameters
- **Architecture:** 2-layer LSTM (128 hidden) + LayerNorm + Dropout (0.2)
- **Features:** Lag (1,3,7,14,30d), rolling stats, seasonal encodings (sin/cos)
- **Targets:** Rainfall (mm), Temperature (°C)

### Random Forest Baseline
- **Algorithm:** Random Forest (200 trees) / Gradient Boosting
- **Features:** 30+ engineered tabular features
- **Purpose:** Fast inference, feature importance, ensemble member

### Training
```bash
cd ai
# Train both models for Kerala (uses mock data by default)
python -m training.run_training --region Kerala --target rainfall --model lstm
python -m training.run_training --region Kerala --target temperature --model rf
```

---

## 📊 API Reference

Full interactive docs available at: http://localhost:8000/docs

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/climate/summary` | India-level summary statistics |
| `GET /api/v1/climate/current` | All regional climate states |
| `GET /api/v1/climate/timeseries/{id}` | Historical time series |
| `GET /api/v1/climate/alerts` | Active climate alerts |
| `GET /api/v1/twin/states` | Digital twin virtual states |
| `POST /api/v1/simulation/run` | What-if scenario simulation |
| `GET /api/v1/forecast/{id}` | AI-generated forecasts |
| `GET /api/v1/analytics/model-performance` | Model evaluation metrics |
| `POST /api/v1/assistant/chat` | AI climate assistant |

---

## 🧪 Data Sources

| Source | Organization | Parameters | Format | Status |
|--------|-------------|------------|--------|--------|
| IMD Gridded Data | India Meteorological Department | Temperature, Rainfall | NetCDF | Mock → Real |
| INSAT-3D | ISRO / SAC | LST, SST, Precipitation | HDF5 | Plug-in ready |
| MOSDAC | SAC / ISRO | Satellite products | HDF5 | Plug-in ready |
| ERA5 | ECMWF | Reanalysis | NetCDF | Future |
| CMIP6 | World Climate Research | Future projections | NetCDF | Future |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, Tailwind CSS, Recharts, React Leaflet |
| **Backend** | FastAPI, Python 3.11, Async SQLAlchemy |
| **Database** | PostgreSQL 15 + PostGIS 3.4 |
| **Cache** | Redis |
| **AI/ML** | PyTorch, scikit-learn, NumPy, Pandas |
| **GIS** | Leaflet.js, CartoDB tiles |
| **Containerization** | Docker, Docker Compose |
| **Migrations** | Alembic |

---

## 📁 Project Status

This is a **Proof of Concept** for ISRO's Bharatiya Antariksh Hackathon 2024.

- ✅ Complete backend API (FastAPI)
- ✅ Digital Twin Engine (30 states)
- ✅ AI prediction models (LSTM + Random Forest)
- ✅ Full frontend dashboard (9 pages)
- ✅ GIS climate maps
- ✅ What-if simulation engine
- ✅ Docker deployment
- 🔌 Real IMD/INSAT data: plug-in ready
- 🔌 LLM integration: plug-in ready

---

## 📝 License

MIT License — Built for ISRO Bharatiya Antariksh Hackathon 2024
