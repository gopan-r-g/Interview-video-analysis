import React, { useState } from 'react';

function UploadForm({ onUploadSuccess, onStartUpload }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setUploadError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setUploadError('Please select a video file');
      return;
    }
    
    try {
      if (onStartUpload) onStartUpload();
      
      setIsUploading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Upload error response:", errorText);
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      onUploadSuccess(data);
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-form">
      {uploadError && <div className="error-message">{uploadError}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="file-input-container">
          <input 
            type="file" 
            id="video-file" 
            accept="video/*"
            onChange={handleFileChange}
            disabled={isUploading}
            className="file-input"
          />
          <label htmlFor="video-file" className="file-label">
            {file ? file.name : 'Select Video File'}
          </label>
        </div>
        
        <button 
          type="submit" 
          disabled={!file || isUploading}
          className="upload-button"
        >
          {isUploading ? (
            <>
              <span className="spinner"></span>
              <span>Uploading...</span>
            </>
          ) : (
            'Upload Video'
          )}
        </button>
      </form>
    </div>
  );
}

export default UploadForm;