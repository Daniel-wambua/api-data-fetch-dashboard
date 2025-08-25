import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Any
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DataPulse - Command Center",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Disable service workers and add meta tags to prevent webview errors
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<script>
// Disable service worker registration to prevent webview errors
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
            registration.unregister();
        }
    });
}
// Prevent service worker registration
if (navigator.serviceWorker) {
    delete navigator.serviceWorker;
}
</script>
""", unsafe_allow_html=True)

# Constants
API_BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 60  # seconds

# Custom CSS for premium, modern UI
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* CLASSIC WEBPAGE - RESET DEFAULT MARGINS */
    html, body, .stApp {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
    }
    
    /* Global Styles - ENHANCED */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* COOL ANIMATED BACKGROUND ELEMENTS */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(240, 147, 251, 0.05) 0%, transparent 50%);
        z-index: -1;
        animation: backgroundShift 20s ease-in-out infinite alternate;
    }
    
    @keyframes backgroundShift {
        0% { transform: scale(1) rotate(0deg); opacity: 0.3; }
        100% { transform: scale(1.1) rotate(2deg); opacity: 0.6; }
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stActionButton {display:none;}
    header[data-testid="stHeader"] {display: none;}
    .block-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
    .main .block-container {padding: 0 !important; margin: 0 !important;}
    section[data-testid="stSidebar"] {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    
    /* Responsive Container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* CLASSIC WEBPAGE - EDGE-TO-EDGE HEADER */
    .main-header {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 60px !important;
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        border-bottom: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        z-index: 10000 !important;
        padding: 0 2rem !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    
    /* CLASSIC WEBPAGE - EDGE-TO-EDGE NAVIGATION (MOVED MUCH LOWER) */
    .nav-bar-fixed {
        position: fixed !important;
        top: 200px !important;
        left: 0 !important;
        width: 100% !important;
        height: 60px !important;
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        border-bottom: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 2px 15px rgba(0,0,0,0.2) !important;
        z-index: 9000 !important;
        padding: 0 2rem !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Position the Streamlit navigation buttons - DISABLED (using spacing instead) */
    .nav-bar-fixed + div[data-testid="stHorizontalBlock"] {
        /* Disabled - using margin-top spacing instead */
    }
    
    /* Hide the navigation selectbox */
    div[data-testid="stSelectbox"] {
        display: none !important;
    }
    
    /* OLD BUTTON STYLING - DISABLED (using new approach below) */
    
    /* FALLBACK: Target any horizontal block with buttons that might be navigation */
    div[data-testid="stHorizontalBlock"]:has(button) {
        position: relative !important;
        top: 0 !important;
        margin-top: 0 !important;
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* ULTRA AGGRESSIVE: Move navigation buttons away from header if they exist near top */
    body div[data-testid="stHorizontalBlock"]:first-of-type {
        margin-top: 0px !important;
        position: relative !important;
    }
    
    /* Style all navigation buttons nicely */
    div[data-testid="stHorizontalBlock"] button {
        background: linear-gradient(135deg, #334155, #475569) !important;
        border: 1px solid #64748b !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-size: 1.2rem !important;
        min-width: 70px !important;
        text-align: center !important;
        height: 50px !important;
    }
    
    /* Navigation button hover effect */
    div[data-testid="stHorizontalBlock"] button:hover {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-color: #667eea !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3) !important;
        color: white !important;
    }
    
    /* Active navigation button styling */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-color: #667eea !important;
        color: white !important;
        box-shadow: 0 3px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* CLASSIC WEBPAGE - EDGE-TO-EDGE FOOTER */
    .main-footer {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 50px !important;
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        border-top: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.3) !important;
        z-index: 10000 !important;
        padding: 0 2rem !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
        width: 100%;
        height: 100%;
        gap: 2rem;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
        min-width: 200px;
    }
    
    .logo-icon {
        font-size: 1.8rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 10px #667eea);
    }
    
    .logo-text {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .logo-subtitle {
        color: #64748b;
        font-size: 0.7rem;
        margin-left: 4px;
        font-weight: 500;
    }
    
    /* Static Navigation Buttons in Header */
    .header-nav-buttons {
        display: flex;
        gap: 0.5rem;
        flex: 1;
        justify-content: center;
        align-items: center;
        max-width: 700px;
        margin: 0 1rem;
    }
    
    .nav-btn {
        background: linear-gradient(135deg, #334155, #475569);
        border: 1px solid #64748b;
        color: #e2e8f0;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        cursor: pointer;
        font-size: 0.85rem;
        min-width: 70px;
        text-align: center;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 32px;
    }
    
    .nav-btn:hover {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        color: white;
    }
    
    .nav-btn.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-color: rgba(102, 126, 234, 0.6);
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .nav-btn.active:hover {
        background: linear-gradient(135deg, #5a6fd8, #6b42a0);
        transform: translateY(-2px) scale(1.02);
    }
    
    /* INDENTED CONTENT WITH ADJUSTED SPACING FOR MUCH LOWER NAV */
    .content-wrapper {
        margin-top: 280px !important;
        margin-bottom: 60px !important;
        margin-left: 60px !important;
        margin-right: 60px !important;
        padding: 1.5rem 3rem !important;
        min-height: calc(100vh - 340px) !important;
        max-width: 1280px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        box-sizing: border-box !important;
        position: relative !important;
        background: transparent !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: none !important;
        z-index: 1 !important;
    }
    
    /* EPIC ANIMATED SIDE BORDERS - POSITIONED FOR INDENTED LAYOUT */
    .content-wrapper::before {
        content: '' !important;
        position: fixed !important;
        left: 20px !important;
        top: 0 !important;
        width: 6px !important;
        height: 100vh !important;
        background: linear-gradient(180deg, 
            #667eea 0%, 
            #764ba2 25%, 
            #f093fb 50%, 
            #667eea 75%, 
            #764ba2 100%) !important;
        z-index: 10001 !important;
        animation: borderPulse 4s ease-in-out infinite !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5) !important;
    }
    
    .content-wrapper::after {
        content: '' !important;
        position: fixed !important;
        right: 20px !important;
        top: 0 !important;
        width: 6px !important;
        height: 100vh !important;
        background: linear-gradient(180deg, 
            #f093fb 0%, 
            #667eea 25%, 
            #764ba2 50%, 
            #f093fb 75%, 
            #667eea 100%) !important;
        z-index: 10001 !important;
        animation: borderPulse 4s ease-in-out infinite reverse !important;
        box-shadow: 0 0 20px rgba(240, 147, 251, 0.5) !important;
    }
    
    @keyframes borderPulse {
        0% { 
            opacity: 0.6; 
            transform: scaleY(0.95) scaleX(1); 
            filter: hue-rotate(0deg);
        }
        50% { 
            opacity: 1; 
            transform: scaleY(1) scaleX(1.2); 
            filter: hue-rotate(30deg);
        }
        100% { 
            opacity: 0.8; 
            transform: scaleY(0.98) scaleX(1); 
            filter: hue-rotate(60deg);
        }
    }
    
    .main-content {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
        width: 100% !important;
    }
    
    /* Fixed Footer - Completely Static and Pinned */
    .custom-footer {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.03));
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 15px 15px 0 0;
        padding: 0.8rem 1.5rem;
        margin: 0;
        text-align: center;
        box-shadow: 0 -8px 25px rgba(0,0,0,0.2);
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 9999 !important;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .footer-content {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 500;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .footer-heart {
        color: #ff4757;
        animation: heartbeat 2s ease-in-out infinite;
        font-size: 0.8rem;
    }
    
    .footer-author {
        background: linear-gradient(135deg, #667eea, #764ba2);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
    
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 0.6rem 1rem;
            height: 55px;
        }
        
        .nav-container {
            flex-wrap: wrap;
            height: auto;
        }
        
        .logo-section {
            gap: 6px;
        }
        
        .logo-icon {
            font-size: 1.3rem;
        }
        
        .logo-text {
            font-size: 1rem;
        }
        
        .logo-subtitle {
            font-size: 0.6rem;
        }
        
        .nav-buttons {
            gap: 4px;
            width: 100%;
            margin: 0.5rem 0 0 0;
        }
        
        .nav-btn-container {
            min-width: 60px;
            max-width: 75px;
        }
        
        .content-wrapper {
            margin-top: 90px;
            padding: 0.5rem;
            min-height: calc(100vh - 140px);
            margin-bottom: 45px;
        }
        
        .custom-footer {
            padding: 0.6rem 1rem;
            height: 35px;
        }
        
        .footer-content {
            font-size: 0.7rem;
            gap: 4px;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            height: 50px;
            padding: 0.5rem 0.8rem;
        }
        
        .nav-buttons {
            gap: 3px;
        }
        
        .nav-btn-container {
            min-width: 50px;
            max-width: 65px;
        }
        
        .content-wrapper {
            margin-top: 85px;
            padding: 0.3rem;
            min-height: calc(100vh - 130px);
            margin-bottom: 40px;
        }
        
        .custom-footer {
            height: 30px;
            padding: 0.4rem 0.8rem;
        }
        
        .footer-content {
            font-size: 0.65rem;
        }
    }
    
    /* Glassmorphism Effects - IMPROVED STRUCTURE */
    .glass-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.35) !important;
    }
    
    /* Reset Streamlit Specific Styles to Prevent Conflicts */
    .stMarkdown, .stMarkdown > div {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        color: inherit !important;
    }
    
    /* Ensure HTML Content Renders Properly */
    .stMarkdown [data-testid="stMarkdownContainer"] {
        color: inherit !important;
    }
    
    /* Prevent Text Escaping Issues */
    .stMarkdown div[data-stale="false"] {
        color: inherit !important;
        font-family: inherit !important;
    }
    
    /* CUSTOM BUTTON STYLING FOR ACTIONS */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        color: white !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin: 0.25rem 0 !important;
        cursor: pointer !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
        height: auto !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Chart Containers - IMPROVED STRUCTURE */
    .chart-container {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Metric Grid - IMPROVED LAYOUT */
    .metric-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
        gap: 1rem !important;
        margin: 1rem 0 !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Insight Grid - IMPROVED RESPONSIVE */
    .insight-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important;
        gap: 1.5rem !important;
        margin: 1.5rem 0 !important;
        position: relative !important;
        z-index: 1 !important;
    }
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 1rem;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    /* Responsive Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .insight-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    @media (max-width: 768px) {
        .chart-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .insight-grid {
            grid-template-columns: 1fr;
        }
        
        .metric-grid {
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.8rem;
        }
        
        .glass-card {
            padding: 1rem;
        }
        
        .chart-container {
            padding: 0.8rem;
        }
    }
    
    @media (max-width: 480px) {
        .metric-grid {
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.6rem;
        }
        
        .chart-grid {
            gap: 0.8rem;
        }
    }
    
    /* Static Navigation Buttons - Completely Fixed */
    .nav-buttons-container {
        position: fixed !important;
        top: 80px !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 9998 !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding: 0.5rem 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Perfect button styling - all uniform and static */
    .stButton > button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        width: 100% !important;
        height: 50px !important;
        font-size: 1.4rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 70px !important;
        max-width: none !important;
        padding: 0 !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        position: relative !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(118, 75, 162, 0.25)) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3) !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        color: white !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5a6fd8, #6b42a0) !important;
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Ensure all columns are perfectly equal */
    .stColumns > div {
        flex: 1 1 0 !important;
        width: 14.28% !important;
        min-width: 0 !important;
        max-width: none !important;
    }
    
    /* Perfect spacing for navigation */
    .stColumns {
        gap: 0.5rem !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    
    /* Remove any unwanted spacing */
    .element-container {
        margin: 0 !important;
    }
    
    /* Static positioning for buttons */
    .stButton {
        position: static !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Better input styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSelectbox > div > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stMultiSelect > div > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Performance optimizations */
    * {
        will-change: auto;
    }
    
    .element-container {
        contain: layout style;
    }
    
    /* Better loading indicators */
    .stSpinner > div {
        border-color: rgba(102, 126, 234, 0.3) rgba(102, 126, 234, 0.3) rgba(102, 126, 234, 0.3) #667eea !important;
    }
    
    /* Selectbox and other inputs styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #e2e8f0 !important;
    }
    
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #e2e8f0 !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #e2e8f0 !important;
    }
    
    /* Fix dropdown visibility */
    .stSelectbox ul {
        background: rgba(30, 30, 50, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stSelectbox li {
        color: #e2e8f0 !important;
    }
    
    .stSelectbox li:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        color: white !important;
    }
    
    /* Metric containers */
    .metric {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
        color: white;
        font-weight: 600;
        transform: translateX(15px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Premium Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Crypto Price Styling */
    .crypto-positive {
        color: #00ff88;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        animation: pulse-green 2s infinite;
    }
    
    .crypto-negative {
        color: #ff4757;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255, 71, 87, 0.3);
        animation: pulse-red 2s infinite;
    }
    
    @keyframes pulse-green {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes pulse-red {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Premium Sidebar */
    .sidebar-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    /* Control Elements */
    .stSelectbox > div > div {
        background: rgba(15, 15, 35, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8 0%, #6b5b95 100%);
    }
    
    /* Event Items */
    .event-item {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        backdrop-filter: blur(10px);
    }
    
    .event-item:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        transform: translateX(10px);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    .event-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 0 2px 2px 0;
    }
    
    /* Chart Containers */
    .chart-container {
        background: rgba(15, 15, 35, 0.6);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(15px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    /* Premium Status Indicators */
    .status-online {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #00ff88;
        border-radius: 50%;
        animation: pulse-online 2s infinite;
        box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7);
    }
    
    @keyframes pulse-online {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
    
    /* Loading Animations */
    .loading-pulse {
        animation: loading-pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes loading-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Premium Typography - Maximum Visibility */
    .section-title {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 2rem !important;
        margin-top: 1rem !important;
        text-align: center !important;
        padding: 1.5rem 2rem !important;
        position: relative !important;
        z-index: 1000 !important;
        clear: both !important;
        display: block !important;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        border-radius: 15px !important;
        border: 2px solid #667eea !important;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(102, 126, 234, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Add glow effect for better visibility */
    .section-title::before {
        content: '' !important;
        position: absolute !important;
        top: -2px !important;
        left: -2px !important;
        right: -2px !important;
        bottom: -2px !important;
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 15px !important;
        z-index: -1 !important;
        filter: blur(8px) !important;
        opacity: 0.7 !important;
    }
    
    .subsection-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff !important;
        margin-bottom: 1rem;
        padding: 0.75rem 1.5rem !important;
        border-bottom: 2px solid rgba(102, 126, 234, 0.5);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(51, 65, 85, 0.8)) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Improve general text visibility throughout the app */
    .main .block-container p,
    .main .block-container div,
    .main .block-container span,
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container h5,
    .main .block-container h6 {
        color: #ffffff !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Ensure markdown text is visible */
    .main .block-container .markdown-text-container p,
    .main .block-container .markdown-text-container div,
    .main .block-container .markdown-text-container h1,
    .main .block-container .markdown-text-container h2,
    .main .block-container .markdown-text-container h3 {
        color: #ffffff !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Specific styling for section titles in markdown */
    .main .block-container h2 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-align: center !important;
        padding: 1.5rem 2rem !important;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
        border-radius: 15px !important;
        border: 2px solid #667eea !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
        margin: 1rem 0 2rem 0 !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 15, 35, 0.8);
        border-radius: 15px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        color: #e2e8f0;
        font-weight: 500;
        padding: 1rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 15, 35, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b5b95 100%);
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .glass-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
    }
    
    /* Add floating animation for important elements */
    .floating {
        animation: floating 3s ease-in-out infinite;
    }
    
    @keyframes floating {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Enhanced focus states */
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Premium tooltips */
    [data-testid="stTooltipHoverTarget"] {
        background: rgba(15, 15, 35, 0.95);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(20px);
    }
    
    /* ANIMATED SIDE BORDERS FOR INDENTED LAYOUT */
    .side-border-left, .side-border-right {
        position: fixed;
        top: 150px;
        bottom: 60px;
        width: 4px;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: borderGradient 8s ease infinite;
        z-index: 5;
        border-radius: 2px;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
    }
    
    .side-border-left {
        left: 20px;
    }
    
    .side-border-right {
        right: 20px;
    }
    
    /* BETTER SECTION SPACING AND VISUAL HIERARCHY */
    .metric-section {
        margin-bottom: 3rem !important;
        padding: 2rem !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
    }
    
    .metric-section h1,
    .metric-section h2,
    .metric-section h3 {
        margin-bottom: 1.5rem !important;
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    }
    
    .chart-container {
        margin: 2rem 0 !important;
        padding: 1.5rem !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* ENHANCED METRIC CARDS WITH BETTER GLASS EFFECTS */
    .metric-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .metric-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=60)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_data(endpoint: str, params: Dict = None) -> Dict:
    """Fetch data from API with caching for better performance"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)  # Reduced timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {endpoint}: {str(e)}")
        return {}
    except json.JSONDecodeError:
        st.error(f"Invalid JSON response from {endpoint}")
        return {}

