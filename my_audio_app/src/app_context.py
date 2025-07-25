from services import LLMService, SettingsService, ChatService

# Global application services
settings_service = SettingsService()
llm_service = LLMService()
chat_service = ChatService(llm_service=llm_service)
