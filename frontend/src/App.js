// Import React library for building UI components
import React, { useState, useEffect } from 'react';
// Import axios library for making HTTP requests to backend API
import axios from 'axios';
// Import ChatComponent for medical chat interface
import ChatComponent from './components/ChatComponent';
// Import Sidebar component for navigation
import Sidebar from './components/Sidebar';

// Main App component that renders the entire application
function App() {
  // State variable to store chat history
  const [chatHistory, setChatHistory] = useState([]);
  // State variable to track current chat
  const [currentChat, setCurrentChat] = useState(null);
  // State variable to track loading state for chat history
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Function to handle new chat creation
  const handleNewChat = () => {
    // Log new chat action for debugging
    console.log('New chat button clicked');
    // Reset current chat to start fresh
    setCurrentChat(null);
  };

  // Function to handle chat selection from history
  const handleSelectChat = (chat) => {
    // Set selected chat as current chat
    setCurrentChat(chat);
  };

  // Function to fetch chat history from MongoDB via API
  const fetchChatHistory = async () => {
    try {
      // Set loading state to true
      setLoadingHistory(true);
      // Make GET request to backend API to retrieve all chat sessions
      const response = await axios.get('http://localhost:8000/api/sessions');
      // Update chat history state with data from API
      setChatHistory(response.data);
      // Log successful fetch
      console.log('Chat history loaded from database');
    } catch (err) {
      // Handle errors from API call
      // Check if error has response data
      if (err.response) {
        // Log error message from API response
        console.error('Error fetching chat history:', err.response.data.detail || 'An error occurred');
      } else if (err.request) {
        // Log error if request was made but no response received
        console.error('Unable to connect to the server. Please check if the backend is running.');
      } else {
        // Log generic error message for other errors
        console.error('An unexpected error occurred while fetching chat history');
      }
      // Set empty array on error to prevent UI issues
      setChatHistory([]);
    } finally {
      // Set loading state to false after API call completes
      setLoadingHistory(false);
    }
  };

  // useEffect hook to fetch chat history when component mounts
  useEffect(() => {
    // Call fetchChatHistory function on component mount
    fetchChatHistory();
  }, []); // Empty dependency array means this runs only once on mount

  // Function to add chat to history (called from ChatComponent)
  const addToHistory = (chatData) => {
    // Refresh chat history from database after adding new chat
    fetchChatHistory();
  };

  // Function to handle chat update (rename, pin, etc.)
  const handleChatUpdate = async (chatId, updates) => {
    try {
      // Make PATCH request to backend API to update chat session
      await axios.patch(`http://localhost:8000/api/sessions/${chatId}`, updates);
      // Refresh chat history from database after update
      fetchChatHistory();
      // Log successful update
      console.log('Chat updated successfully');
    } catch (err) {
      // Handle errors from API call
      if (err.response) {
        // Log error message from API response
        console.error('Error updating chat:', err.response.data.detail || 'An error occurred');
        // Show alert to user
        alert('Failed to update chat. Please try again.');
      } else if (err.request) {
        // Log error if request was made but no response received
        console.error('Unable to connect to the server. Please check if the backend is running.');
        alert('Unable to connect to the server.');
      } else {
        // Log generic error message for other errors
        console.error('An unexpected error occurred while updating chat');
        alert('An unexpected error occurred.');
      }
      // Re-throw error to be handled by caller
      throw err;
    }
  };

  // Function to handle chat deletion
  const handleChatDelete = async (chatId) => {
    try {
      // Make DELETE request to backend API to delete chat session
      await axios.delete(`http://localhost:8000/api/sessions/${chatId}`);
      // Clear current chat if it's the one being deleted
      if (currentChat && (currentChat.id === chatId || currentChat._id === chatId)) {
        setCurrentChat(null);
      }
      // Refresh chat history from database after deletion
      fetchChatHistory();
      // Log successful deletion
      console.log('Chat deleted successfully');
    } catch (err) {
      // Handle errors from API call
      if (err.response) {
        // Log error message from API response
        console.error('Error deleting chat:', err.response.data.detail || 'An error occurred');
        // Show alert to user
        alert('Failed to delete chat. Please try again.');
      } else if (err.request) {
        // Log error if request was made but no response received
        console.error('Unable to connect to the server. Please check if the backend is running.');
        alert('Unable to connect to the server.');
      } else {
        // Log generic error message for other errors
        console.error('An unexpected error occurred while deleting chat');
        alert('An unexpected error occurred.');
      }
      // Re-throw error to be handled by caller
      throw err;
    }
  };

  // Return JSX structure for the application
  return (
    // Main container div with full viewport height, flexbox layout, and dark background
    <div className="h-screen bg-black flex overflow-hidden">
      {/* Left sidebar for navigation and chat history */}
      <Sidebar
        // Pass chat history to sidebar
        chatHistory={chatHistory}
        // Pass loading state to sidebar
        loadingHistory={loadingHistory}
        // Pass new chat handler to sidebar
        onNewChat={handleNewChat}
        // Pass chat selection handler to sidebar
        onSelectChat={handleSelectChat}
        // Pass chat update handler to sidebar
        onChatUpdate={handleChatUpdate}
        // Pass chat delete handler to sidebar
        onChatDelete={handleChatDelete}
      />
      {/* Main content area with flex-grow to fill available space */}
      <div className="flex-1 flex flex-col overflow-hidden border-l border-gray-900">
        {/* Chat component area - fills entire screen */}
        <ChatComponent
          // Pass current chat data to component
          currentChat={currentChat}
          // Pass function to add chat to history
          onChatComplete={addToHistory}
        />
      </div>
    </div>
  );
}

// Export App component as default export
export default App;