def format_currency(value: float, currency: str = "USD") -> str:
    """Format currency values"""
    if currency == "USD":
        return f"${value:,.2f}"
    return f"{value:,.2f} {currency}"

def format_percentage(value: float) -> str:
    """Format percentage with color"""
    color = "crypto-positive" if value >= 0 else "crypto-negative"
    sign = "+" if value >= 0 else ""
    return f'<span class="{color}">{sign}{value:.2f}%</span>'

# Removed old create_premium_metric_card function - using newer version below

def create_weather_forecast_chart(forecast_data):
    """Create a beautiful weather forecast chart"""
    if not forecast_data or "list" not in forecast_data:
        return go.Figure()
    
    temps = []
    times = []
    humidity = []
    
    for item in forecast_data["list"][:8]:  # Next 24 hours (3-hour intervals)
        temps.append(item["main"]["temp"])
        humidity.append(item["main"]["humidity"])
        # Convert timestamp to hour
        from datetime import datetime
        dt = datetime.fromtimestamp(item["dt"])
        times.append(dt.strftime("%H:%M"))
    
    fig = go.Figure()
    
    # Temperature line
    fig.add_trace(go.Scatter(
        x=times,
        y=temps,
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='#74b9ff', width=3),
        marker=dict(size=8, symbol='circle'),
        fill='tonexty',
        fillcolor='rgba(116, 185, 255, 0.1)'
    ))
    
    fig.update_layout(
        title=dict(
            text="24h Weather Forecast",
            font=dict(size=18, color="white", family="Inter"),
            x=0.5
        ),
        xaxis=dict(color="white", title="Time"),
        yaxis=dict(color="white", title="Temperature (°C)"),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="white", family="Inter"),
        height=400,
        showlegend=False
    )
    
    return fig

