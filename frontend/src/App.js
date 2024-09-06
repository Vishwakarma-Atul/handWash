import React, { useState, useEffect } from 'react';
import './App.css';
import ProgressSlider from './ProgressSlider';
import CameraFeed from './CameraFeed';

function App() {
  const [counters, setCounters] = useState({});
  const [status, setStatus] = useState('Connecting...');
  const [socket, setSocket] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');

  const connectWebSocket = () => {
    const ws = new WebSocket(process.env.REACT_APP_WS_URL);
    
    ws.onopen = () => {
      setStatus('Connected');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setCounters(data.counters);
      setStatus(data.status);
      if (data.status === 'complete' && !showPopup) {
        setShowPopup(true);
        setPopupMessage(data.message);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('Error');
    };

    ws.onclose = () => {
      setStatus('Completed');
    };

    return ws;
  };

  useEffect(() => {
    const ws = connectWebSocket();
    return () => {
      ws.close();
    };
  }, []);

  const handleReset = () => {
    if (socket) {
      socket.close();
    }
    setShowPopup(false);
    setCounters({});
    const newSocket = connectWebSocket();
    setSocket(newSocket);
  };

  return (
    <div className="App">
      <h1>Project Hand Wash</h1>
      <p>Status: {status}</p>
      <button onClick={handleReset}>Reset Counters</button>
      <div><br></br><br></br></div>
      <div className="content-wrapper">
        <div className="camera-section">
          <CameraFeed />
        </div>
        <div className="sliders-section">
          <h2>Steps Count</h2>
          {Object.entries(counters).map(([className, count]) => (
            <ProgressSlider
              key={className}
              name={className}
              value={Math.min(Math.round((count / 100) * 100), 100)}
            />
          ))}
        </div>
      </div>
      {showPopup && (
        <div className="popup">
          <div className="popup-content">
            <h2>Test Passed!</h2>
            <p>{popupMessage}</p>
            <button onClick={() => setShowPopup(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;