# Secure API Key Management Guide

## Overview

The secure API key management system provides encrypted storage and management of API keys for various LLM providers. This system ensures that sensitive credentials are stored securely and can be managed through a user-friendly interface.

## Features

### 🔐 Security Features
- **AES Encryption**: All API keys are encrypted using Fernet (AES 128) encryption
- **Salt-based Protection**: Each key uses a unique salt for additional security
- **Secure Deletion**: Keys are securely removed from storage with confirmation
- **Key Rotation**: Support for rotating API keys with history tracking
- **Master Password**: Automatic generation and management of encryption keys

### 🔑 Key Management
- **Multi-Provider Support**: OpenAI, Anthropic, Google, Cohere, and more
- **Format Validation**: Automatic validation of API key formats per provider
- **Connection Testing**: Built-in connection testing with response time tracking
- **Usage Tracking**: Monitor when keys were last used and tested
- **History Logging**: Complete audit trail of key operations

### 🛡️ Data Protection
- **Local Storage**: All data stored locally in encrypted SQLite database
- **No Cloud Dependencies**: No external services required for key management
- **Automatic Cleanup**: Configurable cleanup of old test data and history
- **Export/Import**: Secure backup and restore functionality

## Architecture

### Core Components

1. **APIKeyManager**: Main service for encrypted key storage and retrieval
2. **APIKeyDialog**: User interface for key management
3. **LLMService Integration**: Seamless integration with existing LLM service
4. **Connection Testing**: Automated testing and validation

### Database Schema

```sql
-- Encrypted API keys storage
CREATE TABLE encrypted_api_keys (
    provider_name TEXT PRIMARY KEY,
    encrypted_key TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_used TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    key_hash TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'
);

-- Key rotation history
CREATE TABLE key_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    deactivated_at TEXT,
    reason TEXT DEFAULT 'rotation'
);

-- Connection test results
CREATE TABLE connection_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT NOT NULL,
    test_time TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    response_time REAL,
    error_message TEXT,
    test_type TEXT DEFAULT 'manual'
);
```

## Usage Guide

### Basic Usage

```python
from services.api_key_manager import APIKeyManager

# Initialize the manager
api_key_manager = APIKeyManager()

# Store an API key
success = api_key_manager.store_api_key("OpenAI", "sk-your-api-key-here")

# Retrieve an API key
api_key = api_key_manager.retrieve_api_key("OpenAI")

# Test connection
success, message, response_time = api_key_manager.test_api_key_connection("OpenAI")

# Delete a key
success = api_key_manager.delete_api_key("OpenAI")
```

### Integration with LLM Service

```python
from services.llm_service import LLMService

# Initialize LLM service (includes API key manager)
llm_service = LLMService()

# Set API key for a provider
llm_service.set_provider_api_key("OpenAI", "sk-your-api-key-here")

# Test provider connection
success, message, response_time = llm_service.test_provider_connection_secure("OpenAI")

# Get security status
status = llm_service.get_api_key_security_status()
```

### Using the UI Dialog

```python
from ui.components.llm.api_key_dialog import APIKeyDialog
from services.api_key_manager import APIKeyManager

# Create manager and dialog
api_key_manager = APIKeyManager()
dialog = APIKeyDialog("OpenAI", api_key_manager, parent_widget)

# Show dialog
if dialog.exec() == QDialog.DialogCode.Accepted:
    api_key = dialog.get_api_key()
    print(f"API key configured: {api_key is not None}")
```

## API Reference

### APIKeyManager Class

#### Core Methods

- `store_api_key(provider_name: str, api_key: str, metadata: Dict = None) -> bool`
  - Stores an encrypted API key for the specified provider
  - Returns True if successful

- `retrieve_api_key(provider_name: str) -> Optional[str]`
  - Retrieves and decrypts an API key for the specified provider
  - Returns the decrypted key or None if not found

- `delete_api_key(provider_name: str) -> bool`
  - Securely deletes an API key for the specified provider
  - Returns True if successful

- `rotate_api_key(provider_name: str, new_api_key: str) -> bool`
  - Rotates an API key, storing the old one in history
  - Returns True if successful

#### Validation Methods

- `validate_api_key_format(provider_name: str, api_key: str) -> Tuple[bool, str]`
  - Validates API key format for the specified provider
  - Returns (is_valid, error_message)

