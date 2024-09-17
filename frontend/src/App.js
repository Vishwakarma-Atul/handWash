import React, { useState, useRef } from 'react';

import './App.css';
import ProgressSlider from './components/ProgressSlider';
import WebcamCapture from './components/WebcamCapture';

const wsUrl = process.env.REACT_APP_BACKEND_URL + '/ws_model';

function App() {
  const [counters, setCounters] = useState({});
  const [status, setStatus] = useState('Connecting...');
  const [socket, setSocket] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [maxCount, setMaxCount] = useState(100);
  const webcamRef = useRef(null);

  const connectWebSocket = () => {
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatus('Connected');
      setSocket(ws);
      // ws.send(JSON.stringify({ action: 'start' }));
      webcamRef.current.startSendingFrames(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setCounters(data.counters);
      setStatus(data.status);
      setMaxCount(data.max_count);
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

  const handleStart = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      const newSocket = connectWebSocket();
      setSocket(newSocket);
    }
  };

  const handleReset = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.close();
    }
    setCounters({});
    setStatus('Disconnected');
    setShowPopup(false);
  };

  return (
    <div className="App">
      <h1>Project Hand Wash</h1>
      <p>Status: {status}</p>
      <div className="button-group">
        <button onClick={handleStart}>Start</button>
        <button onClick={handleReset}>Reset</button>
      </div>
      <div><br></br><br></br></div>
      <div className="content-wrapper">
        <div className="camera-section">
          <WebcamCapture ref={webcamRef} />
        </div>
        <div className="sliders-section">
          <h2>Steps Count</h2>
          {Object.entries(counters).map(([className, count]) => (
            <ProgressSlider
              key={className}
              name={className}
              value={Math.min(Math.round((count / maxCount) * 100), 100)}
            />
          ))}
        </div>
      </div>
      {showPopup && (
        <div className="popup">
          <div className="popup-content">
            <h2>Sanitize Hands!</h2>
            <p>{popupMessage}</p>
            <button onClick={() => setShowPopup(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;