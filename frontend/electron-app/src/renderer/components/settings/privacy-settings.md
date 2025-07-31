# Privacy Settings Component

A comprehensive privacy and security settings component for the AI Chat System that provides users with full control over their data privacy, encryption, and retention policies.

## Features

### 🔒 Privacy Controls
- **Local-only Mode**: Ensures all data stays on the local device
- **Message Encryption**: AES-256-GCM encryption for all chat messages
- **Anonymous Mode**: Disables all telemetry and analytics
- **Telemetry Controls**: Fine-grained control over data collection

### 📊 Data Management
- **Data Statistics**: Real-time view of storage usage and message counts
- **Data Export**: Complete backup of all chat data in JSON format
- **Data Clearing**: Secure deletion of all local data
- **Storage Monitoring**: Track encrypted vs unencrypted messages

### ⏰ Data Retention
- **Custom Retention Periods**: Set data retention from 1 day to 1 year
- **Auto-deletion**: Automatic cleanup of old messages
- **Predefined Policies**: Quick-apply retention policies (Minimal, Standard, Extended)
- **Retention Indicators**: Visual feedback on current retention settings

### 🛡️ Security Features
- **Encryption Status Monitoring**: Real-time encryption key information
- **Key Rotation**: Manual and automatic encryption key rotation
- **Migration Tools**: Convert existing unencrypted messages to encrypted format
- **Integrity Verification**: Ensure encryption system health

## Component Structure

```typescript
interface PrivacySettings {
  localOnlyMode: boolean;
  dataRetentionDays: number;
  encryptionEnabled: boolean;
  anonymousMode: boolean;
  telemetryEnabled: boolean;
  crashReportsEnabled: boolean;
  usageAnalyticsEnabled: boolean;
  autoDeleteEnabled: boolean;
  backupEnabled: boolean;
  cloudSyncEnabled: boolean;
}
```

## Usage

```tsx
import { PrivacySettings } from '@/components/settings/privacy-settings';

function SettingsPage() {
  const handleSettingsChange = (settings: PrivacySettings) => {
    console.log('Privacy settings updated:', settings);
  };

  return (
    <PrivacySettings 
      onSettingsChange={handleSettingsChange}
      className="max-w-4xl mx-auto"
    />
  );
}
```

## API Integration

The component integrates with several backend endpoints:

### Settings Management
- `GET /api/settings/privacy` - Load current privacy settings
- `POST /api/settings/privacy` - Save privacy settings

### Data Management
- `GET /api/data/statistics` - Get data usage statistics
- `POST /api/data/clear-all` - Clear all chat data
- `GET /api/data/export` - Export all data

### Encryption Management
- `GET /api/security/encryption/status` - Get encryption status
- `POST /api/security/encryption/rotate-keys` - Rotate encryption keys
- `POST /api/security/encryption/migrate` - Migrate to encryption
- `POST /api/security/encryption/verify` - Verify encryption integrity

## Privacy Indicators

The component provides visual indicators for privacy status:

- **🔒 Encryption**: Shows if messages are encrypted
- **💾 Local-only**: Indicates if data stays local
- **⏰ Retention**: Shows data retention policy
- **👤 Anonymous**: Indicates anonymous mode status

## Security Considerations

1. **Encryption**: All sensitive data is encrypted using AES-256-GCM
2. **Key Management**: Automatic key rotation every 30 days
3. **Local Storage**: Option to keep all data local-only
4. **Data Integrity**: Checksum validation for all encrypted messages
5. **Secure Deletion**: Proper cleanup of sensitive data

## Accessibility

- Full keyboard navigation support
- Screen reader compatible
- High contrast mode support
- RTL (Hebrew) text support
- ARIA labels and descriptions

## Testing

Comprehensive test suite covering:
- Component rendering and interaction
- API integration
- Privacy setting toggles
- Data export/import functionality
- Encryption management
- Error handling

Run tests with:
```bash
npm test privacy-settings.test.tsx
```

## Dependencies

- React 18+
- Lucide React (icons)
- Radix UI components
- Tailwind CSS
- TypeScript

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Lazy loading of encryption status
- Debounced settings updates
- Efficient re-rendering with React.memo
- Minimal bundle size impact

## Localization

Currently supports:
- Hebrew (primary)
- English (fallback)

Text strings are externalized for easy translation to additional languages.