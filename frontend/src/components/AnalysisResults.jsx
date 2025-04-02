import React, { useState } from 'react';

function AnalysisResults({ results }) {
  const [activeTab, setActiveTab] = useState('scores');
  
  const candidateScores = results.candidate_score || {};
  const bodyLanguageAnalysis = results.body_language_analysis || {};
  
  // Helper to format category names
  const formatCategory = (category) => {
    return category
      .replace(/_score$/, '')
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="analysis-results">
      <div className="tabs">
        <button 
          className={`tab-button ${activeTab === 'scores' ? 'active' : ''}`}
          onClick={() => setActiveTab('scores')}
        >
          Scores
        </button>
        <button 
          className={`tab-button ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Body Language And Voice Analysis Result
        </button>
      </div>
      
      {activeTab === 'scores' && (
        <div className="scores-tab">
          <h3>Candidate Evaluation Scores</h3>
          
          <div className="score-cards">
            {Object.entries(candidateScores).map(([category, details]) => {
              const [feedback, score] = details;
              return (
                <div key={category} className="score-card">
                  <div className="score-header">
                    <div className="score-title">{formatCategory(category)}</div>
                    <div className="score-value">{score}/10</div>
                  </div>
                  <div className="score-meter">
                    <div className="score-meter-fill" style={{ width: `${score * 10}%` }}></div>
                  </div>
                  <p className="score-feedback">{feedback}</p>
                </div>
              );
            })}
          </div>
          
          <div className="overall-score">
            <h3>Overall Performance</h3>
            {Object.entries(candidateScores).length > 0 && (
              <div className="score-summary">
                <div className="average-score">
                  {(Object.entries(candidateScores).reduce((sum, [_, details]) => sum + details[1], 0) / 
                    Object.entries(candidateScores).length).toFixed(1)}
                  <span>/10</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {activeTab === 'analysis' && (
        <div className="analysis-tab">          
          {Object.entries(bodyLanguageAnalysis).map(([category, analysis]) => (
            <div key={category} className="analysis-section">
              <h4>{formatCategory(category)}</h4>
              <p>{analysis}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AnalysisResults;