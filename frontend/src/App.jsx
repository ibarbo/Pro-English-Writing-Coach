// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [correctedText, setCorrectedText] = useState('');
  const [changesList, setChangesList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dailyTask, setDailyTask] = useState(''); // Holds the fetched daily task
  const [loadingTask, setLoadingTask] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  // showWritingArea state can be removed or simplified if the main input is always visible.
  // For now, let's just make the main input section always visible.

  const API_BASE_URL = 'http://localhost:5000';

  // useEffect for word counting. This remains simple and counts only inputText.
  useEffect(() => {
    const words = inputText.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [inputText]);


  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    // When getting feedback, clear previous daily task if it's there
    // This makes the UI clean for new feedback sessions.
    setDailyTask('');
    // Clear previous feedback results
    setCorrectedText('');
    setChangesList([]);


    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/feedback`, {
        text: inputText,
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
    setError(null);
    setLoadingTask(true);

    // When fetching a new task, clear previous results, but keep current input if desired
    setDailyTask(''); // Clear previous task display
    setCorrectedText(''); // Clear previous corrections
    setChangesList([]); // Clear previous changes

    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/daily-task`);
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

  // New function to start a fresh writing session (clears input, not task)
  const startNewWritingSession = () => {
    setInputText(''); // Clear user's input
    setWordCount(0); // Reset word count
    setCorrectedText(''); // Clear feedback
    setChangesList([]); // Clear feedback list
    setDailyTask(''); // Clear task if it was there, for a completely fresh start
    setError(null); // Clear any errors
  };

  return (
    <div className="container">
      <h1 className="title">English Writing Coach</h1>

      {/* Button to start a new blank writing session */}
      <div className="action-buttons">
        <button
          className="start-new-button"
          onClick={startNewWritingSession}
        >
          Start a New Blank Writing Session
        </button>
      </div>


      {/* Daily Task Section - remains visible when task is fetched */}
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
            <p>{dailyTask}</p> {/* Task is now displayed here permanently */}
            {/* The 'Start Writing This Task' button is removed as input is always visible.
                Users just type in the main input area below, referring to the task above. */}
          </div>
        )}
      </div>

      {/* --- Main Writing/Feedback Area - Always visible --- */}
      <div className="input-section">
        <h2 className="section-title">Your Text</h2>
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