def create_crypto_chart(data: Dict) -> go.Figure:
    """Create a stunning cryptocurrency price chart"""
    if not data or "prices" not in data:
        return go.Figure()
    
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    
    fig = go.Figure()
    
    # Main price line with gradient
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["price"],
        mode="lines",
        name="Price",
        line=dict(
            color="rgba(102, 126, 234, 1)",
            width=3
        ),
        fill="tonexty",
        fillcolor="rgba(102, 126, 234, 0.1)",
        hovertemplate="<b>%{y:$,.2f}</b><br>%{x}<extra></extra>"
    ))
    
    # Add volume bars if available
    if "total_volumes" in data:
        volumes = data["total_volumes"]
        vol_df = pd.DataFrame(volumes, columns=["timestamp", "volume"])
        vol_df["datetime"] = pd.to_datetime(vol_df["timestamp"], unit="ms")
        
        fig.add_trace(go.Bar(
            x=vol_df["datetime"],
            y=vol_df["volume"],
            name="Volume",
            yaxis="y2",
            opacity=0.3,
            marker_color="rgba(118, 75, 162, 0.6)"
        ))
    
    fig.update_layout(
        title=dict(
            text="Price Chart",
            font=dict(size=20, color="white", family="Inter"),
            x=0.5
        ),
        xaxis=dict(
            title="Time",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="white",
            showgrid=True
        ),
        yaxis=dict(
            title="Price (USD)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="white",
            showgrid=True
        ),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            color="rgba(118, 75, 162, 0.8)"
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="white", family="Inter"),
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_enhanced_crypto_chart(data, coin_name):
    """Create an enhanced cryptocurrency chart with volume and advanced styling"""
    if not data or "prices" not in data:
        return go.Figure()
    
    from datetime import datetime
    dates = [datetime.fromtimestamp(item[0] / 1000) for item in data["prices"]]
    prices = [item[1] for item in data["prices"]]
    
    # Get volume data if available
    volumes = []
    if "total_volumes" in data:
        volumes = [item[1] for item in data["total_volumes"]]
    
    fig = go.Figure()
    
    # Price line with gradient fill
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color='#667eea', width=3),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)',
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Date: %{x}<br>' +
                      'Price: $%{y:,.2f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add volume bars if available
    if volumes:
        fig.add_trace(go.Bar(
            x=dates,
            y=volumes,
            name='Volume',
            marker_color='rgba(118, 75, 162, 0.3)',
            yaxis='y2',
            opacity=0.6
        ))
    
    # Calculate price change for title color
    price_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if len(prices) > 1 else 0
    title_color = "#00b894" if price_change >= 0 else "#ff4757"
    
    fig.update_layout(
        title=dict(
            text=f"📈 {coin_name.title()} Price History ({price_change:+.2f}%)",
            font=dict(size=20, color=title_color, family="Inter"),
            x=0.5
        ),
        xaxis=dict(
            color="white",
            title="Date",
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            color="white",
            title="Price (USD)",
            side='left',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="white", family="Inter"),
        height=500,
        showlegend=False,
        hovermode='x unified'
    )
    
    # Add secondary y-axis for volume if available
    if volumes:
        fig.update_layout(
            yaxis2=dict(
                color="white",
                title="Volume",
                side='right',
                overlaying='y',
                showgrid=False
            )
        )
    
    return fig

