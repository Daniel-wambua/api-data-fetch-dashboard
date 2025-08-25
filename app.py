import os
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services import (
    crypto_service,
    weather_service,
    ipinfo_service,
    trends_service,
    news_service,
    events_service
)

# Create FastAPI app
app = FastAPI(
    title="API Data Dashboard",
    description="A comprehensive dashboard API that aggregates data from multiple sources",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Log startup event"""
    await events_service.log_event(
        event="API Started",
        description="FastAPI backend server started successfully",
        icon="🚀"
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "API Data Dashboard Backend",
        "version": "1.0.0",
        "endpoints": {
            "crypto": "/crypto",
            "weather": "/weather",
            "ip-info": "/ip-info",
            "trending": "/trending",
            "news": "/news",
            "events": "/events"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Crypto endpoints
@app.get("/crypto/prices")
async def get_crypto_prices(coins: Optional[str] = Query(None, description="Comma-separated list of coin IDs")):
    """Get current cryptocurrency prices"""
    try:
        coin_list = coins.split(",") if coins else None
        data = await crypto_service.get_crypto_prices(coin_list)
        await events_service.log_api_call("crypto", "prices", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch crypto prices")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "crypto_prices")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto/history/{coin_id}")
async def get_crypto_history(coin_id: str, days: int = Query(7, ge=1, le=365)):
    """Get historical price data for a cryptocurrency"""
    try:
        data = await crypto_service.get_crypto_history(coin_id, days)
        await events_service.log_api_call("crypto", f"history/{coin_id}", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch crypto history")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "crypto_history")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto/trending")
async def get_trending_crypto():
    """Get trending cryptocurrencies"""
    try:
        data = await crypto_service.get_trending_coins()
        await events_service.log_api_call("crypto", "trending", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch trending crypto")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "crypto_trending")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crypto/global")
async def get_global_crypto_data():
    """Get global cryptocurrency market data"""
    try:
        data = await crypto_service.get_global_market_data()
        await events_service.log_api_call("crypto", "global", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch global crypto data")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "crypto_global")
        raise HTTPException(status_code=500, detail=str(e))

# Weather endpoints
@app.get("/weather/current")
async def get_current_weather(city: str = Query(..., description="City name")):
    """Get current weather for a city"""
    try:
        data = await weather_service.get_current_weather(city)
        await events_service.log_api_call("weather", "current", data is not None)
        
        if not data or "error" in data:
            raise HTTPException(status_code=503, detail=data.get("error", "Unable to fetch weather"))
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "current_weather")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/forecast")
async def get_weather_forecast(city: str = Query(..., description="City name"), days: int = Query(5, ge=1, le=5)):
    """Get weather forecast for a city"""
    try:
        data = await weather_service.get_weather_forecast(city, days)
        await events_service.log_api_call("weather", "forecast", data is not None)
        
        if not data or "error" in data:
            raise HTTPException(status_code=503, detail=data.get("error", "Unable to fetch forecast"))
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "weather_forecast")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/coordinates")
async def get_weather_by_coordinates(lat: float = Query(...), lon: float = Query(...)):
    """Get weather by coordinates"""
    try:
        data = await weather_service.get_weather_by_coordinates(lat, lon)
        await events_service.log_api_call("weather", "coordinates", data is not None)
        
        if not data or "error" in data:
            raise HTTPException(status_code=503, detail=data.get("error", "Unable to fetch weather"))
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "weather_coordinates")
        raise HTTPException(status_code=500, detail=str(e))

# IP Info endpoints
@app.get("/ip-info")
async def get_ip_info(ip: Optional[str] = Query(None, description="IP address (optional)")):
    """Get IP information"""
    try:
        data = await ipinfo_service.get_ip_info(ip)
        await events_service.log_api_call("ipinfo", "lookup", data is not None)
        
        if not data or "error" in data:
            raise HTTPException(status_code=503, detail=data.get("error", "Unable to fetch IP info"))
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "ip_info")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ip-info/current")
async def get_current_ip_info():
    """Get current IP information"""
    try:
        data = await ipinfo_service.get_current_ip_info()
        await events_service.log_api_call("ipinfo", "current", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch current IP info")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "current_ip_info")
        raise HTTPException(status_code=500, detail=str(e))

# Trending endpoints
@app.get("/trending/github")
async def get_github_trending(language: str = Query("", description="Programming language"), since: str = Query("daily", description="Time range: daily, weekly, monthly")):
    """Get trending GitHub repositories"""
    try:
        data = await trends_service.get_github_trending(language, since)
        await events_service.log_api_call("trends", "github", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch GitHub trending")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "github_trending")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending/hackernews")
async def get_hackernews_top(count: int = Query(20, ge=1, le=50)):
    """Get top Hacker News stories"""
    try:
        data = await trends_service.get_hacker_news_top(count)
        await events_service.log_api_call("trends", "hackernews", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch Hacker News stories")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "hackernews_top")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending/devto")
async def get_devto_trending():
    """Get trending Dev.to articles"""
    try:
        data = await trends_service.get_dev_to_trending()
        await events_service.log_api_call("trends", "devto", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch Dev.to articles")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "devto_trending")
        raise HTTPException(status_code=500, detail=str(e))

# News endpoints
@app.get("/news/headlines")
async def get_news_headlines(country: str = Query("us"), category: Optional[str] = Query(None), page_size: int = Query(20, ge=1, le=100)):
    """Get top news headlines"""
    try:
        data = await news_service.get_top_headlines(country, category, page_size)
        await events_service.log_api_call("news", "headlines", data is not None)
        
        if not data or "error" in data:
            raise HTTPException(status_code=503, detail=data.get("error", "Unable to fetch news"))
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "news_headlines")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/search")
async def search_news(q: str = Query(..., description="Search query"), page_size: int = Query(20, ge=1, le=100)):
    """Search news articles"""
    try:
        data = await news_service.search_news(q, page_size)
        await events_service.log_api_call("news", "search", data is not None)
        
        if not data or "error" in data:
            raise HTTPException(status_code=503, detail=data.get("error", "Unable to search news"))
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "news_search")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/tech")
async def get_tech_news():
    """Get technology news"""
    try:
        data = await news_service.get_tech_news()
        await events_service.log_api_call("news", "tech", data is not None)
        
        if not data or "error" in data:
            # Try alternative source
            data = await news_service.get_bbc_news()
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch tech news")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "tech_news")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/crypto")
async def get_crypto_news():
    """Get cryptocurrency news"""
    try:
        data = await news_service.get_crypto_news()
        await events_service.log_api_call("news", "crypto", data is not None)
        
        if not data:
            raise HTTPException(status_code=503, detail="Unable to fetch crypto news")
        
        return JSONResponse(content=data)
    except Exception as e:
        await events_service.log_error(str(e), "crypto_news")
        raise HTTPException(status_code=500, detail=str(e))

# Events endpoints
@app.get("/events")
async def get_recent_events(limit: int = Query(50, ge=1, le=100)):
    """Get recent dashboard events"""
    try:
        data = await events_service.get_recent_events(limit)
        return JSONResponse(content={"events": data})
    except Exception as e:
        await events_service.log_error(str(e), "get_events")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/log")
async def log_custom_event(event: str, description: str, icon: str = "📊"):
    """Log a custom event"""
    try:
        success = await events_service.log_event(event, description, icon)
        return JSONResponse(content={"success": success})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
