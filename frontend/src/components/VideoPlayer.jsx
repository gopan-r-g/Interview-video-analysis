import React, { useRef, useState, useEffect } from 'react';

function VideoPlayer({ videoUrl, filename }) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Log when props change
  useEffect(() => {
    console.log("VideoPlayer received URL:", videoUrl);
    // Reset states when video URL changes
    setIsPlaying(false);
    setCurrentTime(0);
    setIsLoading(true);
    setError(null);
  }, [videoUrl]);
  
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        // Attempt to play and handle any errors
        const playPromise = videoRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log("Video playback started successfully");
            })
            .catch(err => {
              console.error("Error playing video:", err);
              setError("Could not play video: " + err.message);
            });
        }
      }
      setIsPlaying(!isPlaying);
    }
  };
  
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };
  
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      console.log("Video metadata loaded, duration:", videoRef.current.duration);
      setDuration(videoRef.current.duration);
      setIsLoading(false);
    }
  };
  
  const handleLoadedData = () => {
    console.log("Video data loaded and ready to play");
    setIsLoading(false);
  };
  
  const handleError = (e) => {
    console.error("Video error:", e);
    setError("Error loading video. Please try again.");
    setIsLoading(false);
  };
  
  const handleSeek = (e) => {
    const newTime = e.target.value;
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };
  
  // Format time in MM:SS format
  const formatTime = (timeInSeconds) => {
    if (!timeInSeconds) return "00:00";
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="video-player">
      <h3>Video Preview: {filename}</h3>
      <div className="video-container">
        {isLoading && <div className="video-loading">Loading video...</div>}
        {error && <div className="video-error">{error}</div>}
        
        <video
          ref={videoRef}
          src={videoUrl}
          controls  // Add default controls as fallback
          preload="auto"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onLoadedData={handleLoadedData}
          onError={handleError}
          onClick={togglePlay}
          playsInline // For better mobile support
        />
        
        {!isLoading && !error && (
          <div className="video-controls">
            <button 
              className="play-button" 
              onClick={togglePlay}
              aria-label={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? "⏸️" : "▶️"}
            </button>
            
            <div className="time-control">
              <span className="time-display">{formatTime(currentTime)}</span>
              <input
                type="range"
                min="0"
                max={duration || 0}
                value={currentTime || 0}
                onChange={handleSeek}
                className="seek-slider"
              />
              <span className="time-display">{formatTime(duration)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoPlayer;