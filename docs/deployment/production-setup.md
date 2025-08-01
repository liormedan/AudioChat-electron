# 🚀 Production Deployment Guide

מדריך מקיף לפריסת Audio Chat Studio בסביבת ייצור.

## 📋 דרישות מערכת לייצור

### חומרה מינימלית
- **CPU**: Intel i5 / AMD Ryzen 5 או טוב יותר
- **RAM**: 8GB (מומלץ 16GB)
- **Storage**: 10GB פנויים (SSD מומלץ)
- **Network**: חיבור אינטרנט יציב

### חומרה מומלצת
- **CPU**: Intel i7 / AMD Ryzen 7 או טוב יותר
- **RAM**: 16GB או יותר
- **Storage**: 50GB פנויים (NVMe SSD)
- **GPU**: NVIDIA RTX 3060 או טוב יותר (אופציונלי)

### תוכנה נדרשת
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8+ (מומלץ 3.11)
- **Node.js**: 16+ (מומלץ 18 LTS)
- **Git**: Latest version
- **Visual C++ Redistributable**: Latest

## 🏗️ הכנה לפריסה

### 1. הורדה והתקנה

```bash
# הורד את הפרויקט
git clone <repository-url>
cd Audio-Chat-Studio

# הפעל התקנה מלאה
scripts\setup.bat

# בדוק התקנה
scripts\utils\health-check.bat
```

### 2. הגדרת סביבת ייצור

```bash
# צור קובץ הגדרות ייצור
copy config\settings.example.json config\production.json
```

**עריכת `config\production.json`:**
```json
{
  "environment": "production",
  "debug": false,
  "api": {
    "host": "0.0.0.0",
    "port": 5000,
    "workers": 4,
    "timeout": 60
  },
  "database": {
    "path": "data/production.db",
    "backup_interval": 3600,
    "max_connections": 20
  },
  "logging": {
    "level": "INFO",
    "max_file_size": "10MB",
    "backup_count": 5
  },
  "security": {
    "rate_limit": "10/minute",
    "max_session_age": 86400,
    "enable_cors": false
  },
  "performance": {
    "cache_enabled": true,
    "cache_ttl": 300,
    "max_message_length": 4000
  }
}
```

### 3. בנייה לייצור

```bash
# בנייה מלאה
scripts\build.bat

# בדיקת בנייה
scripts\final-integration-test.bat
```

## 🔧 הגדרות אבטחה

### 1. הגדרת חומת אש (Firewall)

```bash
# פתח פורט 5000 (אם נדרש)
netsh advfirewall firewall add rule name="Audio Chat Studio" dir=in action=allow protocol=TCP localport=5000

# הגבל גישה לרשת מקומית בלבד
netsh advfirewall firewall set rule name="Audio Chat Studio" new remoteip=192.168.0.0/16,10.0.0.0/8,172.16.0.0/12
```

### 2. הגדרת הרשאות

```bash
# צור משתמש מוגבל לשירות
net user audiochat /add /passwordreq:yes
net localgroup "Users" audiochat /add

# הגדר הרשאות לתיקיית הפרויקט
icacls "Audio-Chat-Studio" /grant audiochat:(OI)(CI)F
```

### 3. הצפנת נתונים

```python
# הוסף להגדרות
"encryption": {
    "enabled": true,
    "key_file": "config/encryption.key",
    "algorithm": "AES-256-GCM"
}
```

## 🚀 פריסה כשירות Windows

### 1. יצירת שירות Windows

צור קובץ `install-service.bat`:
```batch
@echo off
echo Installing Audio Chat Studio as Windows Service...

# התקן NSSM (Non-Sucking Service Manager)
if not exist "tools\nssm.exe" (
    echo Downloading NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath 'tools'"
    del nssm.zip
)

# התקן שירות
tools\nssm.exe install "AudioChatStudio" "%CD%\scripts\start-prod.bat"
tools\nssm.exe set "AudioChatStudio" DisplayName "Audio Chat Studio"
tools\nssm.exe set "AudioChatStudio" Description "AI-powered audio processing and chat system"
tools\nssm.exe set "AudioChatStudio" Start SERVICE_AUTO_START

# הפעל שירות
net start AudioChatStudio

echo Service installed and started successfully!
pause
```

### 2. הגדרת שירות

```bash
# הפעל התקנת שירות
install-service.bat

# בדוק סטטוס שירות
sc query AudioChatStudio

# הפעל/עצור שירות
net start AudioChatStudio
net stop AudioChatStudio
```

### 3. ניטור שירות

