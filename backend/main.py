#!/usr/bin/env python3
"""
Audio Chat Studio - Backend Main Entry Point
נקודת הכניסה הראשית לשרת הבקאנד
"""

import sys
import os
import logging
import uvicorn
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application
    הגדרת מערכת הלוגים לאפליקציה
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/backend.log', encoding='utf-8')
        ]
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Audio Chat Studio Backend Starting...")
    logger.info("מתחיל שרת הבקאנד של Audio Chat Studio")

def check_dependencies() -> bool:
    """
    Check if all required dependencies are available
    בדיקת זמינות כל התלויות הנדרשות
    """
    logger = logging.getLogger(__name__)
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'librosa',
        'soundfile',
        'pydub'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.debug(f"✅ Module {module} is available")
        except ImportError:
            missing_modules.append(module)
            logger.error(f"❌ Module {module} is missing")
    
    if missing_modules:
        logger.error(f"Missing required modules: {', '.join(missing_modules)}")
        logger.error("Please run: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies are available")
    return True

def create_directories() -> None:
    """
    Create necessary directories for the application
    יצירת התיקיות הנדרשות לאפליקציה
    """
    directories = [
        'data/uploads',
        'data/processed', 
        'data/temp',
        'data/cache',
        'logs/api',
        'logs/system'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info("📁 Created necessary directories")

def start_server(host: str = "127.0.0.1", port: int = 5000, reload: bool = False) -> None:
    """
    Start the FastAPI server with proper configuration
    הפעלת שרת FastAPI עם הגדרות נכונות
    
    Args:
        host: Server host address
        port: Server port number  
        reload: Enable auto-reload for development
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🌐 Starting server on http://{host}:{port}")
        logger.info(f"מפעיל שרת על http://{host}:{port}")
        
        # Import the FastAPI app from api module
        from backend.api.main import app
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        logger.error(f"שגיאה בהפעלת השרת: {e}")
        sys.exit(1)

def main() -> None:
    """
    Main entry point for the backend server
    נקודת הכניסה הראשית לשרת הבקאנד
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed. Exiting.")
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Audio Chat Studio Backend Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    # Update log level if specified
    if args.log_level != 'INFO':
        setup_logging(args.log_level)
    
    # Start the server
    start_server(host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()