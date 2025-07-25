# Requirements Document

## Introduction

מסמך זה מגדיר את הדרישות לעיצוב מחדש של דף הבית (Home) באפליקציית Audio Chat QT ושינוי צבעי התפריט ללבן. דף הבית יהיה הדף הראשי שהמשתמש רואה בפתיחת האפליקציה, ויכלול אזור צ'אט ואזור להעלאת קבצים. בנוסף, צבעי התפריט ישונו מכחול ללבן לשיפור הנראות והקריאות.

## Requirements

### Requirement 1

**User Story:** As a user, I want the Home page to include both chat and file upload functionality, so that I can interact with the AI and upload audio files from the same screen.

#### Acceptance Criteria

1. WHEN the user opens the application THEN the system SHALL display the Home page by default
2. WHEN the Home page loads THEN the system SHALL display a chat interface for interacting with the AI
3. WHEN the Home page loads THEN the system SHALL display a file upload area for audio files
4. WHEN the user types in the chat input THEN the system SHALL send the message to the AI and display the response
5. WHEN the user uploads an audio file THEN the system SHALL process the file and make it available for AI analysis

### Requirement 2

**User Story:** As a user, I want a clean and intuitive layout for the Home page, so that I can easily navigate and use all features.

#### Acceptance Criteria

1. WHEN the Home page is displayed THEN the system SHALL organize content in a clear two-panel layout
2. WHEN the Home page is displayed THEN the system SHALL ensure the chat panel is prominently visible
3. WHEN the Home page is displayed THEN the system SHALL ensure the file upload area is easily accessible
4. WHEN the user resizes the window THEN the system SHALL adapt the layout responsively
5. WHEN the user has many chat messages THEN the system SHALL provide proper scrolling functionality

### Requirement 3

**User Story:** As a user, I want the sidebar menu to have white text instead of blue, so that it's easier to read and matches the application's design.

#### Acceptance Criteria

1. WHEN the sidebar is displayed THEN the system SHALL use white color for all text elements
2. WHEN a sidebar button is active THEN the system SHALL highlight it while maintaining white text
3. WHEN a sidebar button is hovered THEN the system SHALL show appropriate hover effects with white text
4. WHEN the sidebar section titles are displayed THEN the system SHALL use white color with appropriate opacity
5. WHEN the application theme changes THEN the system SHALL ensure sidebar text remains white

### Requirement 4

**User Story:** As a user, I want the Home page to remember my recent interactions, so that I can continue where I left off.

#### Acceptance Criteria

1. WHEN the user returns to the Home page THEN the system SHALL display recent chat history
2. WHEN the user uploads files THEN the system SHALL show them in a recent uploads section
3. WHEN the user has no previous interactions THEN the system SHALL display appropriate welcome messages
4. WHEN the chat history exceeds the display limit THEN the system SHALL provide pagination or scrolling
5. WHEN the user clears the chat history THEN the system SHALL confirm before removing all messages
