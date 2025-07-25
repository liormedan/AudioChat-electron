import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_models import (
    LLMProvider, LLMModel, UsageRecord, LLMParameters,
    ProviderStatus, ModelCapability
)


class LLMService(QObject):
    """שירות לניהול מודלי LLM"""
    
    # אותות
    provider_connected = pyqtSignal(str)  # provider_name
    provider_disconnected = pyqtSignal(str)  # provider_name
    model_activated = pyqtSignal(str)  # model_id
    usage_recorded = pyqtSignal(object)  # UsageRecord
    
    def __init__(self, db_path: str = None):
        """
        יוצר שירות LLM חדש
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים
        """
        super().__init__()
        
        # נתיב למסד הנתונים
        if db_path is None:
            app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "llm_data.db")
        
        self.db_path = db_path
        
        # יצירת מסד נתונים אם לא קיים
        self._init_db()
        
        # מודל פעיל נוכחי
        self.active_model: Optional[LLMModel] = None
        
        # פרמטרים נוכחיים
        self.current_parameters = LLMParameters()
        
        # טעינת ספקים ברירת מחדל
        self._init_default_providers()
    
    def _init_db(self) -> None:
        """יצירת מסד נתונים אם לא קיים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת ספקים
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_providers (
            name TEXT PRIMARY KEY,
            api_base_url TEXT NOT NULL,
            supported_models TEXT NOT NULL,
            api_key TEXT,
            is_connected BOOLEAN DEFAULT FALSE,
            connection_status TEXT DEFAULT 'disconnected',
            last_test_date TEXT,
            error_message TEXT,
            rate_limit INTEGER,
            cost_per_1k_tokens REAL,
            metadata TEXT DEFAULT '{}'
        )
        ''')
        
        # טבלת מודלים
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            description TEXT,
            max_tokens INTEGER NOT NULL,
            cost_per_token REAL NOT NULL,
            capabilities TEXT NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
            is_available BOOLEAN DEFAULT TRUE,
            context_window INTEGER DEFAULT 4096,
            training_data_cutoff TEXT,
            version TEXT,
            parameters TEXT DEFAULT '{}',
            metadata TEXT DEFAULT '{}'
        )
        ''')
        
        # טבלת שימוש
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            model_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            tokens_used INTEGER NOT NULL,
            cost REAL NOT NULL,
            response_time REAL NOT NULL,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            request_type TEXT DEFAULT 'chat',
            user_id TEXT,
            session_id TEXT,
            metadata TEXT DEFAULT '{}'
        )
        ''')
        
        # טבלת הגדרות
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_default_providers(self) -> None:
        """יצירת ספקים ברירת מחדל"""
        default_providers = [
            {
                "name": "OpenAI",
                "api_base_url": "https://api.openai.com/v1",
                "supported_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "rate_limit": 3500,
                "cost_per_1k_tokens": 0.03
            },
            {
                "name": "Anthropic",
                "api_base_url": "https://api.anthropic.com/v1",
                "supported_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "rate_limit": 1000,
                "cost_per_1k_tokens": 0.015
            },
            {
                "name": "Google",
                "api_base_url": "https://generativelanguage.googleapis.com/v1",
                "supported_models": ["gemini-pro", "gemini-pro-vision"],
                "rate_limit": 60,
                "cost_per_1k_tokens": 0.001
            },
            {
                "name": "Cohere",
                "api_base_url": "https://api.cohere.ai/v1",
                "supported_models": ["command", "command-light"],
                "rate_limit": 1000,
                "cost_per_1k_tokens": 0.002
            }
        ]
        
        for provider_data in default_providers:
            if not self.get_provider(provider_data["name"]):
                provider = LLMProvider(
                    name=provider_data["name"],
                    api_base_url=provider_data["api_base_url"],
                    supported_models=provider_data["supported_models"],
                    rate_limit=provider_data["rate_limit"],
                    cost_per_1k_tokens=provider_data["cost_per_1k_tokens"]
                )
                self.save_provider(provider)
        
        # יצירת מודלים ברירת מחדל
        self._init_default_models()
    
    def _init_default_models(self) -> None:
        """יצירת מודלים ברירת מחדל"""
        default_models = [
            {
                "id": "openai-gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "description": "מודל שפה מתקדם עם יכולות חזקות בהבנה ויצירה",
                "max_tokens": 8192,
                "cost_per_token": 0.00003,
                "capabilities": [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT, ModelCapability.CODE_GENERATION],
                "context_window": 8192
            },
            {
                "id": "openai-gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "description": "מודל מהיר וחסכוני לשיחות ויצירת טקסט",
                "max_tokens": 4096,
                "cost_per_token": 0.000002,
                "capabilities": [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
                "context_window": 4096
            },
            {
                "id": "anthropic-claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "description": "מודל מתקדם עם יכולות חזקות בניתוח ויצירה",
                "max_tokens": 4096,
                "cost_per_token": 0.000015,
                "capabilities": [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT, ModelCapability.SUMMARIZATION],
                "context_window": 200000
            },
            {
                "id": "google-gemini-pro",
                "name": "Gemini Pro",
                "provider": "Google",
                "description": "מודל רב-תכליתי של Google",
                "max_tokens": 2048,
                "cost_per_token": 0.000001,
                "capabilities": [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
                "context_window": 32768
            }
        ]
        
        for model_data in default_models:
            if not self.get_model(model_data["id"]):
                model = LLMModel(
                    id=model_data["id"],
                    name=model_data["name"],
                    provider=model_data["provider"],
                    description=model_data["description"],
                    max_tokens=model_data["max_tokens"],
                    cost_per_token=model_data["cost_per_token"],
                    capabilities=model_data["capabilities"],
                    context_window=model_data["context_window"]
                )
                self.save_model(model)
    
    # Provider Management
    def save_provider(self, provider: LLMProvider) -> None:
        """שמירת ספק במסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO llm_providers 
        (name, api_base_url, supported_models, api_key, is_connected, connection_status,
         last_test_date, error_message, rate_limit, cost_per_1k_tokens, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            provider.name,
            provider.api_base_url,
            json.dumps(provider.supported_models),
            provider.api_key,
            provider.is_connected,
            provider.connection_status.value,
            provider.last_test_date.isoformat() if provider.last_test_date else None,
            provider.error_message,
            provider.rate_limit,
            provider.cost_per_1k_tokens,
            json.dumps(provider.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """קבלת ספק לפי שם"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM llm_providers WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return LLMProvider(
            name=row[0],
            api_base_url=row[1],
            supported_models=json.loads(row[2]),
            api_key=row[3],
            is_connected=bool(row[4]),
            connection_status=ProviderStatus(row[5]),
            last_test_date=datetime.fromisoformat(row[6]) if row[6] else None,
            error_message=row[7],
            rate_limit=row[8],
            cost_per_1k_tokens=row[9],
            metadata=json.loads(row[10]) if row[10] else {}
        )
    
    def get_all_providers(self) -> List[LLMProvider]:
        """קבלת כל הספקים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM llm_providers ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        providers = []
        for row in rows:
            provider = LLMProvider(
                name=row[0],
                api_base_url=row[1],
                supported_models=json.loads(row[2]),
                api_key=row[3],
                is_connected=bool(row[4]),
                connection_status=ProviderStatus(row[5]),
                last_test_date=datetime.fromisoformat(row[6]) if row[6] else None,
                error_message=row[7],
                rate_limit=row[8],
                cost_per_1k_tokens=row[9],
                metadata=json.loads(row[10]) if row[10] else {}
            )
            providers.append(provider)
        
        return providers
    
    def test_provider_connection(self, provider_name: str) -> bool:
        """בדיקת חיבור לספק"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        # עדכון סטטוס לבדיקה
        provider.connection_status = ProviderStatus.TESTING
        self.save_provider(provider)
        
        # בדיקת חיבור
        success = provider.test_connection()
        
        # שמירת תוצאה
        self.save_provider(provider)
        
        # שליחת אות
        if success:
            self.provider_connected.emit(provider_name)
        else:
            self.provider_disconnected.emit(provider_name)
        
        return success
    
    # Model Management
    def save_model(self, model: LLMModel) -> None:
        """שמירת מודל במסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO llm_models 
        (id, name, provider, description, max_tokens, cost_per_token, capabilities,
         is_active, is_available, context_window, training_data_cutoff, version, parameters, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model.id,
            model.name,
            model.provider,
            model.description,
            model.max_tokens,
            model.cost_per_token,
            json.dumps([cap.value for cap in model.capabilities]),
            model.is_active,
            model.is_available,
            model.context_window,
            model.training_data_cutoff,
            model.version,
            json.dumps(model.parameters),
            json.dumps(model.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_model(self, model_id: str) -> Optional[LLMModel]:
        """קבלת מודל לפי ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM llm_models WHERE id = ?', (model_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        capabilities = [ModelCapability(cap) for cap in json.loads(row[6])]
        
        return LLMModel(
            id=row[0],
            name=row[1],
            provider=row[2],
            description=row[3],
            max_tokens=row[4],
            cost_per_token=row[5],
            capabilities=capabilities,
            is_active=bool(row[7]),
            is_available=bool(row[8]),
            context_window=row[9],
            training_data_cutoff=row[10],
            version=row[11],
            parameters=json.loads(row[12]) if row[12] else {},
            metadata=json.loads(row[13]) if row[13] else {}
        )
    
    def get_models_by_provider(self, provider_name: str) -> List[LLMModel]:
        """קבלת מודלים לפי ספק"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM llm_models WHERE provider = ? ORDER BY name', (provider_name,))
        rows = cursor.fetchall()
        conn.close()
        
        models = []
        for row in rows:
            capabilities = [ModelCapability(cap) for cap in json.loads(row[6])]
            
            model = LLMModel(
                id=row[0],
                name=row[1],
                provider=row[2],
                description=row[3],
                max_tokens=row[4],
                cost_per_token=row[5],
                capabilities=capabilities,
                is_active=bool(row[7]),
                is_available=bool(row[8]),
                context_window=row[9],
                training_data_cutoff=row[10],
                version=row[11],
                parameters=json.loads(row[12]) if row[12] else {},
                metadata=json.loads(row[13]) if row[13] else {}
            )
            models.append(model)
        
        return models
    
    def get_all_models(self) -> List[LLMModel]:
        """קבלת כל המודלים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM llm_models ORDER BY provider, name')
        rows = cursor.fetchall()
        conn.close()
        
        models = []
        for row in rows:
            capabilities = [ModelCapability(cap) for cap in json.loads(row[6])]
            
            model = LLMModel(
                id=row[0],
                name=row[1],
                provider=row[2],
                description=row[3],
                max_tokens=row[4],
                cost_per_token=row[5],
                capabilities=capabilities,
                is_active=bool(row[7]),
                is_available=bool(row[8]),
                context_window=row[9],
                training_data_cutoff=row[10],
                version=row[11],
                parameters=json.loads(row[12]) if row[12] else {},
                metadata=json.loads(row[13]) if row[13] else {}
            )
            models.append(model)
        
        return models
    
    def set_active_model(self, model_id: str) -> bool:
        """הגדרת מודל פעיל"""
        # איפוס כל המודלים
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE llm_models SET is_active = FALSE')
        
        # הגדרת המודל החדש כפעיל
        cursor.execute('UPDATE llm_models SET is_active = TRUE WHERE id = ?', (model_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            self.active_model = self.get_model(model_id)
            self.model_activated.emit(model_id)
        
        return success
    
    def get_active_model(self) -> Optional[LLMModel]:
        """קבלת המודל הפעיל"""
        if self.active_model:
            return self.active_model
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM llm_models WHERE is_active = TRUE LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        capabilities = [ModelCapability(cap) for cap in json.loads(row[6])]
        
        self.active_model = LLMModel(
            id=row[0],
            name=row[1],
            provider=row[2],
            description=row[3],
            max_tokens=row[4],
            cost_per_token=row[5],
            capabilities=capabilities,
            is_active=bool(row[7]),
            is_available=bool(row[8]),
            context_window=row[9],
            training_data_cutoff=row[10],
            version=row[11],
            parameters=json.loads(row[12]) if row[12] else {},
            metadata=json.loads(row[13]) if row[13] else {}
        )
        
        return self.active_model
    
    # Parameters Management
    def set_parameters(self, parameters: LLMParameters) -> bool:
        """הגדרת פרמטרים"""
        if not parameters.validate():
            return False
        
        self.current_parameters = parameters
        
        # שמירה במסד הנתונים
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO llm_settings (key, value, updated_at)
        VALUES (?, ?, ?)
        ''', ("current_parameters", json.dumps(parameters.to_dict()), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_parameters(self) -> LLMParameters:
        """קבלת פרמטרים נוכחיים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM llm_settings WHERE key = ?', ("current_parameters",))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                params_data = json.loads(row[0])
                self.current_parameters = LLMParameters.from_dict(params_data)
            except:
                pass
        
        return self.current_parameters