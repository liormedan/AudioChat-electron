import React, { useState, useEffect } from 'react';
import { PrivacySettings, PrivacySettings as PrivacySettingsType } from './privacy-settings';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

/**
 * Integration example showing how to use the PrivacySettings component
 * in a larger settings page or application context.
 */

interface PrivacyStatus {
  level: 'high' | 'medium' | 'low';
  message: string;
  recommendations: string[];
}

export const PrivacySettingsIntegrationExample: React.FC = () => {
  const [currentSettings, setCurrentSettings] = useState<PrivacySettingsType | null>(null);
  const [privacyStatus, setPrivacyStatus] = useState<PrivacyStatus | null>(null);
  const [showRecommendations, setShowRecommendations] = useState(false);

  // Calculate privacy status based on current settings
  useEffect(() => {
    if (!currentSettings) return;

    const status = calculatePrivacyStatus(currentSettings);
    setPrivacyStatus(status);
    
    // Show recommendations if privacy level is not high
    setShowRecommendations(status.level !== 'high');
  }, [currentSettings]);

  const calculatePrivacyStatus = (settings: PrivacySettingsType): PrivacyStatus => {
    let score = 0;
    const recommendations: string[] = [];

    // Check encryption
    if (settings.encryptionEnabled) {
      score += 30;
    } else {
      recommendations.push('הפעל הצפנת הודעות לאבטחה מקסימלית');
    }

    // Check local-only mode
    if (settings.localOnlyMode) {
      score += 25;
    } else {
      recommendations.push('הפעל מצב מקומי בלבד למניעת שליחת נתונים לשרתים חיצוניים');
    }

    // Check anonymous mode
    if (settings.anonymousMode) {
      score += 20;
    } else {
      recommendations.push('שקול הפעלת מצב אנונימי למניעת איסוף נתוני שימוש');
    }

    // Check auto-delete
    if (settings.autoDeleteEnabled) {
      score += 15;
    } else {
      recommendations.push('הפעל מחיקה אוטומטית לניהול טוב יותר של נתונים ישנים');
    }

    // Check telemetry
    if (!settings.telemetryEnabled && !settings.usageAnalyticsEnabled) {
      score += 10;
    } else {
      recommendations.push('כבה טלמטריה וניתוח שימוש לפרטיות מקסימלית');
    }

    // Determine level and message
    if (score >= 80) {
      return {
        level: 'high',
        message: 'רמת הפרטיות שלך גבוהה מאוד',
        recommendations: []
      };
    } else if (score >= 50) {
      return {
        level: 'medium',
        message: 'רמת הפרטיות שלך בינונית',
        recommendations
      };
    } else {
      return {
        level: 'low',
        message: 'רמת הפרטיות שלך נמוכה',
        recommendations
      };
    }
  };

  const getStatusColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (level: string) => {
    switch (level) {
      case 'high': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'medium': return <Shield className="h-5 w-5 text-yellow-500" />;
      case 'low': return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default: return <Shield className="h-5 w-5 text-gray-500" />;
    }
  };

  const handleSettingsChange = (settings: PrivacySettingsType) => {
    setCurrentSettings(settings);
    
    // Here you could also:
    // 1. Save to global state management (Redux, Zustand, etc.)
    // 2. Trigger other privacy-related updates in the app
    // 3. Show notifications about privacy changes
    // 4. Update other components that depend on privacy settings
    
    console.log('Privacy settings updated:', settings);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Privacy Status Overview */}
      {privacyStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(privacyStatus.level)}
              סקירת פרטיות
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <span className={`text-lg font-medium ${getStatusColor(privacyStatus.level)}`}>
                {privacyStatus.message}
              </span>
              <Badge 
                variant={privacyStatus.level === 'high' ? 'default' : 
                        privacyStatus.level === 'medium' ? 'secondary' : 'destructive'}
              >
                {privacyStatus.level === 'high' ? 'מעולה' :
                 privacyStatus.level === 'medium' ? 'בינוני' : 'דורש שיפור'}
              </Badge>
            </div>

            {/* Recommendations */}
            {showRecommendations && privacyStatus.recommendations.length > 0 && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <div className="space-y-2">
                    <p className="font-medium">המלצות לשיפור הפרטיות:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {privacyStatus.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm">{rec}</li>
                      ))}
                    </ul>
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Current Settings Summary */}
      {currentSettings && (
        <Card>
          <CardHeader>
            <CardTitle>הגדרות נוכחות</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-sm text-muted-foreground">הצפנה</div>
                <Badge variant={currentSettings.encryptionEnabled ? 'default' : 'destructive'}>
                  {currentSettings.encryptionEnabled ? 'פעיל' : 'כבוי'}
                </Badge>
              </div>
              <div className="text-center">
                <div className="text-sm text-muted-foreground">מקומי בלבד</div>
                <Badge variant={currentSettings.localOnlyMode ? 'default' : 'secondary'}>
                  {currentSettings.localOnlyMode ? 'פעיל' : 'כבוי'}
                </Badge>
              </div>
              <div className="text-center">
                <div className="text-sm text-muted-foreground">מצב אנונימי</div>
                <Badge variant={currentSettings.anonymousMode ? 'default' : 'secondary'}>
                  {currentSettings.anonymousMode ? 'פעיל' : 'כבוי'}
                </Badge>
              </div>
              <div className="text-center">
                <div className="text-sm text-muted-foreground">שמירת נתונים</div>
                <Badge variant="outline">
                  {currentSettings.dataRetentionDays} ימים
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Privacy Settings Component */}
      <PrivacySettings 
        onSettingsChange={handleSettingsChange}
        className="w-full"
      />

      {/* Integration Notes */}
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-sm">הערות אינטגרציה</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <p>
            דוגמה זו מדגימה כיצד לשלב את רכיב הגדרות הפרטיות עם:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>מעקב אחר שינויים בהגדרות</li>
            <li>חישוב רמת פרטיות</li>
            <li>הצגת המלצות לשיפור</li>
            <li>סקירה כללית של הגדרות נוכחות</li>
            <li>אינטגרציה עם מערכות ניהול מצב גלובליות</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

// Example of how to use in a larger application context
export const AppWithPrivacySettings: React.FC = () => {
  const [isPrivacySettingsOpen, setIsPrivacySettingsOpen] = useState(false);
  const [globalPrivacySettings, setGlobalPrivacySettings] = useState<PrivacySettingsType | null>(null);

  // This could be integrated with your app's routing system
  const openPrivacySettings = () => {
    setIsPrivacySettingsOpen(true);
  };

  // This could be integrated with your global state management
  const handleGlobalPrivacyChange = (settings: PrivacySettingsType) => {
    setGlobalPrivacySettings(settings);
    
    // Apply privacy settings globally
    if (settings.localOnlyMode) {
      // Disable all external API calls
      console.log('Local-only mode enabled - disabling external APIs');
    }
    
    if (settings.anonymousMode) {
      // Disable all analytics and telemetry
      console.log('Anonymous mode enabled - disabling analytics');
    }
    
    // Update other parts of the application based on privacy settings
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Your app header/navigation */}
      <header className="border-b p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">AI Chat System</h1>
          <button 
            onClick={openPrivacySettings}
            className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent"
          >
            <Shield className="h-4 w-4" />
            הגדרות פרטיות
          </button>
        </div>
      </header>

      {/* Main app content */}
      <main className="p-4">
        {isPrivacySettingsOpen ? (
          <PrivacySettingsIntegrationExample />
        ) : (
          <div className="text-center py-12">
            <p>תוכן האפליקציה הראשי</p>
            <p className="text-sm text-muted-foreground mt-2">
              לחץ על "הגדרות פרטיות" כדי לראות את הרכיב
            </p>
          </div>
        )}
      </main>

      {/* Privacy status indicator (could be a floating widget) */}
      {globalPrivacySettings && (
        <div className="fixed bottom-4 right-4 bg-background border rounded-lg p-3 shadow-lg">
          <div className="flex items-center gap-2 text-sm">
            <Shield className="h-4 w-4" />
            <span>
              פרטיות: {globalPrivacySettings.encryptionEnabled && globalPrivacySettings.localOnlyMode ? 
                'גבוהה' : 'בינונית'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PrivacySettingsIntegrationExample;