import React, { useState, useEffect } from 'react';
import './App.css';
import UploadForm from './components/UploadForm';
import JobStatus from './components/JobStatus';
import AnalysisResults from './components/AnalysisResults';
import VideoPlayer from './components/VideoPlayer';

function App() {
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [error, setError] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);

  const handleUploadSuccess = (data) => {
    setJobId(data.job_id);
    setJobStatus(data);
    
    // Set the video URL to play the uploaded video
    if (data.video_url) {
      setVideoUrl(data.video_url);
    } else {
      // If API doesn't return video_url directly, construct it
      setVideoUrl(`/api/v1/videos/${data.job_id}`);
    }
    console.log("Set video URL to:", data.video_url || `/api/v1/videos/${data.job_id}`);
    setError(null);
    console.log('Upload success, job ID:', data.job_id);
  };

  useEffect(() => {
    let intervalId;
    
    if (jobId) {
      // Poll immediately without waiting for first interval
      pollJobStatus(jobId);
      
      // Set up frequent polling
      intervalId = setInterval(() => {
        pollJobStatus(jobId);
      }, 1000); // Poll every 100ms for responsive updates
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [jobId]);

  const pollJobStatus = async (id) => {
    try {
      const response = await fetch(`/api/v1/status/${id}`, {
        headers: {
          'Cache-Control': 'no-cache, no-store',
          'Pragma': 'no-cache'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch job status');
      }
      
      const data = await response.json();
      console.log("Status update:", data);
      
      // Update job status
      setJobStatus(data);
      
      // If job is completed, fetch results and stop polling
      if (data.status === 'COMPLETED' || data.status === 'completed') {
        fetchResults(id);
      }
      
    } catch (err) {
      console.error('Error fetching job status:', err);
      setError(err.message);
    }
  };

  const fetchResults = async (id) => {
    try {
      const response = await fetch(`/api/v1/results/${id}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch results');
      }
      
      const data = await response.json();
      console.log("Results received:", data);
      setAnalysisResults(data);
    } catch (err) {
      console.error('Error fetching results:', err);
      setError(`Failed to get analysis results: ${err.message}`);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Video Analysis Tool</h1>
        <p className="subtitle">AI-powered interview analysis</p>
      </header>
      
      <main className="app-content">
        {error && <div className="error-alert">{error}</div>}
        
        <div className="card">
          <h2>Upload Video</h2>
          <UploadForm onUploadSuccess={handleUploadSuccess} />
        </div>
        
        {/* Video Player for the uploaded video */}
        {videoUrl && jobStatus && (
          <div className="card">
            <VideoPlayer 
              videoUrl={videoUrl} 
              filename={jobStatus.filename || "Uploaded Video"} 
            />
          </div>
        )}
        
        {jobStatus && (
          <div className="card">
            <h2>Job Status</h2>
            <JobStatus status={jobStatus} />
          </div>
        )}
        
        {analysisResults && analysisResults.analysis_result && (
          <div className="card results-card">
            <h2>Analysis Results</h2>
            <AnalysisResults results={analysisResults.analysis_result} />
          </div>
        )}
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2023 Video Analysis Tool</p>
      </footer>
    </div>
  );
}

export default App;