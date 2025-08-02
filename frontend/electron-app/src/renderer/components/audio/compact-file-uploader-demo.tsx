import React, { useState } from 'react';
import { CompactFileUploader } from './compact-file-uploader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

export const CompactFileUploaderDemo: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFileSelect = (file: File) => {
    setSelectedFiles(prev => [...prev, file]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleClearAll = () => {
    setSelectedFiles([]);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Compact File Uploader Demo</CardTitle>
          <CardDescription>
            A compact file uploader with 200px fixed height, drag-and-drop support, and multi-file tabs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CompactFileUploader
            onFileSelect={handleFileSelect}
            selectedFiles={selectedFiles}
            onRemoveFile={handleRemoveFile}
            onClearAll={handleClearAll}
            dragDropOnly={true}
            maxHeight={200}
          />
        </CardContent>
      </Card>

      {selectedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Files ({selectedFiles.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-muted/20 rounded">
                  <div>
                    <p className="font-medium text-sm">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {file.type || 'Unknown type'}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};