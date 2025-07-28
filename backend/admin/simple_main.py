"""
Simple Admin Interface Server
ממשק ניהול פשוט ללא תלויות מורכבות
"""

import os
import psutil
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app for admin
admin_app = FastAPI(
    title="Audio Chat Studio - Simple Admin",
    description="Simple admin interface",
    version="1.0.0"
)

# Configure CORS
admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple HTML template
SIMPLE_ADMIN_HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Chat Studio - ממשק ניהול פשוט</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .status-online {
            color: #28a745;
            font-weight: bold;
        }
        .status-offline {
            color: #dc3545;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Audio Chat Studio - ממשק ניהול</h1>
            <p>מוניטורינג פשוט של המערכת</p>
        </div>

        <div class="status-grid">
            <div class="card">
                <h3>🖥️ סטטוס מערכת</h3>
                <p>CPU: <span id="cpu-usage">טוען...</span></p>
                <p>זיכרון: <span id="memory-usage">טוען...</span></p>
                <p>דיסק: <span id="disk-usage">טוען...</span></p>
            </div>

            <div class="card">
                <h3>🌐 שרתים</h3>
                <p>API Server: <span id="api-status" class="status-online">פעיל</span></p>
                <p>Admin Interface: <span class="status-online">פעיל</span></p>
                <p>זמן הפעלה: <span id="uptime">טוען...</span></p>
            </div>

            <div class="card">
                <h3>📊 סטטיסטיקות</h3>
                <p>בקשות כולל: <span id="total-requests">0</span></p>
                <p>קבצים עובדו: <span id="files-processed">0</span></p>
                <p>שגיאות: <span id="errors">0</span></p>
            </div>

            <div class="card">
                <h3>⚡ פעולות מהירות</h3>
                <button class="btn" onclick="refreshData()">🔄 רענון</button>
                <button class="btn" onclick="testAPI()">🧪 בדיקת API</button>
                <button class="btn" onclick="viewLogs()">📋 לוגים</button>
            </div>
        </div>

        <div class="card">
            <h3>📱 קישורים מהירים</h3>
            <a href="http://127.0.0.1:5000/docs" target="_blank" class="btn">📚 Swagger UI</a>
            <a href="http://127.0.0.1:5000" target="_blank" class="btn">🔧 API</a>
            <button class="btn" onclick="openElectronApp()">🖥️ אפליקציה</button>
        </div>
    </div>

    <script>
        // Auto refresh every 5 seconds
        setInterval(refreshData, 5000);
        
        // Initial load
        refreshData();

        async function refreshData() {
            try {
                const response = await fetch('/api/system/status');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('cpu-usage').textContent = data.system.cpu_percent.toFixed(1) + '%';
                    document.getElementById('memory-usage').textContent = data.system.memory.percent.toFixed(1) + '%';
                    document.getElementById('disk-usage').textContent = data.system.disk.percent.toFixed(1) + '%';
                }
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        async function testAPI() {
            try {
                const response = await fetch('http://127.0.0.1:5000/health');
                const data = await response.json();
                
                if (data.status === 'healthy') {
                    alert('✅ API עובד תקין!');
                    document.getElementById('api-status').textContent = 'פעיל';
                    document.getElementById('api-status').className = 'status-online';
                } else {
                    alert('⚠️ בעיה ב-API');
                    document.getElementById('api-status').textContent = 'בעיה';
                    document.getElementById('api-status').className = 'status-offline';
                }
            } catch (error) {
                alert('❌ שגיאה בחיבור ל-API: ' + error.message);
                document.getElementById('api-status').textContent = 'לא זמין';
                document.getElementById('api-status').className = 'status-offline';
            }
        }

        function viewLogs() {
            alert('תכונת לוגים תתווסף בגרסה הבאה');
        }

        function openElectronApp() {
            window.open('http://127.0.0.1:3000', '_blank');
        }
    </script>
</body>
</html>
"""

# --- Routes ---
@admin_app.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    """דף הבית של ממשק הניהול"""
    return HTMLResponse(content=SIMPLE_ADMIN_HTML)

@admin_app.get("/api/system/status")
async def get_system_status():
    """קבלת סטטוס המערכת"""
    try:
        # System info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "used": disk.used,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.get("/health")
async def admin_health():
    """בדיקת תקינות ממשק הניהול"""
    return {
        "status": "healthy",
        "service": "simple_admin_interface",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run admin server on port 5001
    uvicorn.run(
        "simple_main:admin_app",
        host="127.0.0.1",
        port=5001,
        reload=True,
        log_level="info"
    )