def create_weather_forecast_chart(data: Dict) -> go.Figure:
    """Create a beautiful weather forecast chart"""
    if not data or "list" not in data:
        return go.Figure()
    
    forecast_data = []
    for item in data["list"][:24]:  # Next 24 forecasts
        forecast_data.append({
            "datetime": datetime.fromtimestamp(item["dt"]),
            "temp": item["main"]["temp"],
            "feels_like": item["main"]["feels_like"],
            "humidity": item["main"]["humidity"],
            "description": item["weather"][0]["description"].title()
        })
    
    df = pd.DataFrame(forecast_data)
    
    fig = go.Figure()
    
    # Temperature line
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["temp"],
        mode="lines+markers",
        name="Temperature",
        line=dict(color="#ff6b6b", width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{y:.1f}°C</b><br>%{x}<extra></extra>"
    ))
    
    # Feels like temperature
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["feels_like"],
        mode="lines",
        name="Feels Like",
        line=dict(color="#4ecdc4", width=2, dash="dash"),
        hovertemplate="<b>%{y:.1f}°C</b><br>%{x}<extra></extra>"
    ))
    
    # Humidity on secondary axis
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["humidity"],
        mode="lines",
        name="Humidity",
        line=dict(color="#74b9ff", width=2),
        yaxis="y2",
        hovertemplate="<b>%{y}%</b><br>%{x}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="24-Hour Weather Forecast",
            font=dict(size=20, color="white", family="Inter"),
            x=0.5
        ),
        xaxis=dict(
            title="Time",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="white"
        ),
        yaxis=dict(
            title="Temperature (°C)",
            gridcolor="rgba(255, 255, 255, 0.1)",
            color="white"
        ),
        yaxis2=dict(
            title="Humidity (%)",
            overlaying="y",
            side="right",
            color="#74b9ff"
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="white", family="Inter"),
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# Main dashboard
def main():
    load_css()
    
    # Initialize session state
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "🏠 Overview"
    
    # Create top navigation header
    create_top_navigation()
    
    # Main content wrapper - accounts for fixed header and nav
    st.markdown('<div class="main-content" style="padding: 1rem 1.5rem; margin-top: 280px;">', unsafe_allow_html=True)
    
    # Get selected page from session state
    selected_section = st.session_state.selected_page
    
    # Display the selected section
    if selected_section == "🏠 Overview":
        show_overview()
    elif selected_section == "₿ Crypto":
        show_crypto_dashboard()
    elif selected_section == "🌤️ Weather":
        show_weather_dashboard()
    elif selected_section == "🌐 IP Info":
        show_ip_info_dashboard()
    elif selected_section == "📈 Trending":
        show_trending_dashboard()
    elif selected_section == "📰 News":
        show_news_dashboard()
    elif selected_section == "📊 Events":
        show_events_dashboard()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add footer
    create_footer()

