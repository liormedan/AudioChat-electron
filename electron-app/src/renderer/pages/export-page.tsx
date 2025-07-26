import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Download, FileAudio, Settings } from 'lucide-react';

export const ExportPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Export Center</h1>
        <p className="text-muted-foreground">
          Export and download your processed audio files
        </p>
      </div>

      {/* Export Queue */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Download className="h-5 w-5" />
            <span>Export Queue</span>
          </CardTitle>
          <CardDescription>
            Manage your export jobs and download files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileAudio className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">
              No files in export queue
            </p>
            <Button variant="outline">Add Files to Export</Button>
          </div>
        </CardContent>
      </Card>

      {/* Export Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Export Settings</span>
          </CardTitle>
          <CardDescription>
            Configure export format and quality settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Export settings configuration will be implemented here.
          </p>
        </CardContent>
      </Card>

      {/* Export History */}
      <Card>
        <CardHeader>
          <CardTitle>Export History</CardTitle>
          <CardDescription>
            View previously exported files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Export history will be displayed here.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};