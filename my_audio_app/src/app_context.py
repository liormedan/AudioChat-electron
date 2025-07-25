from services import LLMService, SettingsService, ChatService, ProfileService

# Global application services
settings_service = SettingsService()
llm_service = LLMService()
chat_service = ChatService(llm_service=llm_service)
profile_service = ProfileService()
