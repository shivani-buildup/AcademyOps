from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db, engine, Base
from src.models import LeadModel
from src.schemas import LeadCreate, LeadUpdateStage, LeadResponse, MessageRequest, MessageResponse
from src.classifier import RuleBasedClassifier
from sqlalchemy.exc import IntegrityError
import logging

# Initialize DB schema
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AcademyOps API", version="1.0.0", docs_url=None, redoc_url=None)
classifier_instance = RuleBasedClassifier()

logging.basicConfig(filename='academyops.log', level=logging.INFO)

# --- Custom Premium UI HTML/CSS ---
ROOT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AcademyOps API Console</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0a1a;
            --card-bg: rgba(30, 27, 75, 0.25);
            --card-border: rgba(139, 92, 246, 0.15);
            --primary: #8b5cf6;
            --primary-glow: rgba(139, 92, 246, 0.35);
            --secondary: #3b82f6;
            --success: #10b981;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at top right, rgba(139, 92, 246, 0.12), transparent 40%),
                        radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.08), transparent 40%),
                        var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 2rem 1.5rem;
            overflow-x: hidden;
        }

        header {
            max-width: 1100px;
            width: 100%;
            margin: 0 auto 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-family: 'Outfit', sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-badge {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
            display: inline-block;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        main {
            max-width: 1100px;
            width: 100%;
            margin: 0 auto;
            flex-grow: 1;
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        .hero-section {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 3rem 2.5rem;
            backdrop-filter: blur(15px);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: -20%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.25), transparent 70%);
            z-index: 0;
            pointer-events: none;
        }

        .hero-section * {
            position: relative;
            z-index: 1;
        }

        .hero-section h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.8rem;
            letter-spacing: -0.02em;
        }

        .hero-section p {
            color: var(--text-muted);
            font-size: 1.1rem;
            max-width: 650px;
            margin-bottom: 2rem;
            line-height: 1.6;
        }

        .btn-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.8rem 1.6rem;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%);
            color: white;
            border: none;
            box-shadow: 0 4px 15px var(--primary-glow);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px var(--primary-glow);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-main);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 140px;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            border-color: rgba(139, 92, 246, 0.3);
        }

        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .stat-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            font-weight: 600;
        }

        .stat-icon {
            font-size: 1.4rem;
        }

        .stat-value {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            margin-top: 0.5rem;
        }

        .stat-footer {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 0.3rem;
        }

        .api-details {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }

        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1.2rem;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .endpoints-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        .endpoints-table th {
            padding: 0.8rem 1rem;
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .endpoints-table td {
            padding: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.9rem;
            vertical-align: middle;
        }

        .endpoints-table tr:last-child td {
            border-bottom: none;
        }

        .method-badge {
            display: inline-block;
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            text-align: center;
            width: 70px;
        }

        .method-badge.get { background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); }
        .method-badge.post { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
        .method-badge.patch { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
        .method-badge.delete { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }

        .path-text {
            font-family: monospace;
            color: #38bdf8;
            font-weight: 600;
        }

        footer {
            max-width: 1100px;
            width: 100%;
            margin: 2.5rem auto 0;
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 1.5rem;
        }

        @media (max-width: 768px) {
            body { padding: 1rem; }
            .hero-section { padding: 2rem 1.5rem; }
            .hero-section h1 { font-size: 2.2rem; }
            .endpoints-table th, .endpoints-table td { padding: 0.6rem 0.5rem; }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap" style="width:24px; height:24px; vertical-align:middle; display:inline-block; margin-right:8px;"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M6 12v5c0 2 3 3 6 3s6-1 6-3v-5"/><path d="M21.5 12v6"/></svg>AcademyOps API
        </div>
        <div class="status-badge">
            <span class="status-dot"></span> Server Active
        </div>
    </header>

    <main>
        <div class="hero-section">
            <h1>AcademyOps API Console</h1>
            <p>Welcome to the Lead-to-Enrollment Management System backend REST API console. Track marketing channels, manage lead pipelines, classify student messages, and optimize sales conversions.</p>
            <div class="btn-group">
                <a href="/docs" class="btn btn-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap" style="width:16px; height:16px; margin-right:6px; display:inline-block; vertical-align:middle;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Interactive Swagger Docs
                </a>
                <a href="/redoc" class="btn btn-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-text" style="width:16px; height:16px; margin-right:6px; display:inline-block; vertical-align:middle;"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>ReDoc Reference
                </a>
                <a href="http://localhost:8501" target="_blank" class="btn btn-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bar-chart3" style="width:16px; height:16px; margin-right:6px; display:inline-block; vertical-align:middle;"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>Streamlit Dashboard
                </a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Total Leads</span>
                    <span class="stat-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-users" style="width:20px; height:20px; display:block;"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>
                </div>
                <div class="stat-value" id="stat-total">-</div>
                <div class="stat-footer">Database registry</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Active Pipeline</span>
                    <span class="stat-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap" style="width:20px; height:20px; display:block;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span>
                </div>
                <div class="stat-value" id="stat-active">-</div>
                <div class="stat-footer">New, Contacted, Qualified, Demo</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Enrolled Leads</span>
                    <span class="stat-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check-circle" style="width:20px; height:20px; display:block;"><circle cx="12" cy="12" r="10"/><path d="m9 11 3 3 6-6"/></svg></span>
                </div>
                <div class="stat-value" id="stat-enrolled">-</div>
                <div class="stat-footer">Successfully converted</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Conversion Rate</span>
                    <span class="stat-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-target" style="width:20px; height:20px; display:block;"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></span>
                </div>
                <div class="stat-value" id="stat-rate">-%</div>
                <div class="stat-footer">Enrollment success rate</div>
            </div>
        </div>

        <div class="api-details">
            <div class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clipboard-list" style="width:22px; height:22px; margin-right:8px; display:inline-block; vertical-align:middle;"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6"/><path d="M9 16h6"/><path d="M9 8h6"/></svg>Key REST API Endpoints
            </div>
            <table class="endpoints-table">
                <thead>
                    <tr>
                        <th>Method</th>
                        <th>Endpoint Path</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="method-badge get">GET</span></td>
                        <td><span class="path-text">/api/v1/leads</span></td>
                        <td>List leads with support for filtering and pagination</td>
                    </tr>
                    <tr>
                        <td><span class="method-badge post">POST</span></td>
                        <td><span class="path-text">/api/v1/leads</span></td>
                        <td>Create a new lead (Name, Phone, Source)</td>
                    </tr>
                    <tr>
                        <td><span class="method-badge get">GET</span></td>
                        <td><span class="path-text">/api/v1/leads/{id}</span></td>
                        <td>Retrieve details of a specific lead by ID</td>
                    </tr>
                    <tr>
                        <td><span class="method-badge patch">PATCH</span></td>
                        <td><span class="path-text">/api/v1/leads/{id}/stage</span></td>
                        <td>Update pipeline stage of a lead (e.g. Qualified, Enrolled)</td>
                    </tr>
                    <tr>
                        <td><span class="method-badge post">POST</span></td>
                        <td><span class="path-text">/api/v1/leads/{id}/message</span></td>
                        <td>Classify lead's incoming message intent & get suggested response</td>
                    </tr>
                    <tr>
                        <td><span class="method-badge get">GET</span></td>
                        <td><span class="path-text">/api/v1/stats</span></td>
                        <td>Get real-time database counts and funnel statistics</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </main>

    <footer>
        AcademyOps v1.0.0 &copy; 2026 EasySkill Career Academy. All rights reserved.
    </footer>

    <script>
        async function fetchStats() {
            try {
                const response = await fetch('/api/v1/stats');
                const data = await response.json();
                
                document.getElementById('stat-total').innerText = data.total_leads;
                document.getElementById('stat-active').innerText = data.active_pipeline;
                document.getElementById('stat-enrolled').innerText = data.enrolled_leads;
                document.getElementById('stat-rate').innerText = data.conversion_rate.toFixed(1) + '%';
            } catch (error) {
                console.error('Error fetching stats:', error);
            }
        }
        
        fetchStats();
        setInterval(fetchStats, 10000);
    </script>
</body>
</html>
"""

SWAGGER_CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

body {
    background: radial-gradient(circle at top right, rgba(139, 92, 246, 0.04), transparent 45%),
                radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.02), transparent 45%),
                #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    margin: 0;
}

.swagger-ui {
    font-family: 'Inter', sans-serif !important;
    color: #334155 !important;
    background: transparent !important;
}

.swagger-ui .info {
    margin: 40px 0 !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
}

.swagger-ui .info .title {
    font-family: 'Outfit', sans-serif !important;
    color: #4f46e5 !important;
    font-weight: 800 !important;
    font-size: 2.5rem !important;
    background: linear-gradient(90deg, #4f46e5, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.swagger-ui .info .title small {
    display: inline-flex !important;
    align-items: center !important;
    vertical-align: middle !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    -webkit-text-fill-color: initial !important;
}

.swagger-ui .info .title .version {
    background: rgba(79, 70, 229, 0.1) !important;
    color: #4f46e5 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 4px 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    margin-left: 10px !important;
    -webkit-text-fill-color: #4f46e5 !important;
    display: inline-block !important;
}

.swagger-ui .info .title .version-stamp {
    background: rgba(16, 185, 129, 0.12) !important;
    color: #059669 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 4px 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    margin-left: 10px !important;
    -webkit-text-fill-color: #059669 !important;
    display: inline-flex !important;
    align-items: center !important;
}

.swagger-ui .info .title .version-stamp .version-type {
    color: #059669 !important;
    -webkit-text-fill-color: #059669 !important;
}

.swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info table, .swagger-ui .info a {
    color: #475569 !important;
    font-size: 0.95rem !important;
    line-height: 1.6;
}

.swagger-ui .scheme-container {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    margin-bottom: 30px !important;
}

.swagger-ui select {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 8px 30px 8px 12px !important;
}

.swagger-ui .opblock-tag {
    font-family: 'Outfit', sans-serif !important;
    color: #0f172a !important;
    font-size: 1.4rem !important;
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 10px 0 !important;
    margin-bottom: 15px !important;
}

.swagger-ui .opblock {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03) !important;
    margin-bottom: 15px !important;
    transition: all 0.2s ease !important;
    overflow: hidden;
}

.swagger-ui .opblock:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
}

.swagger-ui .opblock .opblock-summary {
    padding: 12px 20px !important;
}

.swagger-ui .opblock .opblock-summary-method {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    padding: 6px 14px !important;
    min-width: 80px;
    text-align: center;
}

.swagger-ui .opblock.opblock-get {
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
}
.swagger-ui .opblock.opblock-get:hover {
    border-color: #3b82f6 !important;
}
.swagger-ui .opblock.opblock-get .opblock-summary-method {
    background: #3b82f6 !important;
    color: #ffffff !important;
}
.swagger-ui .opblock.opblock-get .opblock-summary-path {
    color: #2563eb !important;
}

.swagger-ui .opblock.opblock-post {
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
}
.swagger-ui .opblock.opblock-post:hover {
    border-color: #10b981 !important;
}
.swagger-ui .opblock.opblock-post .opblock-summary-method {
    background: #10b981 !important;
    color: #ffffff !important;
}
.swagger-ui .opblock.opblock-post .opblock-summary-path {
    color: #059669 !important;
}

.swagger-ui .opblock.opblock-patch {
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
}
.swagger-ui .opblock.opblock-patch:hover {
    border-color: #f59e0b !important;
}
.swagger-ui .opblock.opblock-patch .opblock-summary-method {
    background: #f59e0b !important;
    color: #ffffff !important;
}
.swagger-ui .opblock.opblock-patch .opblock-summary-path {
    color: #d97706 !important;
}

.swagger-ui .opblock.opblock-delete {
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
}
.swagger-ui .opblock.opblock-delete:hover {
    border-color: #ef4444 !important;
}
.swagger-ui .opblock.opblock-delete .opblock-summary-method {
    background: #ef4444 !important;
    color: #ffffff !important;
}
.swagger-ui .opblock.opblock-delete .opblock-summary-path {
    color: #dc2626 !important;
}

.swagger-ui .opblock-summary-path {
    font-size: 1rem !important;
    font-family: monospace !important;
}

.swagger-ui .opblock-summary-description {
    color: #475569 !important;
    font-size: 0.9rem !important;
}

.swagger-ui .opblock-body {
    background: #ffffff !important;
    border-top: 1px solid #e2e8f0 !important;
}

.swagger-ui .opblock .opblock-section-header {
    background: #f8fafc !important;
    border-bottom: 1px solid #e2e8f0 !important;
}
.swagger-ui .opblock .opblock-section-header h4 {
    color: #0f172a !important;
}

.swagger-ui .btn.try-out__btn {
    border: 1px solid #6366f1 !important;
    color: #4f46e5 !important;
    background: rgba(99, 102, 241, 0.05) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.swagger-ui .btn.try-out__btn:hover {
    background: rgba(99, 102, 241, 0.1) !important;
}

.swagger-ui .btn.execute {
    background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
}
.swagger-ui .btn.execute:hover {
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.25) !important;
}

.swagger-ui .btn.cancel {
    background: rgba(239, 68, 68, 0.05) !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
    color: #ef4444 !important;
    border-radius: 8px !important;
}

.swagger-ui table thead tr td, .swagger-ui table thead tr th {
    border-bottom: 1px solid #e2e8f0 !important;
    color: #475569 !important;
}

.swagger-ui .response-col_status {
    color: #0f172a !important;
    font-weight: 700 !important;
}

.swagger-ui .response-col_description__wrapper {
    color: #334155 !important;
}

.swagger-ui .parameter__name {
    color: #0f172a !important;
    font-weight: 600 !important;
}
.swagger-ui .parameter__type {
    color: #4f46e5 !important;
}
.swagger-ui .parameter__in {
    color: #64748b !important;
}

.swagger-ui .opblock-body pre {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #0f172a !important;
}
.swagger-ui .opblock-body pre.microlight {
    background: #f8fafc !important;
}

.swagger-ui code {
    color: #b45309 !important;
}

.swagger-ui input[type=text] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    padding: 8px 12px !important;
}

.swagger-ui .models {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin-top: 30px !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
}

.swagger-ui .models h4 {
    font-family: 'Outfit', sans-serif !important;
    color: #0f172a !important;
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    border-bottom: 1px solid #f1f5f9 !important;
    margin: 0 0 20px 0 !important;
    padding-bottom: 12px !important;
}

.swagger-ui .models h4 svg {
    fill: #0f172a !important;
}

.swagger-ui .model-container {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin: 12px 0 !important;
    padding: 14px 20px !important;
    transition: all 0.2s ease !important;
}

.swagger-ui .model-container:hover {
    border-color: #cbd5e1 !important;
    background: #f1f5f9 !important;
}

.swagger-ui .model-box-control {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer !important;
}

.swagger-ui .model-box-control:focus {
    outline: none !important;
}

.swagger-ui .model-box-control .toggle-model-icon {
    fill: #64748b !important;
}

.swagger-ui .model-box {
    background: #ffffff !important;
    border: 1px solid #f1f5f9 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    width: 100% !important;
    margin-top: 10px !important;
}

.swagger-ui .model-box table {
    background: transparent !important;
}

.swagger-ui .models,
.swagger-ui .models span,
.swagger-ui .models div,
.swagger-ui .models button,
.swagger-ui .models table,
.swagger-ui .models td,
.swagger-ui .models th {
    color: #334155 !important;
    font-family: 'Inter', sans-serif !important;
}

.swagger-ui .models .model-title {
    color: #0f172a !important;
    font-weight: 700 !important;
}

.swagger-ui .models .prop-type {
    color: #059669 !important;
    font-weight: 600 !important;
}

.swagger-ui .models .prop-format {
    color: #64748b !important;
}

.swagger-ui .models code {
    color: #b45309 !important;
    background: #fffbeb !important;
    border: 1px solid #fef3c7 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

.swagger-ui .topbar {
    background-color: #ffffff !important;
    border-bottom: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
}

.swagger-ui .topbar .download-url-wrapper input[type=text] {
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #0f172a !important;
}

/* Override ALL microlight inline colors to readable values */
.swagger-ui pre.microlight {
    color: #0f172a !important;
    background: #f1f5f9 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
}

/* Nuke ALL inline green/lime/teal span colors -> deep indigo */
.swagger-ui pre.microlight span[style*="color: rgb(0, 128, 0)"],
.swagger-ui pre.microlight span[style*="color: rgb(0,128,0)"],
.swagger-ui pre.microlight span[style*="color:#008000"],
.swagger-ui pre.microlight span[style*="color: #008000"],
.swagger-ui pre.microlight span[style*="color: green"],
.swagger-ui pre.microlight span[style*="color:green"],
.swagger-ui pre.microlight span[style*="color: lime"],
.swagger-ui pre.microlight span[style*="color: rgb(16, 185, 129)"],
.swagger-ui pre.microlight span[style*="color:#10b981"],
.swagger-ui pre.microlight span[style*="color: #10b981"],
.swagger-ui pre.microlight span[style*="color: rgb(5, 150, 105)"],
.swagger-ui pre.microlight span[style*="color:#059669"],
.swagger-ui pre.microlight span[style*="color: #059669"],
.swagger-ui pre.microlight span[style*="color: rgb(0, 255, 0)"],
.swagger-ui pre.microlight span[style*="color: #00cc00"],
.swagger-ui pre.microlight span[style*="color: #00ff00"] {
    color: #3730a3 !important;
    -webkit-text-fill-color: #3730a3 !important;
}

/* Number values -> dark teal */
.swagger-ui pre.microlight span[style*="color: rgb(0, 0, 128)"],
.swagger-ui pre.microlight span[style*="color: rgb(0,0,128)"],
.swagger-ui pre.microlight span[style*="color:#000080"],
.swagger-ui pre.microlight span[style*="color: #000080"] {
    color: #0369a1 !important;
    -webkit-text-fill-color: #0369a1 !important;
}

/* Boolean/null -> dark amber */
.swagger-ui pre.microlight span[style*="color: rgb(0, 0, 255)"],
.swagger-ui pre.microlight span[style*="color: blue"],
.swagger-ui pre.microlight span[style*="color:#0000ff"] {
    color: #b45309 !important;
    -webkit-text-fill-color: #b45309 !important;
}
"""

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def get_root():
    return HTMLResponse(content=ROOT_HTML, status_code=200)

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui_html():
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="AcademyOps API - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )
    
    # Decode base response and inject our custom dark CSS styles + JS fix for microlight inline colors
    html_content = response.body.decode("utf-8")

    # JS that aggressively re-colors all microlight inline spans on every render
    js_fix = """
<script>
(function() {
    // Determine if a color string is any shade of green/lime/teal
    function isGreenish(c) {
        c = c.replace(/\\s+/g, '').toLowerCase();
        if (c === 'green' || c === 'lime' || c === '#008000' || c === '#00ff00' || c === '#0f0') return true;
        if (c === '#10b981' || c === '#059669' || c === '#00cc00' || c === '#34d399') return true;
        // rgb(...) patterns
        var m = c.match(/^rgb\\((\\d+),(\\d+),(\\d+)\\)$/);
        if (m) {
            var r = +m[1], g = +m[2], b = +m[3];
            // Greenish: green channel dominant AND reasonably saturated
            if (g > 100 && g > r * 1.4 && g > b * 1.4) return true;
            // Pure/near-pure green
            if (r === 0 && g === 128 && b === 0) return true;
        }
        return false;
    }

    function isNavyBlue(c) {
        c = c.replace(/\\s+/g, '').toLowerCase();
        if (c === '#000080') return true;
        var m = c.match(/^rgb\\((\\d+),(\\d+),(\\d+)\\)$/);
        if (m) { var r=+m[1],g=+m[2],b=+m[3]; return r===0 && g===0 && b===128; }
        return false;
    }

    function isBrightBlue(c) {
        c = c.replace(/\\s+/g, '').toLowerCase();
        if (c === 'blue' || c === '#0000ff' || c === '#00f') return true;
        var m = c.match(/^rgb\\((\\d+),(\\d+),(\\d+)\\)$/);
        if (m) { var r=+m[1],g=+m[2],b=+m[3]; return r===0 && g===0 && b===255; }
        return false;
    }

    function fixSpan(el) {
        var raw = el.style.color;
        if (!raw) return;
        if (isGreenish(raw)) {
            el.style.setProperty('color', '#3730a3', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#3730a3', 'important');
        } else if (isNavyBlue(raw)) {
            el.style.setProperty('color', '#0369a1', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#0369a1', 'important');
        } else if (isBrightBlue(raw)) {
            el.style.setProperty('color', '#b45309', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#b45309', 'important');
        }
    }

    function fixAll() {
        document.querySelectorAll('pre.microlight span, pre.microlight').forEach(fixSpan);
    }

    // MutationObserver: fires on every DOM change (Swagger re-renders on expand)
    var observer = new MutationObserver(function(mutations) {
        for (var i = 0; i < mutations.length; i++) {
            if (mutations[i].addedNodes.length || mutations[i].type === 'attributes') {
                fixAll();
                return;
            }
        }
    });

    function init() {
        if (document.body) {
            observer.observe(document.body, {
                childList: true, subtree: true,
                attributes: true, attributeFilter: ['style']
            });
            fixAll();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Safety net: re-run at increasing intervals after page load
    [100, 300, 600, 1200, 2500, 5000].forEach(function(ms) {
        setTimeout(fixAll, ms);
    });
})();
</script>
"""

    injection = f"<style>{SWAGGER_CUSTOM_CSS}</style>{js_fix}</head>"
    html_content = html_content.replace("</head>", injection)
    
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="AcademyOps API - ReDoc Reference",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.77/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/api/v1/stats", include_in_schema=True)
def get_api_stats(db: Session = Depends(get_db)):
    total = db.query(LeadModel).count()
    
    active_stages = ["New", "Contacted", "Qualified", "Demo"]
    active = db.query(LeadModel).filter(LeadModel.stage.in_(active_stages)).count()
    
    enrolled = db.query(LeadModel).filter(LeadModel.stage == "Enrolled").count()
    lost = db.query(LeadModel).filter(LeadModel.stage == "Lost").count()
    
    conversion_rate = (enrolled / total * 100) if total > 0 else 0.0
    
    stages = ["New", "Contacted", "Qualified", "Demo", "Enrolled", "Lost"]
    stage_counts = {}
    for s in stages:
        stage_counts[s] = db.query(LeadModel).filter(LeadModel.stage == s).count()
        
    return {
        "total_leads": total,
        "active_pipeline": active,
        "enrolled_leads": enrolled,
        "lost_leads": lost,
        "conversion_rate": conversion_rate,
        "stage_distribution": stage_counts
    }

@app.get("/api/v1/leads", response_model=List[LeadResponse])
def list_leads(
    stage: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(LeadModel)
    if stage:
        query = query.filter(LeadModel.stage == stage)
    if source:
        query = query.filter(LeadModel.source == source)
    
    offset = (page - 1) * limit
    leads = query.offset(offset).limit(limit).all()
    return leads

@app.get("/api/v1/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.post("/api/v1/leads", response_model=LeadResponse, status_code=201)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db_lead = LeadModel(
        name=lead.name,
        phone=lead.phone,
        source=lead.source,
        stage="New",
        notes=lead.notes
    )
    db.add(db_lead)
    try:
        db.commit()
        db.refresh(db_lead)
        logging.info(f"Created lead: {db_lead.phone}")
        return db_lead
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone number already exists")

@app.patch("/api/v1/leads/{lead_id}/stage", response_model=LeadResponse)
def update_lead_stage(lead_id: int, stage_update: LeadUpdateStage, db: Session = Depends(get_db)):
    valid_stages = ["New", "Contacted", "Qualified", "Demo", "Enrolled", "Lost"]
    if stage_update.stage not in valid_stages:
        raise HTTPException(status_code=400, detail="Invalid stage")
        
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead.stage = stage_update.stage
    db.commit()
    db.refresh(lead)
    logging.info(f"Updated lead {lead_id} to stage {stage_update.stage}")
    return lead

@app.delete("/api/v1/leads/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    logging.info(f"Deleted lead {lead_id}")
    return None

@app.post("/api/v1/leads/{lead_id}/message", response_model=MessageResponse)
def classify_message(lead_id: int, msg: MessageRequest, db: Session = Depends(get_db)):
    # Verify lead exists
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    result = classifier_instance.classify(msg.message)
    return result