צור קובץ `monitor-service.bat`:
```batch
@echo off
:loop
sc query AudioChatStudio | findstr "RUNNING" > nul
if %errorlevel% neq 0 (
    echo Service stopped, restarting...
    net start AudioChatStudio
    echo %date% %time% - Service restarted >> logs\service-monitor.log
)
timeout /t 60 > nul
goto loop
```

## 📊 ניטור וביצועים

### 1. הגדרת לוגים

```python
# config/logging.json
{
    "version": 1,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/production.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "detailed"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "error_file"]
    }
}
```

### 2. ניטור ביצועים

צור קובץ `monitor-performance.py`:
```python
import psutil
import time
import json
import logging
from datetime import datetime

def monitor_system():
    """Monitor system performance and log metrics"""
    
    while True:
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Log metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
            
            # Write to metrics file
            with open('logs/metrics.jsonl', 'a') as f:
                f.write(json.dumps(metrics) + '\n')
            
            # Alert if resources are high
            if cpu_percent > 80 or memory_percent > 85:
                logging.warning(f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%")
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor_system()
```

### 3. דשבורד ניטור

צור קובץ `dashboard.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Audio Chat Studio - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { display: inline-block; margin: 10px; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
        .chart-container { width: 400px; height: 300px; margin: 20px; }
    </style>
</head>
<body>
    <h1>Audio Chat Studio - Production Dashboard</h1>
    
    <div id="metrics">
        <div class="metric">
            <h3>System Status</h3>
            <div id="status">Loading...</div>
        </div>
        <div class="metric">
            <h3>Active Sessions</h3>
            <div id="sessions">Loading...</div>
        </div>
        <div class="metric">
            <h3>Messages Today</h3>
            <div id="messages">Loading...</div>
        </div>
    </div>
    
    <div class="chart-container">
        <canvas id="cpuChart"></canvas>
    </div>
    
    <script>
        // Dashboard JavaScript
        async function updateDashboard() {
            try {
                // Fetch system health
                const health = await fetch('/api/health').then(r => r.json());
                document.getElementById('status').textContent = health.status;
                
                // Fetch session count
                const sessions = await fetch('/api/chat/sessions').then(r => r.json());
                document.getElementById('sessions').textContent = sessions.length;
                
                // Update every 30 seconds
                setTimeout(updateDashboard, 30000);
            } catch (error) {
                console.error('Dashboard update failed:', error);
            }
        }
        
        updateDashboard();
    </script>
</body>
</html>
```

## 🔄 גיבוי ושחזור

### 1. גיבוי אוטומטי

צור קובץ `backup.bat`:
```batch
@echo off
set BACKUP_DIR=backups\%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
mkdir "%BACKUP_DIR%" 2>nul

echo Creating backup...

# גבה בסיס נתונים
copy data\*.db "%BACKUP_DIR%\"

# גבה הגדרות
copy config\*.json "%BACKUP_DIR%\"

# גבה לוגים חשובים
copy logs\*.log "%BACKUP_DIR%\"

# דחוס גיבוי
powershell -Command "Compress-Archive -Path '%BACKUP_DIR%' -DestinationPath '%BACKUP_DIR%.zip'"
rmdir /s /q "%BACKUP_DIR%"

echo Backup created: %BACKUP_DIR%.zip

# נקה גיבויים ישנים (שמור 30 ימים)
forfiles /p backups /s /m *.zip /d -30 /c "cmd /c del @path" 2>nul
```

### 2. שחזור מגיבוי

צור קובץ `restore.bat`:
```batch
@echo off
echo Available backups:
dir backups\*.zip /b

set /p BACKUP_FILE="Enter backup filename: "

if not exist "backups\%BACKUP_FILE%" (
    echo Backup file not found!
    pause
    exit /b 1
)

echo Stopping service...
net stop AudioChatStudio 2>nul

echo Restoring from backup...
powershell -Command "Expand-Archive -Path 'backups\%BACKUP_FILE%' -DestinationPath 'temp_restore' -Force"

# שחזר קבצים
copy temp_restore\*.db data\
copy temp_restore\*.json config\

# נקה קבצים זמניים
rmdir /s /q temp_restore

echo Starting service...
net start AudioChatStudio

echo Restore completed!
pause
```

### 3. גיבוי לענן (אופציונלי)

```python
# cloud_backup.py
import boto3
import os
from datetime import datetime

def backup_to_s3():
    """Backup to AWS S3"""
    s3 = boto3.client('s3')
    bucket_name = 'audio-chat-studio-backups'
    
    # Create backup
    os.system('backup.bat')
    
    # Find latest backup
    backup_files = [f for f in os.listdir('backups') if f.endswith('.zip')]
    latest_backup = max(backup_files, key=lambda x: os.path.getctime(f'backups/{x}'))
    
    # Upload to S3
    key = f"backups/{datetime.now().strftime('%Y/%m/%d')}/{latest_backup}"
    s3.upload_file(f'backups/{latest_backup}', bucket_name, key)
    
    print(f"Backup uploaded to S3: {key}")

if __name__ == "__main__":
    backup_to_s3()
```

