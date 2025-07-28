export interface UploadResult {
  success: boolean;
  message?: string;
  file_id?: string;
  original_filename?: string;
  stored_filename?: string;
  file_size?: number;
  metadata?: AudioMetadata;
  validation?: ValidationResult;
  error?: string;
  stage?: string;
}

export interface ValidationResult {
  valid: boolean;
  file_size?: number;
  file_extension?: string;
  mime_type?: string;
  error?: string;
}

export interface AudioMetadata {
  duration?: number;
  sample_rate?: number;
  channels?: number;
  samples?: number;
  bitrate?: number;
  length?: number;
  file_size?: number;
  created_time?: number;
  modified_time?: number;
  file_extension?: string;
  tags?: Record<string, any>;
  format_info?: Record<string, any>;
}

export interface UploadedFileInfo {
  filename: string;
  file_path: string;
  file_size: number;
  created_time: number;
  modified_time: number;
}

export interface ListFilesResult {
  success: boolean;
  files?: UploadedFileInfo[];
  count?: number;
  error?: string;
}

export interface DeleteFileResult {
  success: boolean;
  message?: string;
  error?: string;
}

export interface MetadataResult {
  success: boolean;
  file_info?: UploadedFileInfo;
  metadata?: AudioMetadata;
  error?: string;
}

export class AudioUploadService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * Upload an audio file to the server
   */
  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<UploadResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable && onProgress) {
            const progress = (event.loaded / event.total) * 100;
            onProgress(progress);
          }
        });

        xhr.addEventListener('load', () => {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Network error during upload'));
        });

        xhr.addEventListener('timeout', () => {
          reject(new Error('Upload timeout'));
        });

        xhr.open('POST', `${this.baseUrl}/api/audio/upload`);
        xhr.timeout = 300000; // 5 minutes timeout
        xhr.send(formData);
      });

    } catch (error) {
      return {
        success: false,
        error: `Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        stage: 'client_error'
      };
    }
  }

  /**
   * Get list of all uploaded files
   */
  async listFiles(): Promise<ListFilesResult> {
    try {
      const response = await fetch(`${this.baseUrl}/api/audio/files`);
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to list files: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Delete an uploaded file by ID
   */
  async deleteFile(fileId: string): Promise<DeleteFileResult> {
    try {
      const response = await fetch(`${this.baseUrl}/api/audio/files/${fileId}`, {
        method: 'DELETE'
      });
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to delete file: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Get metadata for a specific file
   */
  async getFileMetadata(fileId: string): Promise<MetadataResult> {
    try {
      const response = await fetch(`${this.baseUrl}/api/audio/metadata/${fileId}`);
      const result = await response.json();
      return result;
    } catch (error) {
      return {
        success: false,
        error: `Failed to get metadata: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Validate file before upload (client-side basic validation)
   */
  validateFileBeforeUpload(file: File): { valid: boolean; error?: string } {
    const allowedExtensions = ['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a', 'wma', 'aiff', 'au'];
    const maxSize = 100 * 1024 * 1024; // 100MB

    // Check file size
    if (file.size > maxSize) {
      return {
        valid: false,
        error: `File size (${(file.size / 1024 / 1024).toFixed(1)}MB) exceeds maximum allowed size (100MB)`
      };
    }

    // Check file extension
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!extension || !allowedExtensions.includes(extension)) {
      return {
        valid: false,
        error: `File extension '${extension}' is not supported. Allowed: ${allowedExtensions.join(', ')}`
      };
    }

    // Check MIME type
    if (!file.type.startsWith('audio/')) {
      return {
        valid: false,
        error: 'File does not appear to be an audio file'
      };
    }

    return { valid: true };
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Format duration for display
   */
  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  }
}