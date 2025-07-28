// Simple test to ensure new home page features exist
const fs = require('fs');

console.log('Testing Home Page enhancements...');

try {
  const queriesContent = fs.readFileSync('./src/renderer/hooks/use-queries.ts', 'utf8');
  if (queriesContent.includes('useQuickStats')) {
    console.log('✓ useQuickStats hook found');
  } else {
    console.log('✗ useQuickStats hook missing');
  }

  const dropZoneExists = fs.existsSync('./src/renderer/components/file-drop-zone.tsx');
  console.log(dropZoneExists ? '✓ FileDropZone component exists' : '✗ FileDropZone component missing');

  const homeContent = fs.readFileSync('./src/renderer/pages/home-page.tsx', 'utf8');
  if (homeContent.includes('<FileDropZone')) {
    console.log('✓ HomePage uses FileDropZone');
  } else {
    console.log('✗ HomePage missing FileDropZone');
  }

  console.log('Home Page feature test complete.');
} catch (err) {
  console.error('Test failed:', err.message);
}