def create_top_navigation():
    """Create stunning static header with separated navigation"""
    # Initialize session state if not exists
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "🏠 Overview"
    
    # Create static header
    st.markdown("""
    <div class="main-header">
        <div class="nav-container">
            <div class="logo-section">
                <div class="logo-icon">⚡</div>
                <div class="logo-text">DataPulse</div>
                <div class="logo-subtitle">Command Center</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation options
    nav_options = [
        ("🏠 Overview", "🏠"),
        ("₿ Crypto", "₿"),
        ("🌤️ Weather", "🌤️"),
        ("🌐 IP Info", "🌐"),
        ("📈 Trending", "📈"),
        ("📰 News", "📰"),
        ("📊 Events", "📊")
    ]
    
    # Create navigation bar with working buttons
    st.markdown("""
    <div class="nav-bar-fixed">
        <div class="nav-spacer" style="height: 60px; width: 100%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add some space to push navigation lower
    st.markdown('<div style="margin-top: 70px;"></div>', unsafe_allow_html=True)
    
    # Use columns for navigation with explicit spacing
    cols = st.columns(len(nav_options))
    
    for i, (label, icon) in enumerate(nav_options):
        with cols[i]:
            # Check if this is the active page
            is_active = st.session_state.selected_page == label
            button_type = "primary" if is_active else "secondary"
            
            # Create button with custom styling through type
            if st.button(
                icon,
                key=f"nav_{i}",
                help=label,
                type=button_type,
                use_container_width=True
            ):
                st.session_state.selected_page = label
                st.rerun()

def create_footer():
    """Create a classic fixed footer"""
    st.markdown("""
    <div class="main-footer">
        <div style="color: #e2e8f0; font-size: 0.9rem; font-weight: 500;">
            <span>Made with ❤️ by Havoc • DataPulse v1.0 • Powered by FastAPI & Streamlit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
def create_premium_navigation():
    """Create a beautiful premium navigation system"""
    
    # Navigation options with emojis and descriptions
    nav_options = {
        "🏠 Overview": {
            "icon": "🏠",
            "title": "Dashboard Overview",
            "desc": "Key metrics and insights",
            "color": "#667eea"
        },
        "₿ Crypto": {
            "icon": "₿", 
            "title": "Cryptocurrency",
            "desc": "Live prices and charts",
            "color": "#f7931a"
        },
        "🌤️ Weather": {
            "icon": "�️",
            "title": "Weather Data",
            "desc": "Forecasts and conditions",
            "color": "#74b9ff"
        },
        "🌐 IP Info": {
            "icon": "🌐",
            "title": "IP Information",
            "desc": "Geolocation and details",
            "color": "#00b894"
        },
        "📈 Trending": {
            "icon": "📈",
            "title": "Trending Content",
            "desc": "GitHub, HN, Dev.to",
            "color": "#e17055"
        },
        "📰 News": {
            "icon": "📰",
            "title": "News Feed",
            "desc": "Latest headlines",
            "color": "#6c5ce7"
        },
        "📊 Events": {
            "icon": "�",
            "title": "Event Logs",
            "desc": "Real-time monitoring",
            "color": "#fd79a8"
        }
    }
    
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    st.markdown('### 🎛️ **Navigation Command Center**')
    
    # Create beautiful radio buttons with custom styling
    selected = st.radio(
        "Select Dashboard Section",
        options=list(nav_options.keys()),
        format_func=lambda x: f"{nav_options[x]['icon']} {nav_options[x]['title']}",
        label_visibility="collapsed"
    )
    
    # Display description for selected item
    if selected:
        option = nav_options[selected]
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {option['color']}20, {option['color']}10);
            border: 1px solid {option['color']}40;
            border-radius: 15px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: center;
        ">
            <div style="font-size: 2rem;">{option['icon']}</div>
            <div style="font-weight: 600; margin: 0.5rem 0;">{option['title']}</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">{option['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add animated side borders for indented layout
    st.markdown("""
    <div class="side-border-left"></div>
    <div class="side-border-right"></div>
    """, unsafe_allow_html=True)
    
    return selected

def create_status_header():
    """Create a premium status header with live indicators"""
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="status-online"></div>
            <div>
                <div style="font-weight: 600; font-size: 1.1rem;">System Status</div>
                <div style="color: #00ff88; font-size: 0.9rem;">All systems operational</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh all data"):
            st.cache_data.clear()
            st.rerun()
    
    with col3:
        theme = st.selectbox("🎨 Theme", ["Dark", "Light"], index=0, label_visibility="collapsed")
    
    with col4:
        auto_refresh = st.checkbox("⚡ Auto", value=False, help="Auto-refresh every 60 seconds")
    
    return auto_refresh, theme

def create_premium_metric_card(title, value, delta=None, icon="📊", color="#667eea"):
    """Create a beautiful metric card with clean rendering"""
    
    # Create delta section if provided
    if delta is not None:
        # Extract numeric value from delta if it's a string
        try:
            if isinstance(delta, str):
                # Remove % and other characters, then convert to float
                delta_numeric = float(delta.replace('%', '').replace('+', '').replace(',', '').replace('°C', ''))
            else:
                delta_numeric = float(delta)
        except (ValueError, TypeError):
            delta_numeric = 0
            
        delta_color = "#00ff88" if delta_numeric >= 0 else "#ff4757"
        delta_symbol = "↗" if delta_numeric >= 0 else "↘"
        
        # Use clean HTML structure
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="color: {color}; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;">{title}</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">{value}</div>
            <div style="color: {delta_color}; font-size: 0.9rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 5px;">
                <span>{delta_symbol}</span>
                <span>{delta}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Simple card without delta
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="color: {color}; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;">{title}</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #e2e8f0;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

def show_overview():
    """Display a stunning responsive overview dashboard"""
    st.markdown('<div class="metric-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🏠 Command Center Overview</h2>', unsafe_allow_html=True)
    
    # Quick stats row - responsive grid
    st.markdown("### ⚡ **Live Market Pulse**")
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        crypto_data = fetch_data("/crypto/prices", {"coins": "bitcoin"})
        if crypto_data and "bitcoin" in crypto_data:
            btc_price = crypto_data["bitcoin"]["usd"]
            btc_change = crypto_data["bitcoin"]["usd_24h_change"]
            create_premium_metric_card(
                "Bitcoin Price", 
                format_currency(btc_price),
                f"{btc_change:+.2f}%",
                "₿",
                "#f7931a"
            )
    
    with col2:
        weather_data = fetch_data("/weather/current", {"city": "New York"})
        if weather_data and "main" in weather_data:
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            create_premium_metric_card(
                "NYC Weather",
                f"{temp:.1f}°C",
                f"Feels {feels_like:.1f}°C",
                "🌤️",
                "#74b9ff"
            )
    
    with col3:
        ip_data = fetch_data("/ip-info/current")
        if ip_data and "country" in ip_data:
            country = ip_data["country"]
            city = ip_data.get("city", "Unknown")
            create_premium_metric_card(
                "Your Location",
                country,
                city,
                "🌐",
                "#00b894"
            )
    
    with col4:
        events_data = fetch_data("/events")
        if events_data and "events" in events_data:
            event_count = len(events_data["events"])
            create_premium_metric_card(
                "Events Today",
                str(event_count),
                "Real-time",
                "📊",
                "#fd79a8"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Market overview section - vertical charts layout
    st.markdown("### 📈 **Market Intelligence**")
    
    # First chart - Crypto Performance (full width)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    crypto_portfolio_data = fetch_data("/crypto/prices", {"coins": "bitcoin,ethereum,binancecoin,cardano"})
    if crypto_portfolio_data:
        coins = []
        prices = []
        changes = []
        for coin, data in crypto_portfolio_data.items():
            coins.append(coin.title())
            prices.append(data["usd"])
            changes.append(data.get("usd_24h_change", 0))
        
        fig = go.Figure()
        
        # Create a beautiful portfolio chart
        colors = ['#f7931a', '#627eea', '#f3ba2f', '#3468dc']
        
        fig.add_trace(go.Bar(
            x=coins,
            y=changes,
            name="24h Change %",
            marker_color=[colors[i] if changes[i] >= 0 else '#ff4757' for i in range(len(changes))],
            text=[f"{change:+.1f}%" for change in changes],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=dict(
                text="🚀 Top Crypto Performance",
                font=dict(size=18, color="white", family="Inter"),
                x=0.5
            ),
            xaxis=dict(color="white", title="Cryptocurrency", tickfont=dict(size=12)),
            yaxis=dict(color="white", title="24h Change (%)", tickfont=dict(size=12)),
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="white", family="Inter"),
            height=400,
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Second chart - Weather Trend (full width)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    weather_forecast = fetch_data("/weather/forecast", {"city": "New York"})
    if weather_forecast:
        fig = create_weather_forecast_chart(weather_forecast)
        fig.update_layout(
            title=dict(text="🌤️ NYC Weather Trend", font=dict(size=18, color="white")),
            height=400,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Live feed section - responsive layout
    st.markdown("### 📡 **Live Intelligence Feed**")
    st.markdown('<div class="insight-grid">', unsafe_allow_html=True)
    
    feed_col1, feed_col2 = st.columns(2)
    
    with feed_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🔥 **Trending Now**")
        
        # Get trending GitHub repos
        github_data = fetch_data("/trending/github", {"language": "", "since": "daily"})
        if github_data and "items" in github_data:
            for i, repo in enumerate(github_data["items"][:5], 1):
                st.markdown(f"""
                <div style="
                    background: rgba(102, 126, 234, 0.05);
                    border: 1px solid rgba(102, 126, 234, 0.2);
                    border-radius: 10px;
                    padding: 0.8rem;
                    margin: 0.5rem 0;
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="
                            background: linear-gradient(135deg, #667eea, #764ba2);
                            color: white;
                            border-radius: 50%;
                            width: 22px;
                            height: 22px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 0.7rem;
                            font-weight: bold;
                            flex-shrink: 0;
                        ">{i}</span>
                        <div style="min-width: 0; flex: 1;">
                            <div style="font-weight: 600; color: #e2e8f0; font-size: 0.9rem; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{repo['name']}</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">⭐ {repo['stargazers_count']} stars</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with feed_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📰 **Breaking News**")
        
        # Get tech news
        news_data = fetch_data("/news/tech")
        if news_data:
            articles = news_data.get("articles", news_data.get("results", []))
            for i, article in enumerate(articles[:5], 1):
                title = article.get('title', 'No title')
                if len(title) > 50:
                    title = title[:50] + "..."
                source = article.get('source', {})
                if isinstance(source, dict):
                    source_name = source.get('name', 'Unknown')
                else:
                    source_name = str(source)[:15]
                
                st.markdown(f"""
                <div style="
                    background: rgba(118, 75, 162, 0.05);
                    border: 1px solid rgba(118, 75, 162, 0.2);
                    border-radius: 10px;
                    padding: 0.8rem;
                            font-size: 0.7rem;
                            font-weight: bold;
                            flex-shrink: 0;
                        ">{i}</span>
                        <div style="min-width: 0; flex: 1;">
                            <div style="font-weight: 600; color: #e2e8f0; font-size: 0.85rem; line-height: 1.2; margin-bottom: 0.2rem;">{title}</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">📰 {source_name}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close metric-section

def show_crypto_dashboard():
    """Display premium cryptocurrency dashboard with responsive design"""
    st.markdown('<div class="metric-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">₿ Cryptocurrency Command Center</h2>', unsafe_allow_html=True)
    
    # Top crypto metrics row - responsive grid
    st.markdown("### 🚀 **Elite Portfolio Tracker**")
    
    coins = st.multiselect(
        "Select cryptocurrencies to track:",
        ["bitcoin", "ethereum", "binancecoin", "cardano", "solana", "polkadot", "chainlink", "litecoin"],
        default=["bitcoin", "ethereum", "binancecoin", "cardano"],
        help="Choose your crypto portfolio to monitor"
    )
    
    if coins:
        # Fetch current prices
        prices_data = fetch_data("/crypto/prices", {"coins": ",".join(coins)})
        
        if prices_data:
            # Create responsive metric grid
            st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
            cols = st.columns(min(len(coins), 4))
            
            coin_colors = {
                "bitcoin": "#f7931a",
                "ethereum": "#627eea", 
                "binancecoin": "#f3ba2f",
                "cardano": "#3468dc",
                "solana": "#9945ff",
                "polkadot": "#e6007a",
                "chainlink": "#375bd2",
                "litecoin": "#bfbbbb"
            }
            
            coin_icons = {
                "bitcoin": "₿",
                "ethereum": "Ξ",
                "binancecoin": "🟡",
                "cardano": "♠",
                "solana": "◎",
                "polkadot": "●",
                "chainlink": "🔗",
                "litecoin": "Ł"
            }
            
            for i, coin in enumerate(coins[:4]):
                if coin in prices_data:
                    data = prices_data[coin]
                    with cols[i]:
                        create_premium_metric_card(
                            coin.title(),
                            format_currency(data["usd"]),
                            f"{data.get('usd_24h_change', 0):+.2f}%",
                            coin_icons.get(coin, "💰"),
                            coin_colors.get(coin, "#667eea")
                        )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Portfolio performance chart - vertical layout for better viewing
        st.markdown("### 📊 **Performance Analytics**")
        
        # First chart - Performance Comparison (full width)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if prices_data:
            # Create price comparison chart
            coin_names = [coin.title() for coin in coins if coin in prices_data]
            prices = [prices_data[coin]["usd"] for coin in coins if coin in prices_data]
            changes = [prices_data[coin].get("usd_24h_change", 0) for coin in coins if coin in prices_data]
            
            fig = go.Figure()
            
            # Use coin-specific colors
            colors = [coin_colors.get(coin, "#667eea") for coin in coins if coin in prices_data]
            
            fig.add_trace(go.Bar(
                x=coin_names,
                y=changes,
                name="24h Change %",
                marker=dict(
                    color=colors,
                    line=dict(color='rgba(255,255,255,0.3)', width=1)
                ),
                text=[f"{change:+.1f}%" for change in changes],
                textposition='auto',
                textfont=dict(color='white', size=12, family='Inter')
            ))
            
            fig.update_layout(
                title=dict(
                    text="🎯 24h Performance Comparison",
                    font=dict(size=20, color="white", family="Inter"),
                    x=0.5
                ),
                xaxis=dict(
                    color="white", 
                    title="Cryptocurrency",
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    color="white", 
                    title="Change (%)",
                    tickfont=dict(size=12),
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
                font=dict(color="white", family="Inter"),
                height=500,
                showlegend=False,
                hovermode='x unified',
                margin=dict(l=60, r=60, t=80, b=60)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Second chart - Historical Price (full width, vertically below)
        st.markdown('<div class="chart-container" style="margin-top: 2rem;">', unsafe_allow_html=True)
        
        if coins:
            days = st.selectbox("Historical period:", [7, 30, 90], index=0, key="crypto_days")
            
            history_data = fetch_data(f"/crypto/history/{coins[0]}", {"days": days})
            if history_data:
                fig = create_enhanced_crypto_chart(history_data, coins[0])
                fig.update_layout(
                    height=500,
                    margin=dict(l=60, r=60, t=80, b=60)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Market insights section - responsive grid
        st.markdown("### 💎 **Market Intelligence**")
        st.markdown('<div class="insight-grid">', unsafe_allow_html=True)
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🏆 **Top Performers**")
            
            if prices_data:
                # Sort by 24h change
                sorted_coins = sorted(
                    [(coin, data) for coin, data in prices_data.items()],
                    key=lambda x: x[1].get("usd_24h_change", 0),
                    reverse=True
                )
                
                for i, (coin, data) in enumerate(sorted_coins[:3], 1):
                    change = data.get("usd_24h_change", 0)
                    color = "#00b894" if change >= 0 else "#ff4757"
                    
                    st.markdown(f"""
                    <div style="
                        background: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 10px;
                        padding: 0.8rem;
                        margin: 0.5rem 0;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="min-width: 0; flex: 1;">
                                <div style="font-weight: 600; color: #e2e8f0; font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{coin.title()}</div>
                                <div style="color: #94a3b8; font-size: 0.75rem;">{format_currency(data['usd'])}</div>
                            </div>
                            <div style="
                                color: {color};
                                font-weight: bold;
                                font-size: 0.9rem;
                                flex-shrink: 0;
                                margin-left: 0.5rem;
                            ">{change:+.2f}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with insight_col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📈 **Market Stats**")
            
            if prices_data:
                total_value = sum(data["usd"] for data in prices_data.values())
                avg_change = sum(data.get("usd_24h_change", 0) for data in prices_data.values()) / len(prices_data)
                
                # Create formatted values to avoid rendering issues
                formatted_value = format_currency(total_value)
                change_color = "#00b894" if avg_change >= 0 else "#ff4757"
                formatted_change = f"{avg_change:+.2f}%"
                
                # Use simpler HTML structure to ensure proper rendering
                st.markdown(f'<div style="text-align: center; padding: 1rem;">', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 1.5rem; color: #667eea; font-weight: bold; margin-bottom: 0.5rem;">{formatted_value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: #94a3b8; margin-bottom: 1rem; font-size: 0.9rem;">Portfolio Value</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 1.2rem; color: {change_color}; font-weight: bold; margin-bottom: 0.5rem;">{formatted_change}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: #94a3b8; font-size: 0.9rem;">Average Change</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align: center; padding: 1rem; color: #94a3b8;">No data available</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with insight_col3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### ⚡ **Quick Actions**")
            
            # Use Streamlit buttons instead of HTML to prevent rendering issues
            if st.button("🔄 Refresh Data", key="refresh_crypto", use_container_width=True):
                st.rerun()
                
            if st.button("📊 Export Data", key="export_crypto", use_container_width=True):
                st.success("Export feature coming soon!")
                
            if st.button("🚨 Set Alerts", key="alerts_crypto", use_container_width=True):
                st.info("Alert system coming soon!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Trending cryptocurrencies - responsive
    st.markdown("### 🔥 **Trending Cryptocurrencies**")
    trending_data = fetch_data("/crypto/trending")
    if trending_data and "coins" in trending_data:
        trending_coins = trending_data["coins"][:5]
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for i, coin in enumerate(trending_coins, 1):
            coin_data = coin["item"]
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.8rem;
                margin: 0.5rem 0;
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
            ">
                <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">
                    <span style="
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        border-radius: 50%;
                        width: 25px;
                        height: 25px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 0.8rem;
                        flex-shrink: 0;
                    ">{i}</span>
                    <div style="min-width: 0; flex: 1;">
                        <div style="font-weight: 600; color: #e2e8f0; font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            {coin_data['name']} ({coin_data['symbol']})
                        </div>
                        <div style="color: #94a3b8; font-size: 0.75rem;">
                            Market Cap Rank: #{coin_data.get('market_cap_rank', 'N/A')}
                        </div>
                    </div>
                </div>
                <div style="flex-shrink: 0; margin-left: 0.5rem;">
                    <span style="color: #ffd700; font-size: 1rem;">⭐</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close metric-section

def show_weather_dashboard():
    """Display weather dashboard"""
    st.markdown('<div class="metric-section">', unsafe_allow_html=True)
    st.header("🌤️ Weather Dashboard")
    
    # City selector
    col1, col2 = st.columns([2, 1])
    with col1:
        city = st.text_input("Enter City Name", value="New York")
    with col2:
        if st.button("Get Weather"):
            st.cache_data.clear()
    
    if city:
        # Current weather
        current_weather = fetch_data("/weather/current", {"city": city})
        
        if current_weather and "main" in current_weather:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                temp = current_weather["main"]["temp"]
                feels_like = current_weather["main"]["feels_like"]
                st.metric("🌡️ Temperature", f"{temp:.1f}°C", f"Feels like {feels_like:.1f}°C")
            
            with col2:
                humidity = current_weather["main"]["humidity"]
                pressure = current_weather["main"]["pressure"]
                st.metric("💧 Humidity", f"{humidity}%", f"Pressure: {pressure} hPa")
            
            with col3:
                if "wind" in current_weather:
                    wind_speed = current_weather["wind"]["speed"]
                    st.metric("💨 Wind Speed", f"{wind_speed} m/s")
            
            with col4:
                if "weather" in current_weather and current_weather["weather"]:
                    description = current_weather["weather"][0]["description"].title()
                    st.metric("☁️ Conditions", description)
        
        # Weather forecast
        st.subheader("📅 7-Day Forecast")
        forecast_data = fetch_data("/weather/forecast", {"city": city})
        
        if forecast_data:
            fig = create_weather_forecast_chart(forecast_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            if "list" in forecast_data:
                forecast_list = []
                for item in forecast_data["list"][:8]:  # Next 24 hours
                    forecast_list.append({
                        "Time": datetime.fromtimestamp(item["dt"]).strftime("%H:%M"),
                        "Temp (°C)": f"{item['main']['temp']:.1f}",
                        "Description": item["weather"][0]["description"].title(),
                        "Humidity (%)": item["main"]["humidity"]
                    })
                
                df = pd.DataFrame(forecast_list)
                st.dataframe(df, use_container_width=True)

def show_ip_info_dashboard():
    """Display IP information dashboard"""
    st.header("🌐 IP Information Dashboard")
    
    # IP input
    col1, col2 = st.columns([2, 1])
    with col1:
        ip_input = st.text_input("Enter IP Address (leave empty for your current IP)", "")
    with col2:
        if st.button("Lookup IP"):
            st.cache_data.clear()
    
    # Get IP info
    endpoint = "/ip-info/current" if not ip_input else "/ip-info"
    params = {"ip": ip_input} if ip_input else None
    
    ip_data = fetch_data(endpoint, params)
    
    if ip_data and "ip" in ip_data:
        # Display IP information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌐 IP Address", ip_data["ip"])
            if "hostname" in ip_data:
                st.metric("🏠 Hostname", ip_data["hostname"])
        
        with col2:
            if "city" in ip_data and "region" in ip_data:
                location = f"{ip_data['city']}, {ip_data['region']}"
                st.metric("📍 Location", location)
            if "country" in ip_data:
                st.metric("🌍 Country", ip_data["country"])
        
        with col3:
            if "org" in ip_data:
                st.metric("🏢 Organization", ip_data["org"])
            if "timezone" in ip_data:
                st.metric("⏰ Timezone", ip_data["timezone"])
        
        # Map visualization (if coordinates available)
        if "loc" in ip_data:
            try:
                lat, lon = map(float, ip_data["loc"].split(","))
                
                # Create a simple map
                map_data = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
                st.subheader("📍 Location on Map")
                st.map(map_data)
                
            except (ValueError, AttributeError):
                st.warning("Could not parse location coordinates")
        
        # Additional details
        st.subheader("ℹ️ Additional Information")
        details = {}
        for key, value in ip_data.items():
            if key not in ["ip", "hostname", "city", "region", "country", "loc", "org", "timezone"]:
                details[key] = value
        
        if details:
            st.json(details)

def show_trending_dashboard():
    """Display trending content dashboard"""
    st.header("📈 Trending Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["🔥 GitHub", "📰 Hacker News", "👨‍💻 Dev.to"])
    
    with tab1:
        st.subheader("🔥 GitHub Trending")
        
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox("Programming Language", ["", "python", "javascript", "java", "go", "rust"])
        with col2:
            since = st.selectbox("Time Range", ["daily", "weekly", "monthly"])
        
        github_data = fetch_data("/trending/github", {"language": language, "since": since})
        
        if github_data and "items" in github_data:
            for repo in github_data["items"][:10]:
                with st.expander(f"⭐ {repo['full_name']} ({repo['stargazers_count']} stars)"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Description:** {repo.get('description', 'No description')}")
                        st.write(f"**Language:** {repo.get('language', 'N/A')}")
                        st.write(f"**URL:** {repo['html_url']}")
                    
                    with col2:
                        st.metric("⭐ Stars", repo['stargazers_count'])
                        st.metric("🍴 Forks", repo['forks_count'])
    
    with tab2:
        st.subheader("📰 Hacker News Top Stories")
        
        hn_data = fetch_data("/trending/hackernews", {"count": 20})
        
        if hn_data:
            for i, story in enumerate(hn_data[:10], 1):
                with st.expander(f"{i}. {story.get('title', 'No title')} ({story.get('score', 0)} points)"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if story.get('url'):
                            st.write(f"**URL:** {story['url']}")
                        st.write(f"**By:** {story.get('by', 'Unknown')}")
                        if story.get('time'):
                            time_str = datetime.fromtimestamp(story['time']).strftime("%Y-%m-%d %H:%M")
                            st.write(f"**Posted:** {time_str}")
                    
                    with col2:
                        st.metric("📊 Score", story.get('score', 0))
                        st.metric("💬 Comments", story.get('descendants', 0))
    
    with tab3:
        st.subheader("👨‍💻 Dev.to Trending")
        
        devto_data = fetch_data("/trending/devto")
        
        if devto_data:
            for article in devto_data[:10]:
                with st.expander(f"📝 {article.get('title', 'No title')}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Description:** {article.get('description', 'No description')}")
                        st.write(f"**Author:** {article.get('user', {}).get('name', 'Unknown')}")
                        st.write(f"**URL:** {article.get('url', 'N/A')}")
                        
                        # Tags
                        if article.get('tag_list'):
                            tags = ", ".join(article['tag_list'])
                            st.write(f"**Tags:** {tags}")
                    
                    with col2:
                        st.metric("❤️ Reactions", article.get('public_reactions_count', 0))
                        st.metric("💬 Comments", article.get('comments_count', 0))

def show_news_dashboard():
    """Display news dashboard"""
    st.header("📰 News Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["🗞️ Headlines", "💻 Tech News", "₿ Crypto News"])
    
    with tab1:
        st.subheader("🗞️ Top Headlines")
        
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("Country", ["us", "gb", "ca", "au", "de", "fr"])
        with col2:
            category = st.selectbox("Category", [None, "business", "entertainment", "health", "science", "sports", "technology"])
        
        headlines_data = fetch_data("/news/headlines", {"country": country, "category": category})
        
        if headlines_data and "articles" in headlines_data:
            for article in headlines_data["articles"][:10]:
                with st.expander(f"📰 {article.get('title', 'No title')}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                        st.write(f"**Description:** {article.get('description', 'No description')}")
                        if article.get('url'):
                            st.write(f"**[Read More]({article['url']})**")
                    
                    with col2:
                        if article.get('urlToImage'):
                            st.image(article['urlToImage'], width=200)
                        
                        if article.get('publishedAt'):
                            pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                            st.write(f"**Published:** {pub_date.strftime('%Y-%m-%d %H:%M')}")
    
    with tab2:
        st.subheader("💻 Technology News")
        
        tech_news = fetch_data("/news/tech")
        
        if tech_news:
            # Handle different response formats
            articles = tech_news.get("articles", tech_news.get("results", []))
            
            for article in articles[:10]:
                title = article.get('title', 'No title')
                with st.expander(f"💻 {title}"):
                    description = article.get('description', article.get('content', 'No description'))
                    source = article.get('source', {})
                    if isinstance(source, dict):
                        source_name = source.get('name', 'Unknown')
                    else:
                        source_name = str(source)
                    
                    st.write(f"**Source:** {source_name}")
                    st.write(f"**Description:** {description}")
                    
                    url = article.get('url', article.get('link'))
                    if url:
                        st.write(f"**[Read More]({url})**")
    
    with tab3:
        st.subheader("₿ Cryptocurrency News")
        
        crypto_news = fetch_data("/news/crypto")
        
        if crypto_news:
            # Handle CoinGecko news format
            articles = crypto_news.get("data", crypto_news)
            if isinstance(articles, list):
                for article in articles[:10]:
                    title = article.get('title', 'No title')
                    with st.expander(f"₿ {title}"):
                        st.write(f"**Description:** {article.get('description', 'No description')}")
                        
                        url = article.get('url')
                        if url:
                            st.write(f"**[Read More]({url})**")
                        
                        if article.get('created_at'):
                            created_at = datetime.fromisoformat(article['created_at'].replace('Z', '+00:00'))
                            st.write(f"**Published:** {created_at.strftime('%Y-%m-%d %H:%M')}")

def show_events_dashboard():
    """Display events dashboard"""
    st.header("📊 Events Dashboard")
    
    # Fetch recent events
    events_data = fetch_data("/events")
    
    if events_data and "events" in events_data:
        events = events_data["events"]
        
        # Event statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Events", len(events))
        
        with col2:
            api_calls = len([e for e in events if "API Call" in e.get("event", "")])
            st.metric("🔌 API Calls", api_calls)
        
        with col3:
            errors = len([e for e in events if "Error" in e.get("event", "")])
            st.metric("🚨 Errors", errors)
        
        with col4:
            page_views = len([e for e in events if "Page View" in e.get("event", "")])
            st.metric("👀 Page Views", page_views)
        
        # Events timeline
        st.subheader("📅 Recent Events")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            event_filter = st.selectbox("Filter Events", ["All", "API Call", "Error", "Page View", "Dashboard"])
        with col2:
            limit = st.slider("Number of Events", 10, 50, 20)
        
        # Filter events
        filtered_events = events
        if event_filter != "All":
            filtered_events = [e for e in events if event_filter in e.get("event", "")]
        
        # Display events
        for event in filtered_events[-limit:]:
            event_name = event.get("event", "Unknown Event")
            description = event.get("description", "No description")
            icon = event.get("icon", "📊")
            timestamp = event.get("timestamp", "")
            
            # Parse timestamp
            try:
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                else:
                    time_str = "Unknown"
            except:
                time_str = "Unknown"
            
            st.markdown(f"""
            <div class="event-item">
                <strong>{icon} {event_name}</strong> - {time_str}<br>
                <small>{description}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Log custom event
        st.subheader("📝 Log Custom Event")
        
        with st.form("log_event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                custom_event = st.text_input("Event Name")
                custom_description = st.text_area("Description")
            
            with col2:
                custom_icon = st.selectbox("Icon", ["📊", "🔔", "⚡", "🎉", "🚀", "⚠️", "✅", "❌"])
            
            if st.form_submit_button("Log Event"):
                if custom_event and custom_description:
                    # Send custom event to API
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/events/log",
                            params={
                                "event": custom_event,
                                "description": custom_description,
                                "icon": custom_icon
                            }
                        )
                        if response.status_code == 200:
                            st.success("Event logged successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Failed to log event")
                    except Exception as e:
                        st.error(f"Error logging event: {str(e)}")
                else:
                    st.warning("Please fill in both event name and description")

# Run the main function when script is executed
if __name__ == "__main__":
    main()
