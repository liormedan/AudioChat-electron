import React, { useState, useEffect, useCallback } from 'react';
import {
  Shield,
  Eye,
  EyeOff,
  Trash2,
  Download,
  Lock,
  Unlock,
  Server,
  HardDrive,
  Clock,
  AlertTriangle,
  CheckCircle,
  Database,
  BarChart3,
  RefreshCw,
  Info,
  Wifi,
  WifiOff,
  RotateCcw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert';

// Privacy settings interfaces
export interface PrivacySettings {
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

export interface DataRetentionPolicy {
  id: string;
  name: string;
  description: string;
  retentionDays: number;
  dataTypes: string[];
  autoDelete: boolean;
  enabled: boolean;
}

export interface PrivacyIndicator {
  type: 'encryption' | 'local-only' | 'retention' | 'anonymous';
  status: 'active' | 'inactive' | 'warning';
  message: string;
  details?: string;
}

interface PrivacySettingsProps {
  className?: string;
  onSettingsChange?: (settings: PrivacySettings) => void;
}

// Default privacy settings
const DEFAULT_PRIVACY_SETTINGS: PrivacySettings = {
  localOnlyMode: false,
  dataRetentionDays: 90,
  encryptionEnabled: true,
  anonymousMode: false,
  telemetryEnabled: true,
  crashReportsEnabled: true,
  usageAnalyticsEnabled: false,
  autoDeleteEnabled: false,
  backupEnabled: true,
  cloudSyncEnabled: false
};

// Built-in retention policies
const RETENTION_POLICIES: DataRetentionPolicy[] = [
  {
    id: 'minimal',
    name: 'מינימלי',
    description: 'שמירת נתונים למינימום הנדרש',
    retentionDays: 7,
    dataTypes: ['messages', 'sessions'],
    autoDelete: true,
    enabled: false
  },
  {
    id: 'standard',
    name: 'סטנדרטי',
    description: 'שמירת נתונים לתקופה סבירה',
    retentionDays: 90,
    dataTypes: ['messages', 'sessions', 'settings'],
    autoDelete: true,
    enabled: true
  },
  {
    id: 'extended',
    name: 'מורחב',
    description: 'שמירת נתונים לתקופה ארוכה',
    retentionDays: 365,
    dataTypes: ['messages', 'sessions', 'settings', 'analytics'],
    autoDelete: false,
    enabled: false
  }
];

export const PrivacySettings: React.FC<PrivacySettingsProps> = ({
  className = '',
  onSettingsChange
}) => {
  // State management
  const [settings, setSettings] = useState<PrivacySettings>(DEFAULT_PRIVACY_SETTINGS);
  const [retentionPolicies, setRetentionPolicies] = useState<DataRetentionPolicy[]>(RETENTION_POLICIES);
  const [privacyIndicators, setPrivacyIndicators] = useState<PrivacyIndicator[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showClearDataDialog, setShowClearDataDialog] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [dataStats, setDataStats] = useState({
    totalMessages: 0,
    totalSessions: 0,
    storageUsed: 0,
    oldestData: '',
    encryptedMessages: 0
  });
  const [encryptionStatus, setEncryptionStatus] = useState<any>(null);
  const [isEncrypting, setIsEncrypting] = useState(false);
  const [showMigrateDialog, setShowMigrateDialog] = useState(false);

  // Load settings on mount
  useEffect(() => {
    loadPrivacySettings();
    loadDataStatistics();
    loadEncryptionStatus();
    updatePrivacyIndicators();
  }, []);

  // Update indicators when settings change
  useEffect(() => {
    updatePrivacyIndicators();
    onSettingsChange?.(settings);
  }, [settings, onSettingsChange]);

  const loadPrivacySettings = useCallback(async () => {
    try {
      const response = await fetch('/api/settings/privacy');
      if (response.ok) {
        const data = await response.json();
        setSettings({ ...DEFAULT_PRIVACY_SETTINGS, ...data });
      }
    } catch (error) {
      console.error('Error loading privacy settings:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const savePrivacySettings = useCallback(async (newSettings: PrivacySettings) => {
    try {
      const response = await fetch('/api/settings/privacy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      });
      
      if (response.ok) {
        setSettings(newSettings);
      }
    } catch (error) {
      console.error('Error saving privacy settings:', error);
    }
  }, []);

  const loadDataStatistics = useCallback(async () => {
    try {
      const response = await fetch('/api/data/statistics');
      if (response.ok) {
        const stats = await response.json();
        setDataStats(stats);
      }
    } catch (error) {
      console.error('Error loading data statistics:', error);
    }
  }, []);

  const loadEncryptionStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/security/encryption/status');
      if (response.ok) {
        const status = await response.json();
        setEncryptionStatus(status);
      }
    } catch (error) {
      console.error('Error loading encryption status:', error);
    }
  }, []);

  const updatePrivacyIndicators = useCallback(() => {
    const indicators: PrivacyIndicator[] = [];

    // Encryption indicator
    indicators.push({
      type: 'encryption',
      status: settings.encryptionEnabled ? 'active' : 'warning',
      message: settings.encryptionEnabled ? 'הצפנה פעילה' : 'הצפנה לא פעילה',
      details: settings.encryptionEnabled ? 
        'כל ההודעות מוצפנות במסד הנתונים' : 
        'הודעות נשמרות ללא הצפנה'
    });

    // Local-only mode indicator
    indicators.push({
      type: 'local-only',
      status: settings.localOnlyMode ? 'active' : 'inactive',
      message: settings.localOnlyMode ? 'מצב מקומי בלבד' : 'מצב רגיל',
      details: settings.localOnlyMode ? 
        'כל הנתונים נשמרים מקומית בלבד' : 
        'נתונים עשויים להישלח לשרתים חיצוניים'
    });

    // Data retention indicator
    indicators.push({
      type: 'retention',
      status: settings.autoDeleteEnabled ? 'active' : 'inactive',
      message: `שמירת נתונים: ${settings.dataRetentionDays} ימים`,
      details: settings.autoDeleteEnabled ? 
        'נתונים ישנים נמחקים אוטומטית' : 
        'נתונים נשמרים ללא הגבלת זמן'
    });

    // Anonymous mode indicator
    indicators.push({
      type: 'anonymous',
      status: settings.anonymousMode ? 'active' : 'inactive',
      message: settings.anonymousMode ? 'מצב אנונימי' : 'מצב רגיל',
      details: settings.anonymousMode ? 
        'לא נאספים נתוני זיהוי אישיים' : 
        'נתוני שימוש עשויים להיאסף'
    });

    setPrivacyIndicators(indicators);
  }, [settings]);

  const handleSettingChange = useCallback((key: keyof PrivacySettings, value: any) => {
    const newSettings = { ...settings, [key]: value };
    savePrivacySettings(newSettings);
  }, [settings, savePrivacySettings]);

  const clearAllData = useCallback(async () => {
    try {
      const response = await fetch('/api/data/clear-all', {
        method: 'POST'
      });
      
      if (response.ok) {
        await loadDataStatistics();
        setShowClearDataDialog(false);
      }
    } catch (error) {
      console.error('Error clearing data:', error);
    }
  }, [loadDataStatistics]);

  const exportData = useCallback(async () => {
    try {
      const response = await fetch('/api/data/export');
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-data-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        setShowExportDialog(false);
      }
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  }, []);

  const applyRetentionPolicy = useCallback(async (policyId: string) => {
    const policy = retentionPolicies.find(p => p.id === policyId);
    if (!policy) return;

    const newSettings = {
      ...settings,
      dataRetentionDays: policy.retentionDays,
      autoDeleteEnabled: policy.autoDelete
    };

    await savePrivacySettings(newSettings);

    // Update policy states
    setRetentionPolicies(prev => prev.map(p => ({
      ...p,
      enabled: p.id === policyId
    })));
  }, [settings, retentionPolicies, savePrivacySettings]);

  const migrateToEncryption = useCallback(async () => {
    try {
      setIsEncrypting(true);
      const response = await fetch('/api/security/encryption/migrate', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Migration completed:', result);
        await loadEncryptionStatus();
        await loadDataStatistics();
        setShowMigrateDialog(false);
      }
    } catch (error) {
      console.error('Error migrating to encryption:', error);
    } finally {
      setIsEncrypting(false);
    }
  }, [loadEncryptionStatus, loadDataStatistics]);

  const rotateEncryptionKeys = useCallback(async () => {
    try {
      const response = await fetch('/api/security/encryption/rotate-keys', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Key rotation completed:', result);
        await loadEncryptionStatus();
      }
    } catch (error) {
      console.error('Error rotating keys:', error);
    }
  }, [loadEncryptionStatus]);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getIndicatorIcon = (indicator: PrivacyIndicator) => {
    switch (indicator.type) {
      case 'encryption':
        return indicator.status === 'active' ? 
          <Lock className="h-4 w-4 text-green-500" /> : 
          <Unlock className="h-4 w-4 text-red-500" />;
      case 'local-only':
        return indicator.status === 'active' ? 
          <HardDrive className="h-4 w-4 text-blue-500" /> : 
          <Server className="h-4 w-4 text-gray-500" />;
      case 'retention':
        return <Clock className="h-4 w-4 text-purple-500" />;
      case 'anonymous':
        return indicator.status === 'active' ? 
          <EyeOff className="h-4 w-4 text-orange-500" /> : 
          <Eye className="h-4 w-4 text-gray-500" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="h-6 w-6 animate-spin" />
        <span className="ml-2">טוען הגדרות פרטיות...</span>
      </div>
    );
  }

  return (
    <div className={`privacy-settings ${className}`}>
      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">
            <Shield className="h-4 w-4 mr-2" />
            כללי
          </TabsTrigger>
          <TabsTrigger value="data">
            <Database className="h-4 w-4 mr-2" />
            נתונים
          </TabsTrigger>
          <TabsTrigger value="retention">
            <Clock className="h-4 w-4 mr-2" />
            שמירה
          </TabsTrigger>
          <TabsTrigger value="indicators">
            <BarChart3 className="h-4 w-4 mr-2" />
            סטטוס
          </TabsTrigger>
        </TabsList>

        {/* General Privacy Settings */}
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                הגדרות פרטיות כלליות
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Local-only mode */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">מצב מקומי בלבד</Label>
                  <p className="text-sm text-muted-foreground">
                    כל הנתונים נשמרים מקומית, ללא שליחה לשרתים חיצוניים
                  </p>
                </div>
                <Switch
                  checked={settings.localOnlyMode}
                  onCheckedChange={(checked) => handleSettingChange('localOnlyMode', checked)}
                />
              </div>

              {/* Encryption */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">הצפנת הודעות</Label>
                  <p className="text-sm text-muted-foreground">
                    הצפנה של כל ההודעות במסד הנתונים המקומי
                  </p>
                </div>
                <Switch
                  checked={settings.encryptionEnabled}
                  onCheckedChange={(checked) => handleSettingChange('encryptionEnabled', checked)}
                />
              </div>

              {/* Anonymous mode */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">מצב אנונימי</Label>
                  <p className="text-sm text-muted-foreground">
                    אי איסוף נתוני זיהוי אישיים או מידע על השימוש
                  </p>
                </div>
                <Switch
                  checked={settings.anonymousMode}
                  onCheckedChange={(checked) => handleSettingChange('anonymousMode', checked)}
                />
              </div>

              {/* Telemetry */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">טלמטריה</Label>
                  <p className="text-sm text-muted-foreground">
                    שליחת נתוני שימוש אנונימיים לשיפור המוצר
                  </p>
                </div>
                <Switch
                  checked={settings.telemetryEnabled}
                  onCheckedChange={(checked) => handleSettingChange('telemetryEnabled', checked)}
                  disabled={settings.anonymousMode}
                />
              </div>

              {/* Crash reports */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">דוחות קריסות</Label>
                  <p className="text-sm text-muted-foreground">
                    שליחת דוחות קריסות אוטומטית לתיקון באגים
                  </p>
                </div>
                <Switch
                  checked={settings.crashReportsEnabled}
                  onCheckedChange={(checked) => handleSettingChange('crashReportsEnabled', checked)}
                  disabled={settings.anonymousMode}
                />
              </div>

              {/* Usage analytics */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">ניתוח שימוש</Label>
                  <p className="text-sm text-muted-foreground">
                    איסוף נתונים מפורטים על דפוסי השימוש
                  </p>
                </div>
                <Switch
                  checked={settings.usageAnalyticsEnabled}
                  onCheckedChange={(checked) => handleSettingChange('usageAnalyticsEnabled', checked)}
                  disabled={settings.anonymousMode}
                />
              </div>
            </CardContent>
          </Card>

          {/* Encryption Management Card */}
          {encryptionStatus && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5" />
                  ניהול הצפנה
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Encryption Status */}
                <div className="bg-muted/50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">סטטוס הצפנה</span>
                    <Badge variant={encryptionStatus.encryption_enabled ? 'default' : 'destructive'}>
                      {encryptionStatus.encryption_enabled ? 'פעיל' : 'לא פעיל'}
                    </Badge>
                  </div>
                  
                  {encryptionStatus.current_key && (
                    <div className="text-sm text-muted-foreground space-y-1">
                      <div>מפתח נוכחי: {encryptionStatus.current_key.key_id}</div>
                      <div>אלגוריתם: {encryptionStatus.current_key.algorithm}</div>
                      <div>ימים עד תפוגה: {encryptionStatus.current_key.days_until_expiry}</div>
                    </div>
                  )}
                </div>

                {/* Encryption Actions */}
                <div className="flex flex-col gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowMigrateDialog(true)}
                    disabled={isEncrypting}
                    className="justify-start"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    העבר הודעות קיימות להצפנה
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={rotateEncryptionKeys}
                    className="justify-start"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    רוטציה של מפתחות הצפנה
                  </Button>
                </div>

                {/* Local-only mode warning */}
                {settings.localOnlyMode && (
                  <Alert>
                    <HardDrive className="h-4 w-4" />
                    <AlertTitle>מצב מקומי בלבד פעיל</AlertTitle>
                    <AlertDescription>
                      כל הנתונים נשמרים מקומית בלבד. לא יישלחו נתונים לשרתים חיצוניים.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Data Management */}
        <TabsContent value="data" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  סטטיסטיקות נתונים
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {dataStats.totalMessages.toLocaleString('he-IL')}
                    </div>
                    <div className="text-sm text-muted-foreground">הודעות</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {dataStats.totalSessions.toLocaleString('he-IL')}
                    </div>
                    <div className="text-sm text-muted-foreground">שיחות</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {formatBytes(dataStats.storageUsed)}
                    </div>
                    <div className="text-sm text-muted-foreground">נפח</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {dataStats.encryptedMessages.toLocaleString('he-IL')}
                    </div>
                    <div className="text-sm text-muted-foreground">מוצפנות</div>
                  </div>
                </div>

                {dataStats.oldestData && (
                  <div className="text-center pt-2 border-t">
                    <div className="text-sm text-muted-foreground">
                      נתונים ישנים ביותר: {new Date(dataStats.oldestData).toLocaleDateString('he-IL')}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>פעולות נתונים</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => setShowExportDialog(true)}
                >
                  <Download className="h-4 w-4 mr-2" />
                  ייצא את כל הנתונים
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => loadDataStatistics()}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  רענן סטטיסטיקות
                </Button>

                <Button
                  variant="destructive"
                  className="w-full justify-start"
                  onClick={() => setShowClearDataDialog(true)}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  מחק את כל הנתונים
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Data Retention */}
        <TabsContent value="retention" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                מדיניות שמירת נתונים
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Custom retention period */}
              <div className="space-y-3">
                <Label className="text-base font-medium">
                  תקופת שמירה מותאמת: {settings.dataRetentionDays} ימים
                </Label>
                <Slider
                  value={[settings.dataRetentionDays]}
                  onValueChange={([value]) => handleSettingChange('dataRetentionDays', value)}
                  min={1}
                  max={365}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>יום אחד</span>
                  <span>שנה</span>
                </div>
              </div>

              {/* Auto-delete toggle */}
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label className="text-base font-medium">מחיקה אוטומטית</Label>
                  <p className="text-sm text-muted-foreground">
                    מחיקה אוטומטית של נתונים ישנים מהתקופה שנקבעה
                  </p>
                </div>
                <Switch
                  checked={settings.autoDeleteEnabled}
                  onCheckedChange={(checked) => handleSettingChange('autoDeleteEnabled', checked)}
                />
              </div>

              {/* Predefined policies */}
              <div className="space-y-3">
                <Label className="text-base font-medium">מדיניות מוגדרות מראש</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {retentionPolicies.map((policy) => (
                    <Card
                      key={policy.id}
                      className={`cursor-pointer transition-colors ${
                        policy.enabled ? 'ring-2 ring-primary' : 'hover:bg-accent/50'
                      }`}
                      onClick={() => applyRetentionPolicy(policy.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{policy.name}</h4>
                          {policy.enabled && (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {policy.description}
                        </p>
                        <div className="text-xs text-muted-foreground">
                          {policy.retentionDays} ימים • {policy.dataTypes.length} סוגי נתונים
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Indicators */}
        <TabsContent value="indicators" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                אינדיקטורי פרטיות
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {privacyIndicators.map((indicator, index) => (
                  <Card key={index} className="p-4">
                    <div className="flex items-start gap-3">
                      {getIndicatorIcon(indicator)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{indicator.message}</span>
                          <Badge
                            variant={
                              indicator.status === 'active' ? 'default' :
                              indicator.status === 'warning' ? 'destructive' : 'secondary'
                            }
                            className="text-xs"
                          >
                            {indicator.status === 'active' ? 'פעיל' :
                             indicator.status === 'warning' ? 'אזהרה' : 'לא פעיל'}
                          </Badge>
                        </div>
                        {indicator.details && (
                          <p className="text-sm text-muted-foreground">
                            {indicator.details}
                          </p>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Clear Data Dialog */}
      <Dialog open={showClearDataDialog} onOpenChange={setShowClearDataDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              מחיקת כל הנתונים
            </DialogTitle>
            <DialogDescription>
              פעולה זו תמחק את כל הנתונים המקומיים כולל הודעות, שיחות והגדרות.
              פעולה זו אינה ניתנת לביטול.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">
                נתונים שיימחקו:
              </p>
              <ul className="text-sm text-red-700 dark:text-red-300 mt-2 space-y-1">
                <li>• {dataStats.totalMessages.toLocaleString('he-IL')} הודעות</li>
                <li>• {dataStats.totalSessions.toLocaleString('he-IL')} שיחות</li>
                <li>• הגדרות אישיות</li>
                <li>• היסטוריית שימוש</li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowClearDataDialog(false)}>
              ביטול
            </Button>
            <Button variant="destructive" onClick={clearAllData}>
              מחק הכל
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Export Data Dialog */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              ייצוא נתונים
            </DialogTitle>
            <DialogDescription>
              ייצוא כל הנתונים המקומיים לקובץ JSON לגיבוי או העברה.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                הקובץ יכלול:
              </p>
              <ul className="text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1">
                <li>• כל ההודעות והשיחות</li>
                <li>• הגדרות אישיות</li>
                <li>• מטאדטה של sessions</li>
                <li>• נתונים מוצפנים (אם הופעלה הצפנה)</li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExportDialog(false)}>
              ביטול
            </Button>
            <Button onClick={exportData}>
              ייצא נתונים
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Migrate to Encryption Dialog */}
      <Dialog open={showMigrateDialog} onOpenChange={setShowMigrateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5" />
              העברה להצפנה
            </DialogTitle>
            <DialogDescription>
              פעולה זו תעביר את כל ההודעות הקיימות להצפנה. 
              זה עשוי לקחת זמן בהתאם לכמות הנתונים.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                מה יקרה:
              </p>
              <ul className="text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1">
                <li>• כל ההודעות הקיימות יוצפנו</li>
                <li>• הודעות שכבר מוצפנות יושארו כפי שהן</li>
                <li>• התהליך בטוח ולא ימחק נתונים</li>
                <li>• ניתן לבטל בכל שלב</li>
              </ul>
            </div>
            
            {isEncrypting && (
              <div className="mt-4 flex items-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span className="text-sm">מעביר הודעות להצפנה...</span>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowMigrateDialog(false)}
              disabled={isEncrypting}
            >
              ביטול
            </Button>
            <Button 
              onClick={migrateToEncryption}
              disabled={isEncrypting}
            >
              {isEncrypting ? 'מעביר...' : 'התחל העברה'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};