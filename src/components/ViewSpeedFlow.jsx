import React from 'react';

const ViewSpeedFlow = () => {
  const handleDownload = () => {
    const downloadLink = '/downloads/speedflow.exe';
    const link = document.createElement('a');
    link.href = downloadLink;
    link.download = 'speedflow.exe';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      // ...existing code...
      <button onClick={handleDownload}>
        Download Now
      </button>
      // ...existing code...
    </div>
  );
};

export default ViewSpeedFlow;
