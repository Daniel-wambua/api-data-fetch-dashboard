# ⚡ DataPulse Command Center

A comprehensive, production-ready dashboard that aggregates and visualizes real-time data from multiple public APIs. Built with FastAPI backend and Streamlit frontend featuring a modern, responsive design with fixed header navigation.

## � Screenshots

<div align="center">

### Dashboard Overview
![Dashboard Overview](https://github.com/Daniel-wambua/Datapulse/blob/main/images/screenshot1.png?raw=true)

### Data Visualization Interface
![Data Visualization](https://github.com/Daniel-wambua/Datapulse/blob/main/images/screenshot2.png?raw=true)

</div>

## �🚀 Features

### 📊 Dashboard Sections
- **🏠 Overview**: Key metrics and quick insights across all services
- **₿ Crypto Dashboard**: Live cryptocurrency prices, charts, and trending coins
- **🌤️ Weather**: Current weather and forecasts with interactive temperature charts
- **🌐 IP Info**: IP address lookup with geolocation mapping and ISP details
- **📈 Trending**: GitHub repos, Hacker News, and Dev.to trending content
- **📰 News**: Headlines, tech news, and cryptocurrency news aggregation
- **📊 Events**: Real-time application events and custom logging system


### 🔌 API Integrations
- **CoinGecko**: Cryptocurrency prices, market data, and trending coins
- **OpenWeatherMap**: Weather information and 5-day forecasts
- **IPInfo**: IP address geolocation and network details
- **GitHub**: Trending repositories by language and timeframe
- **Hacker News**: Top stories and trending tech discussions
- **Dev.to**: Trending developer articles and tutorials
- **NewsAPI**: Headlines and search (with free alternatives)
- **LogSnag**: Event logging and monitoring (optional)


## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/Daniel-wambua/Datapulse.git
cd api_dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional for basic functionality)
nano .env
```

### 3. Get API Keys (Optional but Recommended)

#### Required for Full Functionality:
- **OpenWeatherMap**: [Get free API key](https://openweathermap.org/api) (50,000 calls/month free)
- **IPInfo**: [Get free API key](https://ipinfo.io/signup) (50,000 requests/month free)
- **NewsAPI**: [Get free API key](https://newsapi.org/register) (1,000 requests/day free)

#### Optional Enhancements:
- **GitHub Token**: [Create personal access token](https://github.com/settings/tokens) (higher rate limits)
- **LogSnag**: [Get API key](https://logsnag.com/) (event logging and monitoring)

#### Free Alternatives Included:
- CoinGecko (no key required, 10-50 calls/minute)
- Hacker News (unlimited, public API)
- Dev.to (unlimited, public API)
- Alternative news sources when NewsAPI unavailable

### 4. Run the Application

#### Option A: Run Both Services Separately (Recommended for Development)

```bash
# Start FastAPI backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Start Streamlit frontend  
streamlit run dashboard.py --server.port 8501
```

#### Option B: Using Startup Script

```bash
# Make script executable
chmod +x start.sh

# Run both services
./start.sh
```

#### Option C: Using Docker

```bash
# Build and run with Docker
docker build -t api-dashboard .
docker run -p 8000:8000 -p 8501:8501 api-dashboard

# Or use Docker Compose (recommended)
docker-compose up --build
```

### 5. Access the Dashboard

- **🖥️ Streamlit Dashboard**: http://localhost:8501
- **📚 FastAPI Documentation**: http://localhost:8000/docs
- **🔧 API Endpoints**: http://localhost:8000

## 🎯 Dashboard Navigation Guide

### Header Layout
- **Fixed Header**: ⚡ DataPulse Command Center stays at the top
- **Clean Branding**: Professional logo with gradient styling
- **No Overlap**: Navigation positioned properly below header

### Navigation Buttons
- **🏠 Overview**: Dashboard summary and key metrics
- **₿ Crypto**: Cryptocurrency prices and market data
- **🌤️ Weather**: Weather information and forecasts
- **🌐 IP Info**: IP address lookup and geolocation
- **📈 Trending**: GitHub, Hacker News, Dev.to trending content
- **📰 News**: Technology and general news headlines
- **📊 Events**: Application events and logging

### UI Improvements
- **Fixed Positioning**: Header stays at top during scrolling
- **Smart Spacing**: 160px+ gap between header and navigation
- **Visual Polish**: Gradient backgrounds, shadows, and hover effects
- **Responsive Layout**: Adapts to different screen sizes

## 📖 API Documentation

<details>
<summary><strong>🪙 Crypto Endpoints</strong> (Click to expand)</summary>
- `GET /crypto/prices` - Current cryptocurrency prices (top 10)
- `GET /crypto/history/{coin_id}` - Historical price data with charts
- `GET /crypto/trending` - Trending cryptocurrencies
- `GET /crypto/global` - Global market statistics

**Example Response:**
```json
{
  "prices": [
    {"id": "bitcoin", "name": "Bitcoin", "price": 43250.50, "change_24h": 2.34},
    {"id": "ethereum", "name": "Ethereum", "price": 2580.75, "change_24h": -1.22}
  ]
}
```
</details>

<details>
<summary><strong>🌤️ Weather Endpoints</strong> (Click to expand)</summary>

- `GET /weather/current?city={city}` - Current weather conditions
- `GET /weather/forecast?city={city}` - 5-day weather forecast
- `GET /weather/coordinates?lat={lat}&lon={lon}` - Weather by coordinates

**Example Usage:**
```bash
curl "http://localhost:8000/weather/current?city=London"
curl "http://localhost:8000/weather/forecast?city=New York"
```
</details>

<details>
<summary><strong>🌐 IP Info Endpoints</strong> (Click to expand)</summary>

- `GET /ip-info` - Current public IP information
- `GET /ip-info?ip={ip}` - Specific IP address lookup

**Example Response:**
```json
{
  "ip": "8.8.8.8",
  "city": "Mountain View",
  "region": "California",
  "country": "US",
  "org": "Google LLC"
}
```
</details>

<details>
<summary><strong>📈 Trending Endpoints</strong> (Click to expand)</summary>

- `GET /trending/github` - GitHub trending repositories
- `GET /trending/hackernews` - Hacker News top stories  
- `GET /trending/devto` - Dev.to trending articles

**Query Parameters:**
- `language` - Filter GitHub repos by programming language
- `since` - Time period (daily, weekly, monthly)
- `limit` - Number of results (default: 10)
</details>

<details>
<summary><strong>📰 News Endpoints</strong> (Click to expand)</summary>

- `GET /news/headlines` - Top news headlines
- `GET /news/search?q={query}` - Search news articles
- `GET /news/tech` - Technology news
- `GET /news/crypto` - Cryptocurrency news

**Features:**
- Real-time news aggregation
- Multiple source fallbacks
- Category filtering
- Search functionality
</details>

<details>
<summary><strong>📊 Events Endpoints</strong> (Click to expand)</summary>

- `GET /events` - Recent application events
- `POST /events/log` - Log custom event

**Event Types:**
- API calls and response times
- Error tracking and monitoring
- User interaction logging
- System performance metrics
</details>

<details>
<summary><strong>🔗 API Base URL & Authentication</strong> (Click to expand)</summary>

**Base URL:** `http://localhost:8000`

**Interactive Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Authentication:**
- Most endpoints work without authentication
- API keys are optional but provide higher rate limits
- Rate limiting: 100 requests per minute per IP
</details>

## 🔧 Configuration

### Environment Variables

```bash
# API Keys (Optional but Recommended)
OPENWEATHER_API_KEY=your_key_here        # Weather data
IPINFO_API_KEY=your_key_here             # IP geolocation  
NEWS_API_KEY=your_key_here               # News headlines
GITHUB_TOKEN=your_token_here             # Higher rate limits
LOGSNAG_API_KEY=your_key_here            # Event logging
LOGSNAG_PROJECT=your_project_name        # LogSnag project

# App Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
DEBUG=True

# Cache Configuration  
CACHE_TTL_SECONDS=300                    # 5 minutes default
```


## 🐳 Docker Deployment

### Build Image

```bash
docker build -t api-dashboard .
```

### Run Container

```bash
# Basic run
docker run -p 8000:8000 -p 8501:8501 api-dashboard

# With environment file
docker run --env-file .env -p 8000:8000 -p 8501:8501 api-dashboard

# With persistent cache volume
docker run -v ./cache:/app/cache -p 8000:8000 -p 8501:8501 api-dashboard
```



## 🚀 Production Deployment

### Cloud Deployment Options

#### 1. **Railway** (Recommended)
```bash
# Connect GitHub repo to Railway
# Automatic deployments on git push
# Environment variables via dashboard
```

#### 2. **Heroku**
```bash
# Install Heroku CLI and login
heroku create api-dashboard
heroku config:set OPENWEATHER_API_KEY=your_key
git push heroku main
```

#### 3. **DigitalOcean App Platform**
```yaml
name: api-dashboard
services:
- name: web
  source_dir: /
  github:
    repo: your-username/api-dashboard
    branch: main
  run_command: ./start.sh
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  ports:
  - http_port: 8501
    name: streamlit
  - http_port: 8000
    name: fastapi
```

### Performance Optimization

#### Backend Optimizations
- **Async Operations**: All API calls use httpx async client
- **Connection Pooling**: Efficient HTTP connection reuse
- **Caching Strategy**: Smart TTL-based caching reduces API calls
- **Error Handling**: Graceful degradation when services unavailable

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/Daniel-wambua/Datapulse.git
cd api_dashboard

# Create feature branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements.txt

# Make changes and test
python test_setup.py  # Verify setup

# Commit and push
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

### Adding New API Services

1. **Create Service Module**: Add to `services/` directory
2. **Follow Patterns**: Use existing services as templates
3. **Add Caching**: Implement TTL-based caching
4. **Error Handling**: Include try/catch and fallbacks
5. **API Endpoints**: Add FastAPI endpoints in `app.py`
6. **UI Components**: Add dashboard section in `dashboard.py`
7. **Documentation**: Update README and API docs

## 📊 Monitoring and Analytics

### Health Checks
- **API Status**: All endpoints include health monitoring
- **Database**: Cache database connectivity verification
- **External APIs**: Availability monitoring for all services
- **Performance**: Response time tracking


## 🙏 Acknowledgments

- **CoinGecko**: Comprehensive cryptocurrency data API
- **OpenWeatherMap**: Reliable weather information service  
- **IPInfo**: Accurate IP geolocation services
- **GitHub API**: Repository and trending data
- **Hacker News**: Tech community discussions and stories
- **Dev.to**: Developer articles and tutorials
- **FastAPI**: High-performance async web framework
- **Streamlit**: Rapid data app development framework
- **Plotly**: Interactive data visualization library

## 📝 License

This project is licensed under the MIT LICENSE. See LICENSE file for details.

## 📞 Support and Community

### Getting Help
1. **Documentation**: Check this README and `/docs` endpoint
2. **Issues**: Create GitHub issue with detailed description
3. **Features**: Submit feature request with use case
4. **Security**: Report security issues privately

### Community
- **Discussions**: GitHub Discussions for questions
- **Contributions**: Pull requests welcome
- **Feedback**: Issues and feature requests appreciated

---

## 🌟 Recent Updates

- **Responsive Layout**: Works on all screen sizes
- **Performance**: Optimized CSS and resource loading

---

**⭐ Star this repository if you find it useful!**

Built with ❤️ by havoc using FastAPI, Streamlit.
