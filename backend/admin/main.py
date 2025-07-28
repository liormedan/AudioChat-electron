"""
Admin Interface Server for Audio Chat Studio
ממשק ניהול לשרת עיבוד האודיו
"""

import os
import psutil
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app for admin
admin_app = FastAPI(
    title="Audio Chat Studio - Admin Interface",
    description="ממשק ניהול לשרת עיבוד האודיו",
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

# Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# --- System Monitoring ---
@admin_app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """דף הבית של ממשק הניהול"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@admin_app.get("/api/system/status")
async def get_system_status():
    """קבלת סטטוס המערכת"""
    try:
        # System info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process info
        current_process = psutil.Process()
        process_memory = current_process.memory_info()
        
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
            },
            "process": {
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": current_process.cpu_percent(),
                "num_threads": current_process.num_threads(),
                "create_time": current_process.create_time()
            }
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.get("/api/files/list")
async def list_uploaded_files():
    """רשימת קבצים שהועלו"""
    try:
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            return {"success": True, "files": []}
        
        files = []
        for file_path in uploads_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(file_path)
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "success": True,
            "files": files,
            "total_files": len(files),
            "total_size": sum(f["size"] for f in files)
        }
    except Exception as e:
        logger.error(f"List files error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """מחיקת קובץ"""
    try:
        file_path = Path("uploads") / filename
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return {"success": True, "message": f"File {filename} deleted"}
        else:
            return {"success": False, "error": "File not found"}
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.get("/api/logs")
async def get_recent_logs():
    """קבלת לוגים אחרונים"""
    try:
        # This is a simplified version - in production you'd read from actual log files
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Server is running",
                "module": "admin_server"
            },
            {
                "timestamp": (datetime.now()).isoformat(),
                "level": "INFO", 
                "message": "Audio processing service initialized",
                "module": "audio_service"
            }
        ]
        
        return {
            "success": True,
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Get logs error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.get("/api/stats")
async def get_server_stats():
    """סטטיסטיקות השרת"""
    try:
        # Mock statistics - in production these would come from actual metrics
        stats = {
            "requests_total": 150,
            "requests_today": 45,
            "files_processed": 23,
            "average_processing_time": 2.3,
            "uptime_seconds": 3600,
            "active_connections": 3,
            "errors_count": 2,
            "success_rate": 95.5
        }
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.post("/api/server/restart")
async def restart_server():
    """הפעלה מחדש של השרת (סימולציה)"""
    try:
        # In production, this would trigger an actual restart
        logger.info("Server restart requested")
        return {
            "success": True,
            "message": "Server restart initiated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Restart error: {e}")
        return {"success": False, "error": str(e)}

@admin_app.get("/api/config")
async def get_server_config():
    """קבלת הגדרות השרת"""
    try:
        config = {
            "server": {
                "host": "127.0.0.1",
                "port": 5000,
                "debug": True,
                "max_file_size": "100MB",
                "allowed_formats": ["mp3", "wav", "flac", "ogg", "m4a"]
            },
            "audio": {
                "sample_rate": 44100,
                "channels": 2,
                "bit_depth": 16
            },
            "processing": {
                "max_concurrent": 5,
                "timeout_seconds": 300,
                "temp_dir": "temp"
            }
        }
        
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        logger.error(f"Get config error: {e}")
        return {"success": False, "error": str(e)}

# Health check for admin interface
@admin_app.get("/health")
async def admin_health():
    """בדיקת תקינות ממשק הניהול"""
    return {
        "status": "healthy",
        "service": "admin_interface",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    # Run admin server on port 5001
    uvicorn.run(
        admin_app,
        host="127.0.0.1",
        port=5001,
        reload=False,
        log_level="info"
    )