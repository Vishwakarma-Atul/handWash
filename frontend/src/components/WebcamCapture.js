import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';

const WebcamCapture = forwardRef((props, ref) => {
  const videoRef = useRef(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const streamInterval = useRef(null);

  const refreshDevices = async (promptForPermission = true) => {
    try {
      // If we want labels, prompt the user for camera permission first.
      if (promptForPermission) {
        const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
        // stop the temporary stream so we don't hold the camera
        tempStream.getTracks().forEach(t => t.stop());
      }
    } catch (err) {
      // user may deny permission — still try to enumerate devices (may be empty or unlabeled)
      console.warn('Temporary getUserMedia failed:', err);
    }
    try {
      const all = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = all.filter(d => d.kind === 'videoinput');
      setDevices(videoInputs);
      // auto-select first camera if none selected yet
      if (videoInputs.length && !selectedDevice) {
        setSelectedDevice(videoInputs[0].deviceId);
      }
    } catch (err) {
      console.error('Error enumerating devices:', err);
    }
  };

  useEffect(() => {
    // initial refresh (prompt for permission to get labels)
    refreshDevices(true);

    // refresh when devices change (e.g. plug/unplug)
    const onDeviceChange = () => refreshDevices(false);
    navigator.mediaDevices.addEventListener('devicechange', onDeviceChange);
    return () => navigator.mediaDevices.removeEventListener('devicechange', onDeviceChange);
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
   <div className="camera-container">
     <select 
       className="camera-select"
       onChange={(e) => setSelectedDevice(e.target.value)} 
       value={selectedDevice}
     >
       <option value="">Select a camera</option>
       {devices.map(device => (
         <option key={device.deviceId} value={device.deviceId}>
           {device.label || `Camera ${device.deviceId}`}
         </option>
       ))}
     </select>
     {/* <button type="button" onClick={() => refreshDevices(true)}>Refresh cameras</button> */}
     <video ref={videoRef} autoPlay playsInline />
   </div>
  );
});

export default WebcamCapture;