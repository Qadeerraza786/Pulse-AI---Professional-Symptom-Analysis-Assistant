// Import React library for building UI components
import React, { useState, useEffect } from 'react';
// Import API service for making HTTP requests
import { fetchChatHistory, updateChatSession, deleteChatSession } from './services/api';
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
  const loadChatHistory = async () => {
    try {
      // Set loading state to true
      setLoadingHistory(true);
      // Fetch chat history using API service
      const data = await fetchChatHistory();
      // Update chat history state with data from API
      setChatHistory(data);
      // Log successful fetch
      console.log('Chat history loaded from database');
    } catch (err) {
      // Handle errors from API call
      console.error('Error fetching chat history:', err.message);
      // Set empty array on error to prevent UI issues
      setChatHistory([]);
    } finally {
      // Set loading state to false after API call completes
      setLoadingHistory(false);
    }
  };

  // useEffect hook to fetch chat history when component mounts
  useEffect(() => {
    // Call loadChatHistory function on component mount
    loadChatHistory();
  }, []); // Empty dependency array means this runs only once on mount

  // Function to add chat to history (called from ChatComponent)
  const addToHistory = (chatData) => {
    // Refresh chat history from database after adding new chat
    loadChatHistory();
  };

  // Function to handle chat update (rename, pin, etc.)
  const handleChatUpdate = async (chatId, updates) => {
    try {
      // Update chat session using API service
      await updateChatSession(chatId, updates);
      // Refresh chat history from database after update
      loadChatHistory();
      // Log successful update
      console.log('Chat updated successfully');
    } catch (err) {
      // Handle errors from API call
      console.error('Error updating chat:', err.message);
      // Show alert to user
      alert('Failed to update chat. Please try again.');
      // Re-throw error to be handled by caller
      throw err;
    }
  };

  // Function to handle chat deletion
  const handleChatDelete = async (chatId) => {
    try {
      // Delete chat session using API service
      await deleteChatSession(chatId);
      // Clear current chat if it's the one being deleted
      if (currentChat && (currentChat.id === chatId || currentChat._id === chatId)) {
        setCurrentChat(null);
      }
      // Refresh chat history from database after deletion
      loadChatHistory();
      // Log successful deletion
      console.log('Chat deleted successfully');
    } catch (err) {
      // Handle errors from API call
      console.error('Error deleting chat:', err.message);
      // Show alert to user
      alert('Failed to delete chat. Please try again.');
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
