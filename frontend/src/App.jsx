// frontend/src/App.jsx
import { useState } from 'react';
import axios from 'axios'; // For making HTTP requests
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [correctedText, setCorrectedText] = useState('');
  const [changesList, setChangesList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:5000'; // Your FastAPI backend URL

  const handleSubmit = async () => {
    setError(null); // Clear previous errors
    setLoading(true); // Indicate loading state
    setCorrectedText(''); // Clear previous results
    setChangesList([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/feedback`, {
        text: inputText,
      });

      setCorrectedText(response.data.corrected_text);
      setChangesList(response.data.changes_list);

    } catch (err) {
      console.error("Error fetching feedback:", err);
      // More user-friendly error message
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(err.response.data.detail || 'An error occurred with the API. Please try again.');
      } else if (err.request) {
        // The request was made but no response was received
        setError('No response from the server. Is the backend running?');
      } else {
        // Something else happened in setting up the request that triggered an Error
        setError('An unexpected error occurred. Please check your network.');
      }
    } finally {
      setLoading(false); // End loading state
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: '40px auto', padding: '20px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>English Writing Coach</h1>

      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '1.2em', color: '#555' }}>Your Text</h2>
        <textarea
          style={{ width: '100%', minHeight: '150px', padding: '10px', fontSize: '1em', border: '1px solid #ccc', borderRadius: '4px', resize: 'vertical' }}
          placeholder="Enter the text you want to get feedback on..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        ></textarea>
        <button
          style={{ padding: '10px 20px', fontSize: '1em', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' }}
          onClick={handleSubmit}
          disabled={loading || inputText.trim() === ''} // Disable button when loading or input is empty
        >
          {loading ? 'Analyzing...' : 'Get Feedback'}
        </button>
      </div>

      {error && (
        <div style={{ color: 'red', marginBottom: '20px', padding: '10px', border: '1px solid red', borderRadius: '4px', backgroundColor: '#ffe6e6' }}>
          Error: {error}
        </div>
      )}

      {correctedText && (
        <div style={{ marginBottom: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <h2 style={{ fontSize: '1.2em', color: '#555' }}>Corrected Text</h2>
          <p style={{ backgroundColor: '#f9f9f9', padding: '15px', border: '1px solid #ddd', borderRadius: '4px', lineHeight: '1.6em', whiteSpace: 'pre-wrap' }}>
            {correctedText}
          </p>
        </div>
      )}

      {changesList.length > 0 && (
        <div style={{ borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <h2 style={{ fontSize: '1.2em', color: '#555' }}>Changes Made</h2>
          <ul style={{ listStyleType: 'disc', paddingLeft: '20px' }}>
            {changesList.map((change, index) => (
              <li key={index} style={{ marginBottom: '8px', lineHeight: '1.4em' }}>{change}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;