- `test_api_key_connection(provider_name: str, api_key: str = None) -> Tuple[bool, str, float]`
  - Tests connection using the API key
  - Returns (success, message, response_time)

#### Information Methods

- `list_stored_providers() -> List[Dict]`
  - Returns list of providers with stored keys

- `get_security_status() -> Dict`
  - Returns security status information

- `get_connection_test_history(provider_name: str, limit: int = 10) -> List[Dict]`
  - Returns connection test history for a provider

#### Maintenance Methods

- `cleanup_old_data(days_to_keep: int = 90) -> None`
  - Removes old test data and history

- `export_settings(include_keys: bool = False) -> Dict`
  - Exports settings (optionally including encrypted keys)

### APIKeyDialog Class

#### Constructor
- `APIKeyDialog(provider_name: str, api_key_manager: APIKeyManager, parent=None)`

#### Key Methods
- `get_api_key() -> Optional[str]` - Returns the configured API key
- `exec() -> int` - Shows the dialog and returns result code

### LLMService Integration Methods

- `set_provider_api_key(provider_name: str, api_key: str) -> bool`
- `get_provider_api_key(provider_name: str) -> Optional[str]`
- `test_provider_connection_secure(provider_name: str) -> Tuple[bool, str, float]`
- `remove_provider_api_key(provider_name: str) -> bool`
- `rotate_provider_api_key(provider_name: str, new_api_key: str) -> bool`
- `get_api_key_security_status() -> Dict`
- `validate_provider_api_key_format(provider_name: str, api_key: str) -> Tuple[bool, str]`
- `get_stored_api_key_providers() -> List[Dict]`
- `cleanup_old_api_key_data(days_to_keep: int = 90) -> None`

## Provider-Specific Information

### OpenAI
- **Format**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Minimum Length**: 40 characters
- **Documentation**: https://platform.openai.com/api-keys

### Anthropic
- **Format**: `sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Minimum Length**: 50 characters
- **Documentation**: https://console.anthropic.com/

### Google AI
- **Format**: `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Minimum Length**: 30 characters
- **Documentation**: https://makersuite.google.com/app/apikey

### Cohere
- **Format**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Minimum Length**: 40 characters
- **Documentation**: https://dashboard.cohere.ai/api-keys

## Security Best Practices

### For Developers

1. **Never Log API Keys**: Ensure API keys are never written to logs
2. **Use Secure Storage**: Always use the APIKeyManager for storage
3. **Validate Input**: Always validate API key formats before storage
4. **Test Connections**: Verify keys work before saving
5. **Handle Errors**: Provide clear error messages for key issues

### For Users

1. **Keep Keys Private**: Never share API keys with others
2. **Rotate Regularly**: Change API keys periodically
3. **Monitor Usage**: Check connection test history regularly
4. **Secure Backup**: Use export functionality for secure backups
5. **Clean Up**: Remove unused keys promptly

## Troubleshooting

### Common Issues

1. **"API key format is invalid"**
   - Check the key format matches the provider requirements
   - Ensure no extra spaces or characters

2. **"Connection test failed"**
   - Verify the API key is correct and active
   - Check internet connection
   - Confirm provider service is available

3. **"Failed to decrypt API key"**
   - Database may be corrupted
   - Try deleting and re-adding the key

4. **"No API key stored"**
   - Key may have been deleted or never added
   - Use the management dialog to add a new key

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export AUDIO_CHAT_DEBUG=1
```

## Examples

See the following example files:
- `examples/api_key_management_example.py` - Basic API key management
- `examples/llm_with_secure_keys_example.py` - Full LLM service integration
- `tests/test_api_key_manager.py` - Comprehensive test suite

## Migration Guide

### From Unencrypted Storage

If you have existing unencrypted API keys:

1. Export existing keys manually
2. Delete old storage
3. Re-add keys using the new secure system
4. Test all connections

### Database Location

- Default location: `~/.audio_chat_qt/api_keys.db`
- Can be customized in APIKeyManager constructor
- Backup this file for key recovery

## Performance Considerations

- Encryption/decryption adds minimal overhead (~1ms per operation)
- Database operations are optimized for frequent access
- Connection tests are performed asynchronously
- History cleanup should be run periodically

## Future Enhancements

- Hardware security module (HSM) support
- Multi-user key management
- Key sharing between team members
- Advanced audit logging
- Integration with external key vaults