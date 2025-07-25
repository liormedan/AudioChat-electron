"""
בדיקת imports בסיסית
"""

import sys
import os

# הוספת נתיב
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from models.llm_models import LLMProvider, ProviderStatus
    print("✅ LLM models imported successfully")
    
    from services.llm_service import LLMService
    print("✅ LLM service imported successfully")
    
    from ui.components.llm.provider_card import ProviderCard
    print("✅ Provider card imported successfully")
    
    # יצירת ספק לדוגמה
    provider = LLMProvider(
        name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        supported_models=["gpt-4", "gpt-3.5-turbo"],
        connection_status=ProviderStatus.DISCONNECTED
    )
    print(f"✅ Provider created: {provider.name}")
    
    # יצירת שירות
    llm_service = LLMService()
    print("✅ LLM service created successfully")
    
    print("\n🎉 All imports and basic functionality work correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()