// Import React library for building UI components
import React from 'react';
// Import ReactDOM for rendering React components to DOM
import ReactDOM from 'react-dom/client';
// Import main App component
import App from './App';
// Import Tailwind CSS styles
import './index.css';

// Get root DOM element where React app will be mounted
const root = ReactDOM.createRoot(document.getElementById('root'));
// Render App component inside root element
root.render(
  // React.StrictMode enables additional checks and warnings in development
  <React.StrictMode>
    {/* Main App component */}
    <App />
  </React.StrictMode>
);
