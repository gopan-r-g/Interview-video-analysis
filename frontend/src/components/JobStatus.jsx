import React, { useEffect, useState } from 'react';

function JobStatus({ status }) {
  const [progressPercentage, setProgressPercentage] = useState(0);
  
  // Updated to match EXACTLY what's in your backend code
  const processingSteps = [
    "starting video processing",
    "extracting audio from video",
    "transcribing audio", 
    "analyzing body language",
    "scoring candidate"
  ];
  
  // Format the step name for display
  const formatStepName = (step) => {
    if (!step) return "Initializing";
    return step.charAt(0).toUpperCase() + step.slice(1);
  };

  // Update progress whenever current_step or progress changes
  useEffect(() => {
    // If we have a direct progress value from backend, use it
    if (status.progress !== undefined && status.progress !== null) {
      // Convert from 0-1 scale to percentage
      const progressValue = typeof status.progress === 'number' 
        ? Math.round(status.progress * 100)
        : 0;
      setProgressPercentage(progressValue);
      return;
    }
    
    // Otherwise calculate based on steps
    if (!status.current_step) {
      setProgressPercentage(5);
      return;
    }
    
    const currentStepLower = status.current_step.toLowerCase();
    const stepIndex = processingSteps.indexOf(currentStepLower);
    
    if (stepIndex >= 0) {
      const progress = Math.round(((stepIndex + 1) / processingSteps.length) * 100);
      setProgressPercentage(progress);
    }
    
    // If completed, always show 100%
    if (status.status?.toLowerCase() === 'completed') {
      setProgressPercentage(100);
    }
  }, [status.current_step, status.status, status.progress]);

  return (
    <div className="job-status-container">
      <div className="status-info">
        <div className="info-row">
          <div className="info-label">Job ID:</div>
          <div className="info-value">{status.job_id}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Filename:</div>
          <div className="info-value">{status.filename}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Status:</div>
          <div className="info-value">
            <span className={`status-badge status-${status.status?.toLowerCase()}`}>
              {status.status}
            </span>
          </div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Current Step:</div>
          <div className="info-value">{formatStepName(status.current_step)}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Created:</div>
          <div className="info-value">{new Date(status.created_at).toLocaleString()}</div>
        </div>
      </div>
      
      {/* Progress Bar Below the Status Info */}
      <div className="progress-section">
        <div className="progress-label">
          <span>Overall Progress</span>
          <span>{progressPercentage}%</span>
        </div>
        <div className="progress-bar-container">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
        <div className="current-step-label">
          {formatStepName(status.current_step)}
        </div>
      </div>
    </div>
  );
}

export default JobStatus;