## 🔍 אבחון ופתרון בעיות בייצור

### 1. בדיקות בריאות אוטומטיות

```python
# health_check.py
import requests
import sqlite3
import psutil
import logging
from datetime import datetime

def comprehensive_health_check():
    """Perform comprehensive health check"""
    results = {}
    
    # API Health
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=5)
        results['api'] = response.status_code == 200
    except:
        results['api'] = False
    
    # Database Health
    try:
        conn = sqlite3.connect('data/production.db')
        conn.execute('SELECT 1')
        conn.close()
        results['database'] = True
    except:
        results['database'] = False
    
    # System Resources
    results['cpu_ok'] = psutil.cpu_percent() < 80
    results['memory_ok'] = psutil.virtual_memory().percent < 85
    results['disk_ok'] = psutil.disk_usage('.').percent < 90
    
    # Log results
    status = "HEALTHY" if all(results.values()) else "UNHEALTHY"
    logging.info(f"Health check: {status} - {results}")
    
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    comprehensive_health_check()
```

### 2. התראות אוטומטיות

```python
# alerts.py
import smtplib
from email.mime.text import MIMEText
import logging

def send_alert(subject, message):
    """Send email alert"""
    try:
        msg = MIMEText(message)
        msg['Subject'] = f"Audio Chat Studio Alert: {subject}"
        msg['From'] = "alerts@yourdomain.com"
        msg['To'] = "admin@yourdomain.com"
        
        server = smtplib.SMTP('localhost')
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Alert sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")

def check_and_alert():
    """Check system and send alerts if needed"""
    from health_check import comprehensive_health_check
    
    results = comprehensive_health_check()
    
    if not results['api']:
        send_alert("API Down", "The API service is not responding")
    
    if not results['database']:
        send_alert("Database Issue", "Database connection failed")
    
    if not results['cpu_ok']:
        send_alert("High CPU Usage", f"CPU usage is above 80%")

if __name__ == "__main__":
    check_and_alert()
```

## 📈 אופטימיזציה לביצועים

### 1. הגדרות בסיס נתונים

```sql
-- production_db_setup.sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456; -- 256MB

-- Create optimized indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_updated 
ON chat_sessions(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_timestamp 
ON chat_messages(session_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_content_fts 
ON chat_messages(content);

-- Analyze tables for query optimization
ANALYZE;
```

### 2. הגדרות שרת

```python
# production_server.py
import uvicorn
from backend.api.main import create_app

if __name__ == "__main__":
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        workers=4,  # Based on CPU cores
        loop="uvloop",  # Faster event loop
        http="httptools",  # Faster HTTP parser
        access_log=False,  # Disable for performance
        server_header=False,  # Security
        date_header=False,  # Performance
    )
```

### 3. קאש מתקדם

```python
# advanced_cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):
    """Advanced caching decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

## 🚀 הפעלה בייצור

### 1. סקריפט הפעלה סופי

```batch
@echo off
echo ========================================
echo Audio Chat Studio - Production Startup
echo ========================================

# בדיקות קדם הפעלה
echo [1/5] Pre-flight checks...
if not exist "data\production.db" (
    echo Creating production database...
    python scripts\create_production_db.py
)

echo [2/5] Starting monitoring...
start /b python monitor-performance.py

echo [3/5] Starting backup scheduler...
schtasks /create /tn "AudioChatBackup" /tr "%CD%\backup.bat" /sc daily /st 02:00 /f

echo [4/5] Starting health checks...
start /b python health_check.py

echo [5/5] Starting main service...
net start AudioChatStudio

echo.
echo ✅ Production system started successfully!
echo.
echo Dashboard: http://127.0.0.1:5000/dashboard.html
echo API Docs: http://127.0.0.1:5000/docs
echo Logs: logs\production.log
echo.

pause
```

### 2. בדיקה סופית

```bash
# הפעל בדיקה מקיפה
scripts\final-integration-test.bat

# בדוק שירותים
sc query AudioChatStudio

# בדוק לוגים
type logs\production.log | findstr "ERROR"

# בדוק ביצועים
python monitor-performance.py --check-once
```

## 📚 תיעוד נוסף

- [מדריך משתמש](../user/chat-user-guide.md)
- [API Documentation](../api/chat-api.md)
- [Troubleshooting Guide](../troubleshooting.md)
- [Performance Guide](../../backend/services/database/PERFORMANCE_GUIDE.md)

---

**Audio Chat Studio** מוכן לייצור! 🚀✨