import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [correctedText, setCorrectedText] = useState('');
  const [changesList, setChangesList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dailyTask, setDailyTask] = useState('');
  const [loadingTask, setLoadingTask] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  // --- NEW STATE: To store the user's target English level ---
  const [targetLevel, setTargetLevel] = useState('B2'); // Default to B2

  // --- NEW STATE: To store the user's choice for feature (task or vocabulary) ---
  const [selectedFeature, setSelectedFeature] = useState('task'); // 'task' or 'vocabulary'

  // --- NEW STATE: To store optional writing context ---
  const [writingContext, setWritingContext] = useState('');

  // --- NEW STATE: To store generated vocabulary list ---
  const [vocabularyList, setVocabularyList] = useState([]);
  const [loadingVocabulary, setLoadingVocabulary] = useState(false);
  // --- NEW STATE: To store optional vocabulary topic ---
  const [vocabularyTopic, setVocabularyTopic] = useState('');


  const API_BASE_URL = 'http://localhost:5000';

  useEffect(() => {
    const words = inputText.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [inputText]);

  // Function to clear all non-level/feature related states
  const clearResults = () => {
    setCorrectedText('');
    setChangesList([]);
    setDailyTask('');
    setVocabularyList([]);
    setError(null);
    setLoading(false);
    setLoadingTask(false);
    setLoadingVocabulary(false);
  };

  const handleSubmit = async () => {
    clearResults(); // Clear previous results on new submission
    setLoading(true);

    try {
      // --- MODIFIED: Include targetLevel and writingContext in the feedback request ---
      const response = await axios.post(`${API_BASE_URL}/api/v1/feedback`, {
        text: inputText,
        level: targetLevel,
        context: writingContext, // Pass the optional context
      });

      setCorrectedText(response.data.corrected_text);
      setChangesList(response.data.changes_list);

    } catch (err) {
      console.error("Error fetching feedback:", err);
      if (err.response) {
        setError(err.response.data.detail || 'An error occurred with the API. Please try again.');
      } else if (err.request) {
        setError('No response from the server. Is the backend running?');
      } else {
        setError('An unexpected error occurred. Please check your network.');
      }
      setCorrectedText('');
      setChangesList([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchDailyTask = async () => {
    clearResults(); // Clear previous results
    setLoadingTask(true);

    try {
      // --- MODIFIED: Include targetLevel and writingContext in the daily task request ---
      const response = await axios.get(`${API_BASE_URL}/api/v1/daily-task`, {
        params: {
            level: targetLevel,
            context: writingContext // Pass optional context
        }
      });
      setDailyTask(response.data.task);
    } catch (err) {
      console.error("Error fetching daily task:", err);
      if (err.response) {
        setError(err.response.data.detail || 'Failed to fetch daily task from API.');
      } else if (err.request) {
        setError('No response from the server when fetching daily task. Is the backend running?');
      } else {
        setError('An unexpected error occurred while fetching daily task. Please check your network.');
      }
    } finally {
      setLoadingTask(false);
    }
  };

  // --- ADDED: New function to fetch Vocabulary List ---
  const fetchVocabularyList = async () => {
    clearResults(); // Clear previous results
    setLoadingVocabulary(true);

    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/vocabulary-list`, {
        params: {
          level: targetLevel,
          topic: vocabularyTopic // Pass optional topic
        }
      });
      setVocabularyList(response.data.vocabulary);
    } catch (err) {
      console.error("Error fetching vocabulary list:", err);
      if (err.response) {
        setError(err.response.data.detail || 'Failed to fetch vocabulary list from API.');
      } else if (err.request) {
        setError('No response from the server when fetching vocabulary list. Is the backend running?');
      } else {
        setError('An unexpected error occurred while fetching vocabulary list. Please check your network.');
      }
    } finally {
      setLoadingVocabulary(false);
    }
  };


  const startNewWritingSession = () => {
    setInputText('');
    setWordCount(0);
    setWritingContext(''); // Clear context too
    setVocabularyTopic(''); // Clear vocab topic too
    clearResults(); // Clear all results
  };

  return (
    <div className="container">
      <h1 className="title">English Writing Coach</h1>

      <div className="level-selector-section">
        <label htmlFor="target-level" >Target English Level: </label>
        <select
          id="target-level"
          value={targetLevel}
          onChange={(e) => setTargetLevel(e.target.value)}
        >
          <option value="B1">B1 (Intermediate)</option>
          <option value="B2">B2 (Upper-Intermediate)</option>
          <option value="C1">C1 (Advanced)</option>
        </select>
      </div>

      <div className="action-buttons">
        <button
          className="start-new-button"
          onClick={startNewWritingSession}
        >
          Start a New Blank Writing Session
        </button>
      </div>

      {/* --- ADDED: Feature Selection Radios --- */}
      <div className="feature-selector-section">
        <label className="radio-label">
          <input
            type="radio"
            value="task"
            checked={selectedFeature === 'task'}
            onChange={() => { setSelectedFeature('task'); clearResults(); }}
          />
          Daily Writing Task
        </label>
        <label className="radio-label">
          <input
            type="radio"
            value="vocabulary"
            checked={selectedFeature === 'vocabulary'}
            onChange={() => { setSelectedFeature('vocabulary'); clearResults(); }}
          />
          Vocabulary List
        </label>
      </div>

      {/* --- CONDITIONAL RENDERING FOR TASK OR VOCABULARY --- */}
      {selectedFeature === 'task' && (
        <div className="daily-task-section">
          <button
            className="get-task-button"
            onClick={fetchDailyTask}
            disabled={loadingTask}
          >
            {loadingTask ? 'Generating Task...' : 'Get Daily Writing Task'}
          </button>
          {dailyTask && (
            <div className="task-display">
              <h2 className="section-title">Daily Task</h2>
              <p>{dailyTask}</p>
            </div>
          )}
        </div>
      )}

      {selectedFeature === 'vocabulary' && (
        <div className="vocab-section">
          <div className="vocab-topic-input">
            <label htmlFor="vocabulary-topic">Optional Vocabulary Topic: </label>
            <input
              type="text"
              id="vocabulary-topic"
              className="context-input" // Reusing context-input style
              placeholder="e.g., Finance, Travel, Science"
              value={vocabularyTopic}
              onChange={(e) => setVocabularyTopic(e.target.value)}
            />
          </div>
          <button
            className="get-vocab-button"
            onClick={fetchVocabularyList}
            disabled={loadingVocabulary}
          >
            {loadingVocabulary ? 'Generating Vocabulary...' : 'Get Vocabulary List'}
          </button>
          {vocabularyList.length > 0 && (
            <div className="vocabulary-display">
              <h2 className="section-title">Vocabulary List</h2>
              <ul className="vocabulary-list">
                {vocabularyList.map((item, index) => (
                  <li key={index} className="vocabulary-item">
                    <strong>Word:</strong> {item.word}<br />
                    <strong>Definition:</strong> {item.definition}<br />
                    <strong>Example:</strong> {item.example}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="input-section">
        <h2 className="section-title">Your Text</h2>
        {/* --- MOVED: Optional Writing Context Input now inside input-section and before textarea --- */}
        <div className="context-input-section">
          <label htmlFor="writing-context">Optional Writing Context (e.g., "professional email", "essay"): </label>
          <input
            type="text"
            id="writing-context"
            className="context-input"
            placeholder="e.g., Professional email, College essay, Creative story"
            value={writingContext}
            onChange={(e) => setWritingContext(e.target.value)}
          />
        </div>
        <textarea
          className="text-input"
          placeholder="Enter the text you want to get feedback on, or start writing your daily task response here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        ></textarea>
        <div className="word-count">
          Word Count: {wordCount}
        </div>
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={loading || inputText.trim() === ''}
        >
          {loading ? 'Analyzing...' : 'Get Feedback'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {correctedText && (
        <div className="output-section">
          <h2 className="section-title">Corrected Text</h2>
          <p className="corrected-text-display">
            {correctedText}
          </p>
        </div>
      )}

      {changesList.length > 0 && (
        <div className="changes-section">
          <h2 className="section-title">Changes Made</h2>
          <ul className="changes-list">
            {changesList.map((change, index) => (
              <li key={index}>{change}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;