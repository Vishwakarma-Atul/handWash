import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';

const WebcamCapture = forwardRef((props, ref) => {
  const videoRef = useRef(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const streamInterval = useRef(null);

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices()
      .then(devices => setDevices(devices.filter(device => device.kind === 'videoinput')))
      .catch(err => console.error('Error enumerating devices:', err));
  }, []);

  useImperativeHandle(ref, () => ({
    startSendingFrames: (ws) => {
      if (selectedDevice && videoRef.current.srcObject) {
        const imageCapture = new ImageCapture(videoRef.current.srcObject.getVideoTracks()[0]);
        streamInterval.current = setInterval(async () => {
          const frame = await imageCapture.grabFrame();
          const canvas = document.createElement('canvas');
          canvas.width = frame.width;
          canvas.height = frame.height;
          const ctx = canvas.getContext('2d');
          
          // Rotate the frame by 180 degrees
          ctx.translate(canvas.width / 2, canvas.height / 2);
          ctx.rotate(Math.PI);
          ctx.translate(-canvas.width / 2, -canvas.height / 2);
          
          ctx.drawImage(frame, 0, 0);
          const imageData = canvas.toDataURL('image/jpeg');
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(imageData);
          }
        }, 500); // Send frame every 500ms (2 fps)
      }
    }
  }));

  const startWebcamStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: selectedDevice } }
      });
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
    } catch (err) {
      console.error('Error accessing the camera:', err);
    }
  };

  useEffect(() => {
    if (selectedDevice) {
      startWebcamStream();
    }
  }, [selectedDevice]);

  useEffect(() => {
    return () => {
      if (streamInterval.current) {
        clearInterval(streamInterval.current);
      }
    };
  }, []);

  return (
    <div>
      <select onChange={(e) => setSelectedDevice(e.target.value)} value={selectedDevice}>
        <option value="">Select a camera</option>
        {devices.map(device => (
          <option key={device.deviceId} value={device.deviceId}>
            {device.label || `Camera ${device.deviceId}`}
          </option>
        ))}
      </select>
      <video ref={videoRef} autoPlay playsInline />
    </div>
  );
});

export default WebcamCapture;