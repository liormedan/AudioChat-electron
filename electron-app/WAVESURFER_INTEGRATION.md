# אינטגרציה עם WaveSurfer.js

## סקירה כללית

האפליקציה משתמשת ב-WaveSurfer.js גרסה 7.10.1 לתצוגה ובקרה של קבצי אודיו. האינטגרציה כוללת קומפוננטות React מתקדמות עם פיצ'רים מלאים לעריכת אודיו.

## קומפוננטות עיקריות

### 1. WaveformPlayer (`waveform-player.tsx`)

הקומפוננטה הראשית לנגינת אודיו עם waveform מתקדם.

#### פיצ'רים:
- **תצוגת Waveform**: גרף אודיו אינטראקטיבי
- **בקרות נגינה**: נגן/השהה, עצור, דילוג קדימה/אחורה
- **בחירת אזורים**: לחיצה על הגרף לבחירת קטעים
- **זום**: הגדלה/הקטנה של הגרף
- **מהירות נגינה**: שליטה במהירות (0.25x - 2x)
- **עוצמת קול**: בקרת ווליום
- **מידע זמן**: תצוגת זמן נוכחי ומשך כולל

#### Props:
```typescript
interface WaveformPlayerProps {
  audioFile: File | null;           // קובץ האודיו
  audioUrl: string | null;          // URL לקובץ
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onRegionSelect?: (start: number, end: number) => void;
  showSpectrogram?: boolean;        // הצגת ספקטרוגרמה
  enableRegions?: boolean;          // אפשר בחירת אזורים
  waveformHeight?: number;          // גובה הגרף
  waveColor?: string;              // צבע הגל
  progressColor?: string;          // צבע ההתקדמות
}
```

### 2. WaveformControls (`waveform-controls.tsx`)

קומפוננטת הגדרות מתקדמות לקסטומיזציה של הwaveform.

#### פיצ'רים:
- **הגדרות תצוגה**: הפעלה/כיבוי של ספקטרוגרמה ואזורים
- **גובה גרף**: שליטה בגובה הwaveform (60-200px)
- **צבעים**: בחירת צבעי גל והתקדמות
- **פריסטים**: צבעים מוכנים מראש

### 3. FileUploader (`file-uploader.tsx`)

קומפוננטה להעלאת קבצי אודיו עם drag & drop.

#### פורמטים נתמכים:
- MP3
- WAV
- FLAC
- AAC
- OGG
- M4A

## שימוש בקומפוננטות

### דוגמה בסיסית:

```tsx
import { WaveformPlayer } from './components/audio/waveform-player';

function AudioPage() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleFileSelect = (file: File) => {
    setAudioFile(file);
    setAudioUrl(URL.createObjectURL(file));
  };

  return (
    <div>
      <WaveformPlayer
        audioFile={audioFile}
        audioUrl={audioUrl}
        onTimeUpdate={(current, duration) => {
          console.log(`${current}s / ${duration}s`);
        }}
        onRegionSelect={(start, end) => {
          console.log(`Selected: ${start}s - ${end}s`);
        }}
        enableRegions={true}
        waveformHeight={100}
      />
    </div>
  );
}
```

### דוגמה מתקדמת עם הגדרות:

```tsx
import { WaveformPlayer } from './components/audio/waveform-player';
import { WaveformControls } from './components/audio/waveform-controls';

function AdvancedAudioPage() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [showSpectrogram, setShowSpectrogram] = useState(false);
  const [enableRegions, setEnableRegions] = useState(true);
  const [waveformHeight, setWaveformHeight] = useState(80);
  const [waveColor, setWaveColor] = useState('#6b7280');
  const [progressColor, setProgressColor] = useState('#3b82f6');

  return (
    <div>
      <WaveformPlayer
        audioFile={audioFile}
        audioUrl={audioUrl}
        showSpectrogram={showSpectrogram}
        enableRegions={enableRegions}
        waveformHeight={waveformHeight}
        waveColor={waveColor}
        progressColor={progressColor}
        onRegionSelect={(start, end) => {
          // Handle region selection
          console.log('Region selected:', start, end);
        }}
      />
      
      <WaveformControls
        showSpectrogram={showSpectrogram}
        onSpectrogramToggle={setShowSpectrogram}
        enableRegions={enableRegions}
        onRegionsToggle={setEnableRegions}
        waveformHeight={waveformHeight}
        onHeightChange={setWaveformHeight}
        waveColor={waveColor}
        onWaveColorChange={setWaveColor}
        progressColor={progressColor}
        onProgressColorChange={setProgressColor}
      />
    </div>
  );
}
```

