"""
Debug progress bar functionality
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from unittest.mock import Mock

# הוספת נתיב
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.llm_models import LLMProvider, ProviderStatus
from services.llm_service import LLMService
from ui.components.llm.provider_card import ProviderCard


def debug_progress():
    """בדיקת פונקציונליות פס התקדמות"""
    app = QApplication([])
    
    # יצירת ספק לדוגמה
    provider = LLMProvider(
        name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        supported_models=["gpt-4"],
        connection_status=ProviderStatus.DISCONNECTED
    )
    
    # יצירת שירות מדומה
    mock_llm_service = Mock(spec=LLMService)
    mock_llm_service.get_provider.return_value = provider
    mock_llm_service.api_key_manager = Mock()
    
    # יצירת כרטיס
    card = ProviderCard(provider, mock_llm_service)
    
    print("Initial state:")
    print(f"Progress bar visible: {card.progress_bar.isVisible()}")
    print(f"Status message visible: {card.status_message.isVisible()}")
    
    # הצגת פס התקדמות
    print("\nCalling show_progress...")
    card.show_progress("Testing...")
    
    print("After show_progress:")
    print(f"Progress bar visible: {card.progress_bar.isVisible()}")
    print(f"Status message visible: {card.status_message.isVisible()}")
    print(f"Status message text: '{card.status_message.text()}'")
    
    # הסתרת פס התקדמות
    print("\nCalling hide_progress...")
    card.hide_progress()
    
    print("After hide_progress:")
    print(f"Progress bar visible: {card.progress_bar.isVisible()}")
    print(f"Status message visible: {card.status_message.isVisible()}")
    
    card.close()
    print("\n✅ Debug completed successfully!")


if __name__ == "__main__":
    debug_progress()
