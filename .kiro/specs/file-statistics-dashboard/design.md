# Design Document

## Overview

The File Statistics Dashboard is a comprehensive analytics page that provides users with insights into their uploaded audio files. The feature integrates seamlessly with the existing PyQt6-based application architecture, utilizing the current sidebar navigation system and Material Design theme. The dashboard displays key metrics, visual charts, and detailed file information in an organized, user-friendly interface.

## Architecture

### Component Structure

The File Statistics Dashboard follows the existing application architecture pattern:

```
src/ui/pages/file_stats_page.py (existing)
├── FileStatsPage (QWidget)
    ├── Summary Statistics Section
    ├── Visual Charts Section  
    ├── Recent Files Table Section
    └── Data Management Layer
```

### Integration Points

1. **Sidebar Navigation**: Already integrated via `sidebar.py` with the "📊 File Stats" button
2. **Main Window**: Already registered in `main_window.py` using QStackedWidget
3. **Database Layer**: Will connect to existing database management system
4. **Theme Integration**: Uses qt-material dark theme styling

## Components and Interfaces

### 1. FileStatsPage (Main Component)

**Purpose**: Main container widget that orchestrates all statistics display components

**Key Methods**:
- `__init__()`: Initialize layout and create all sub-components
- `refresh_data()`: Update all statistics with current data
- `_add_stat_box()`: Create summary statistic boxes
- `_create_pie_chart()`: Generate file format distribution chart
- `_create_bar_chart()`: Generate upload timeline chart
- `_create_recent_files_table()`: Create recent files table

### 2. Summary Statistics Section

**Components**:
- Total Files Count Box
- Total Duration Box  
- File Formats Box
- Last Upload Date Box

**Layout**: Horizontal layout with 4 equal-width statistic boxes

**Styling**: Material Design cards with icons, titles, and prominent values

### 3. Visual Charts Section

**Components**:
- **Pie Chart**: File format distribution (MP3, WAV, FLAC, etc.)
- **Bar Chart**: Upload activity over time (daily/weekly view)

**Implementation Approach**:
- Phase 1: Simple text-based placeholders (current implementation)
- Phase 2: Integration with matplotlib or PyQt6 charts
- Phase 3: Interactive charts with hover effects

**Layout**: Horizontal layout with two equal-width chart containers

### 4. Recent Files Table

**Purpose**: Display detailed information about recently uploaded files

**Columns**:
- Filename
- Format
- File Size
- Duration
- Upload Date

**Features**:
- Sortable columns
- Fixed column widths for optimal display
- Scrollable for large datasets

### 5. Data Management Interface

**FileStatsDataManager** (to be implemented):

```python
class FileStatsDataManager:
    def get_total_files_count() -> int
    def get_total_duration() -> str
    def get_format_distribution() -> Dict[str, int]
    def get_last_upload_date() -> str
    def get_recent_files(limit: int = 10) -> List[FileInfo]
    def get_upload_timeline(days: int = 7) -> Dict[str, int]
```

## Data Models

### FileInfo Model

```python
@dataclass
class FileInfo:
    filename: str
    format: str
    size_bytes: int
    duration_seconds: int
    upload_date: datetime
    file_path: str
    
    @property
    def size_formatted(self) -> str:
        """Return human-readable file size"""
        
    @property
    def duration_formatted(self) -> str:
        """Return formatted duration (HH:MM:SS)"""
```

### StatsSummary Model

```python
@dataclass
class StatsSummary:
    total_files: int
    total_duration_seconds: int
    format_distribution: Dict[str, int]
    last_upload: datetime
    
    @property
    def total_duration_formatted(self) -> str:
        """Return formatted total duration"""
```

## Error Handling

### Error Scenarios

1. **Database Connection Failure**
   - Display "Unable to load statistics" message
   - Provide retry button
   - Log error details

2. **No Files Available**
   - Show empty state with helpful message
   - Display "Upload your first file" call-to-action
   - Hide charts and show placeholder content

3. **Chart Rendering Failure**
   - Fall back to text-based summaries
   - Log rendering errors
   - Maintain page functionality

### Error Display Strategy

- Use consistent error styling with Material Design
- Provide actionable error messages
- Maintain page layout integrity during errors
- Implement graceful degradation

## Testing Strategy

### Unit Tests

1. **FileStatsPage Component Tests**
   - Layout initialization
   - Data binding and display
   - Error state handling
   - Refresh functionality

2. **Data Manager Tests**
   - Database query accuracy
   - Data formatting correctness
   - Error handling scenarios
   - Performance with large datasets

3. **Model Tests**
   - Data validation
   - Property calculations
   - Edge cases (zero duration, large files)

### Integration Tests

1. **Navigation Integration**
   - Sidebar button activation
   - Page switching functionality
   - State persistence

2. **Database Integration**
   - Real data loading
   - Performance with actual file counts
   - Data consistency

3. **Theme Integration**
   - Styling consistency
   - Dark/light theme compatibility
   - Responsive layout behavior

### Manual Testing Scenarios

1. **User Workflow Testing**
   - Navigate to File Stats page
   - Verify all statistics display correctly
   - Test with various file counts (0, 1, many)
   - Verify real-time updates after file operations

2. **Visual Testing**
   - Chart readability and accuracy
   - Table sorting and scrolling
   - Responsive behavior on different window sizes
   - Color scheme consistency

## Implementation Phases

### Phase 1: Enhanced Static Implementation (Current)
- Improve existing placeholder implementation
- Add proper styling and layout
- Implement error states and empty states

### Phase 2: Data Integration
- Implement FileStatsDataManager
- Connect to actual database
- Add real-time data updates
- Implement refresh functionality

### Phase 3: Advanced Visualizations
- Replace text placeholders with actual charts
- Add interactive chart features
- Implement chart customization options
- Add export functionality for statistics

### Phase 4: Performance Optimization
- Implement data caching
- Add pagination for large datasets
- Optimize chart rendering
- Add loading states for slow operations