## API Events

### WaveSurfer Events שמטופלים:

- `ready`: כאשר הקובץ נטען ומוכן לנגינה
- `play`: כאשר הנגינה מתחילה
- `pause`: כאשר הנגינה מושהית
- `finish`: כאשר הנגינה מסתיימת
- `audioprocess`: עדכון זמן במהלך נגינה
- `click`: לחיצה על הwaveform לבחירת אזור

### Custom Events:

- `onTimeUpdate(currentTime, duration)`: עדכון זמן
- `onPlayStateChange(isPlaying)`: שינוי מצב נגינה
- `onRegionSelect(start, end)`: בחירת אזור

## התקנה ותלויות

### תלויות נדרשות:

```json
{
  "dependencies": {
    "wavesurfer.js": "^7.10.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

### התקנה:

```bash
npm install wavesurfer.js@latest
```

## בדיקה ופיתוח

### קובץ בדיקה:
- `test-waveform.html` - דף HTML פשוט לבדיקת האינטגרציה

### הרצת בדיקות:
```bash
# Build the project
npm run build:renderer

# Type checking
npm run type-check

# Start development server
npm run dev
```

## פיצ'רים מתקדמים

### 1. בחירת אזורים (Regions)
- לחיצה על הwaveform יוצרת אזור של 5 שניות
- ניתן לנגן רק את האזור הנבחר
- מידע על האזור מוצג למשתמש

### 2. זום ונווטציה
- זום של 1x עד 10x
- דילוג של 10 שניות קדימה/אחורה
- ניווט עם לחיצה על הwaveform

### 3. בקרות אודיו
- עוצמת קול: 0-100%
- מהירות נגינה: 0.25x-2x
- עצירה ואיפוס למיקום ההתחלה

### 4. עיצוב מותאם אישית
- צבעי waveform ניתנים לשינוי
- גובה הגרף ניתן להתאמה
- פריסטים של צבעים

## אינטגרציה עם Chat AI

הקומפוננטות משולבות עם מערכת הצ'אט לעריכת אודיו:

```tsx
onRegionSelect={(start, end) => {
  const regionMessage: ChatMessage = {
    id: Date.now().toString(),
    type: 'assistant',
    content: `אזור נבחר: ${Math.round(start)}s - ${Math.round(end)}s. 
             אתה יכול לתת פקודות כמו "חתוך את האזור הזה" או "הוסף אפקטים לבחירה".`,
    timestamp: new Date()
  };
  setChatMessages(prev => [...prev, regionMessage]);
}}
```

## בעיות נפוצות ופתרונות

### 1. קובץ לא נטען
- ודא שהקובץ בפורמט נתמך
- בדוק שה-URL תקין
- ודא שיש הרשאות לקריאת הקובץ

### 2. Waveform לא מוצג
- בדוק שהקונטיינר קיים ב-DOM
- ודא שה-height מוגדר נכון
- בדוק שאין שגיאות JavaScript

### 3. בעיות ביצועים
- השתמש ב-normalize: true לקבצים גדולים
- הגבל את גובה הwaveform
- השתמש בזום נמוך לקבצים ארוכים

## תוכניות עתידיות

- [ ] תמיכה בפלאגינים נוספים (Regions, Spectrogram)
- [ ] שמירת הגדרות משתמש
- [ ] ייצוא אזורים נבחרים
- [ ] תמיכה במספר קבצים בו-זמנית
- [ ] אפקטים חזותיים נוספים