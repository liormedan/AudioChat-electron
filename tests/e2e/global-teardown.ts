/**
 * Global Teardown for E2E Tests
 * ניקוי גלובלי לבדיקות E2E
 */

import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E test teardown...');
  
  // Cleanup test data
  await cleanupTestData();
  
  // Generate test summary
  await generateTestSummary();
  
  // Cleanup temporary files (optional)
  await cleanupTempFiles();
  
  console.log('✅ E2E test teardown completed');
}

async function cleanupTestData() {
  console.log('🗑️ Cleaning up test data...');
  
  try {
    const BACKEND_URL = 'http://127.0.0.1:5000';
    
    // Cleanup test database
    const response = await fetch(`${BACKEND_URL}/api/test/cleanup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        test_mode: true,
        cleanup_all: true 
      })
    });
    
    if (response.ok) {
      console.log('✅ Test data cleaned up successfully');
    } else {
      console.log('⚠️ Test data cleanup endpoint returned error');
    }
    
  } catch (error) {
    console.log('⚠️ Test data cleanup failed (this is usually okay):', error.message);
  }
}

async function generateTestSummary() {
  console.log('📊 Generating test summary...');
  
  try {
    const testResultsPath = path.join(__dirname, 'test-results.json');
    
    if (fs.existsSync(testResultsPath)) {
      const testResults = JSON.parse(fs.readFileSync(testResultsPath, 'utf8'));
      
      const summary = {
        timestamp: new Date().toISOString(),
        total: testResults.stats?.total || 0,
        passed: testResults.stats?.passed || 0,
        failed: testResults.stats?.failed || 0,
        skipped: testResults.stats?.skipped || 0,
        duration: testResults.stats?.duration || 0,
        suites: testResults.suites?.length || 0,
      };
      
      // Write summary to file
      const summaryPath = path.join(__dirname, 'test-summary.json');
      fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
      
      // Log summary to console
      console.log('📈 Test Summary:');
      console.log(`   Total: ${summary.total}`);
      console.log(`   Passed: ${summary.passed}`);
      console.log(`   Failed: ${summary.failed}`);
      console.log(`   Skipped: ${summary.skipped}`);
      console.log(`   Duration: ${Math.round(summary.duration / 1000)}s`);
      
      // Create simple HTML report
      const htmlReport = `
<!DOCTYPE html>
<html>
<head>
    <title>E2E Test Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .summary { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        .stat { display: inline-block; margin: 10px 20px 10px 0; }
        .passed { color: #28a745; }
        .failed { color: #dc3545; }
        .skipped { color: #ffc107; }
    </style>
</head>
<body>
    <h1>E2E Test Summary</h1>
    <div class="summary">
        <div class="stat">Total: <strong>${summary.total}</strong></div>
        <div class="stat passed">Passed: <strong>${summary.passed}</strong></div>
        <div class="stat failed">Failed: <strong>${summary.failed}</strong></div>
        <div class="stat skipped">Skipped: <strong>${summary.skipped}</strong></div>
        <div class="stat">Duration: <strong>${Math.round(summary.duration / 1000)}s</strong></div>
    </div>
    <p>Generated: ${summary.timestamp}</p>
</body>
</html>`;
      
      const htmlPath = path.join(__dirname, 'test-summary.html');
      fs.writeFileSync(htmlPath, htmlReport);
      
      console.log('✅ Test summary generated');
      
    } else {
      console.log('⚠️ No test results file found');
    }
    
  } catch (error) {
    console.error('❌ Failed to generate test summary:', error);
  }
}

async function cleanupTempFiles() {
  console.log('🧽 Cleaning up temporary files...');
  
  try {
    const tempDirs = [
      path.join(__dirname, 'temp'),
      path.join(__dirname, '.tmp'),
    ];
    
    for (const dir of tempDirs) {
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
        console.log(`   Removed: ${dir}`);
      }
    }
    
    // Clean up old screenshots and videos (keep last 10)
    const artifactDirs = ['screenshots', 'videos', 'traces'];
    
    for (const artifactDir of artifactDirs) {
      const dirPath = path.join(__dirname, artifactDir);
      if (fs.existsSync(dirPath)) {
        const files = fs.readdirSync(dirPath)
          .map(file => ({
            name: file,
            path: path.join(dirPath, file),
            mtime: fs.statSync(path.join(dirPath, file)).mtime
          }))
          .sort((a, b) => b.mtime.getTime() - a.mtime.getTime());
        
        // Keep only the 10 most recent files
        const filesToDelete = files.slice(10);
        for (const file of filesToDelete) {
          fs.unlinkSync(file.path);
        }
        
        if (filesToDelete.length > 0) {
          console.log(`   Cleaned up ${filesToDelete.length} old files from ${artifactDir}`);
        }
      }
    }
    
    console.log('✅ Temporary files cleaned up');
    
  } catch (error) {
    console.error('❌ Failed to cleanup temporary files:', error);
  }
}

export default globalTeardown;