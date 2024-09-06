import React, { useRef, useEffect, useState } from 'react';

function CameraFeed() {
  const videoRef = useRef(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices()
      .then(devices => {
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        setDevices(videoDevices);
        if (videoDevices.length > 0) {
          setSelectedDevice(videoDevices[0].deviceId);
        }
      });
  }, []);

  useEffect(() => {
    if (selectedDevice) {
      setupCamera();
    }
  }, [selectedDevice]);

  async function setupCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: selectedDevice } }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
    } catch (err) {
      console.error("Error accessing the camera: ", err);
    }
  }

  const handleDeviceChange = (event) => {
    setSelectedDevice(event.target.value);
  };

  return (
    <div className="camera-feed">
      <select value={selectedDevice} onChange={handleDeviceChange}>
        {devices.map(device => (
          <option key={device.deviceId} value={device.deviceId}>
            {device.label || `Camera ${devices.indexOf(device) + 1}`}
          </option>
        ))}
      </select>
      <video ref={videoRef} />
    </div>
  );
}

export default CameraFeed;