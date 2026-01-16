/**
 * API service for making HTTP requests to the backend.
 */
// Import axios library for making HTTP requests
import axios from 'axios';

// Set base URL for API requests (backend server address)
const API_BASE_URL = 'http://localhost:8000';

// Request timeout in milliseconds (30 seconds)
const REQUEST_TIMEOUT = 30000;

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Creates a new chat session with patient input (non-streaming).
 * @param {Object} patientInput - Patient input data
 * @param {string} patientInput.name - Patient's name
 * @param {string} patientInput.problem - Medical problem description
 * @param {string} [patientInput.message] - Additional information
 * @returns {Promise<Object>} Chat session response
 */
// Export async function to create a new chat session
export const createChat = async (patientInput) => {
  // Wrap API call in try-catch for error handling
  try {
    // Make POST request to /api/chat endpoint with patient input data
    // Use apiClient with timeout configuration
    const response = await apiClient.post('/api/chat', patientInput);
    // Return response data (chat session object)
    return response.data;
  // Catch any errors from the API call
  } catch (error) {
    // Check if error has response data (server responded with error)
    if (error.response) {
      // Throw error with server's error message or default message
      throw new Error(error.response.data.detail || 'An error occurred while processing your request');
    // Check if error is due to timeout
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // Throw error indicating timeout
      throw new Error('Request timed out. Please check your connection and try again.');
    // Check if error is due to no response (network error)
    } else if (error.request) {
      // Throw error indicating connection problem
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    // Handle any other unexpected errors
    } else {
      // Throw generic error message
      throw new Error('An unexpected error occurred');
    }
  }
};

/**
 * Fetches all chat sessions from the database.
 * @returns {Promise<Array>} Array of chat sessions
 */
// Export async function to fetch all chat sessions
export const fetchChatHistory = async () => {
  // Wrap API call in try-catch for error handling
  try {
    // Make GET request to /api/sessions endpoint
    // Use apiClient with timeout configuration
    const response = await apiClient.get('/api/sessions');
    // Return response data (array of chat sessions)
    return response.data;
  // Catch any errors from the API call
  } catch (error) {
    // Check if error has response data (server responded with error)
    if (error.response) {
      // Throw error with server's error message or default message
      throw new Error(error.response.data.detail || 'An error occurred');
    // Check if error is due to timeout
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // Throw error indicating timeout
      throw new Error('Request timed out. Please check your connection and try again.');
    // Check if error is due to no response (network error)
    } else if (error.request) {
      // Throw error indicating connection problem
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    // Handle any other unexpected errors
    } else {
      // Throw generic error message
      throw new Error('An unexpected error occurred while fetching chat history');
    }
  }
};

/**
 * Fetches a specific chat session by ID.
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Chat session data
 */
// Export async function to fetch a specific chat session by ID
export const fetchChatSession = async (sessionId) => {
  // Wrap API call in try-catch for error handling
  try {
    // Make GET request to /api/sessions/{sessionId} endpoint
    // Use apiClient with timeout configuration
    const response = await apiClient.get(`/api/sessions/${sessionId}`);
    // Return response data (chat session object)
    return response.data;
  // Catch any errors from the API call
  } catch (error) {
    // Check if error has response data (server responded with error)
    if (error.response) {
      // Throw error with server's error message or default message
      throw new Error(error.response.data.detail || 'An error occurred');
    // Check if error is due to timeout
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // Throw error indicating timeout
      throw new Error('Request timed out. Please check your connection and try again.');
    // Check if error is due to no response (network error)
    } else if (error.request) {
      // Throw error indicating connection problem
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    // Handle any other unexpected errors
    } else {
      // Throw generic error message
      throw new Error('An unexpected error occurred while fetching chat session');
    }
  }
};

/**
 * Updates a chat session (rename, pin, etc.).
 * @param {string} sessionId - Session ID
 * @param {Object} updates - Update data
 * @param {string} [updates.problem] - New problem/name
 * @param {boolean} [updates.pinned] - Pin status
 * @returns {Promise<Object>} Updated chat session
 */
// Export async function to update a chat session
export const updateChatSession = async (sessionId, updates) => {
  // Wrap API call in try-catch for error handling
  try {
    // Make PATCH request to /api/sessions/{sessionId} endpoint with update data
    // Use apiClient with timeout configuration
    const response = await apiClient.patch(`/api/sessions/${sessionId}`, updates);
    // Return response data (updated chat session object)
    return response.data;
  // Catch any errors from the API call
  } catch (error) {
    // Check if error has response data (server responded with error)
    if (error.response) {
      // Throw error with server's error message or default message
      throw new Error(error.response.data.detail || 'An error occurred');
    // Check if error is due to timeout
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // Throw error indicating timeout
      throw new Error('Request timed out. Please check your connection and try again.');
    // Check if error is due to no response (network error)
    } else if (error.request) {
      // Throw error indicating connection problem
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    // Handle any other unexpected errors
    } else {
      // Throw generic error message
      throw new Error('An unexpected error occurred while updating chat');
    }
  }
};

/**
 * Deletes a chat session.
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Deletion confirmation
 */
// Export async function to delete a chat session
export const deleteChatSession = async (sessionId) => {
  // Wrap API call in try-catch for error handling
  try {
    // Make DELETE request to /api/sessions/{sessionId} endpoint
    // Use apiClient with timeout configuration
    const response = await apiClient.delete(`/api/sessions/${sessionId}`);
    // Return response data (deletion confirmation object)
    return response.data;
  // Catch any errors from the API call
  } catch (error) {
    // Check if error has response data (server responded with error)
    if (error.response) {
      // Throw error with server's error message or default message
      throw new Error(error.response.data.detail || 'An error occurred');
    // Check if error is due to no response (network error)
    } else if (error.request) {
      // Throw error indicating connection problem
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    // Handle any other unexpected errors
    } else {
      // Throw generic error message
      throw new Error('An unexpected error occurred while deleting chat');
    }
  }
};
