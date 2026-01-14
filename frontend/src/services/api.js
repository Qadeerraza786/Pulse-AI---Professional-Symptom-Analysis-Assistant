/**
 * API service for making HTTP requests to the backend.
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

/**
 * Creates a new chat session with patient input.
 * @param {Object} patientInput - Patient input data
 * @param {string} patientInput.name - Patient's name
 * @param {string} patientInput.problem - Medical problem description
 * @param {string} [patientInput.message] - Additional information
 * @returns {Promise<Object>} Chat session response
 */
export const createChat = async (patientInput) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, patientInput);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'An error occurred while processing your request');
    } else if (error.request) {
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
};

/**
 * Fetches all chat sessions from the database.
 * @returns {Promise<Array>} Array of chat sessions
 */
export const fetchChatHistory = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/sessions`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    } else {
      throw new Error('An unexpected error occurred while fetching chat history');
    }
  }
};

/**
 * Fetches a specific chat session by ID.
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Chat session data
 */
export const fetchChatSession = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/sessions/${sessionId}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    } else {
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
export const updateChatSession = async (sessionId, updates) => {
  try {
    const response = await axios.patch(`${API_BASE_URL}/api/sessions/${sessionId}`, updates);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    } else {
      throw new Error('An unexpected error occurred while updating chat');
    }
  }
};

/**
 * Deletes a chat session.
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} Deletion confirmation
 */
export const deleteChatSession = async (sessionId) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/api/sessions/${sessionId}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      throw new Error('Unable to connect to the server. Please check if the backend is running.');
    } else {
      throw new Error('An unexpected error occurred while deleting chat');
    }
  }
};
