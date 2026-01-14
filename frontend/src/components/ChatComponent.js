// Import React hooks for state management and side effects
import React, { useState, useEffect, useRef } from 'react';
// Import API service for making HTTP requests
import { createChat } from '../services/api';

// ChatComponent - Main component for medical chat interface
function ChatComponent({ currentChat, onChatComplete }) {
  // State variable for patient name input (optional field)
  const [name, setName] = useState('');
  // State variable for medical problem input (required field)
  const [problem, setProblem] = useState('');
  // State variable for additional message input (optional field)
  const [message, setMessage] = useState('');
  // State variable for AI response text
  const [response, setResponse] = useState('');
  // State variable for loading state during API call
  const [loading, setLoading] = useState(false);
  // State variable for error messages
  const [error, setError] = useState('');
  // State variable to track field-specific errors
  const [fieldErrors, setFieldErrors] = useState({ name: false, disease: false });
  // State variable to store chat messages
  const [messages, setMessages] = useState([]);

  // useEffect hook to load selected chat from history
  useEffect(() => {
    // Check if a chat is selected
    if (currentChat) {
      // Set form fields from selected chat
      setName(currentChat.patient_name || '');
      setProblem(currentChat.problem || '');
      setMessage(currentChat.additional_info || '');
      
      // Format and display chat messages
      const userMessageContent = `Name: ${currentChat.patient_name || 'Anonymous'}\nDisease: ${currentChat.problem}${currentChat.additional_info ? `\nAdditional Info: ${currentChat.additional_info}` : ''}`;
      const userMessage = { 
        type: 'user', 
        content: userMessageContent, 
        name: currentChat.patient_name || 'Anonymous', 
        additional: currentChat.additional_info 
      };
      const aiMessage = { 
        type: 'ai', 
        content: currentChat.ai_response 
      };
      // Set messages to display the selected chat
      setMessages([userMessage, aiMessage]);
    } else {
      // Clear form and messages when no chat is selected (new chat)
      setName('');
      setProblem('');
      setMessage('');
      setMessages([]);
      setResponse('');
      setError('');
      setFieldErrors({ name: false, disease: false });
      // Scroll to top to show the form
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 100);
    }
  }, [currentChat]); // Run when currentChat changes

  // Function to handle form submission and API call
  const handleSubmit = async (e) => {
    // Prevent default form submission behavior (page refresh)
    e.preventDefault();
    
    // Validate that required fields are filled
    // Reset field errors
    setFieldErrors({ name: false, disease: false });
    
    // Check if name field is empty
    if (!name.trim()) {
      // Set error message if name is missing
      setError('Please enter your name');
      // Mark name field as having error
      setFieldErrors({ name: true, disease: false });
      // Scroll to form to show error
      setTimeout(() => {
        const formElement = document.querySelector('form');
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          // Focus on name field
          const nameField = document.getElementById('name');
          if (nameField) {
            nameField.focus();
          }
        }
      }, 100);
      // Exit function early if validation fails
      return;
    }
    // Check if problem (disease) field is empty
    if (!problem.trim()) {
      // Set error message if disease is missing
      setError('Please describe your disease or medical problem');
      // Mark disease field as having error
      setFieldErrors({ name: false, disease: true });
      // Scroll to form to show error
      setTimeout(() => {
        const formElement = document.querySelector('form');
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          // Focus on disease field
          const diseaseField = document.getElementById('disease');
          if (diseaseField) {
            diseaseField.focus();
          }
        }
      }, 100);
      // Exit function early if validation fails
      return;
    }
    
    // Clear any previous error messages
    setError('');
    setFieldErrors({ name: false, disease: false });
    // Set loading state to true to show loading indicator
    setLoading(true);
    // Clear previous response
    setResponse('');
    
    try {
      // Create chat using API service
      const result = await createChat({
        name: name.trim() || 'Anonymous',
        problem: problem.trim(),
        message: message.trim() || null
      });
      
      // Set AI response from API result
      setResponse(result.ai_response);
      // Add user message and AI response to messages array
      // Format user message to show name, disease, and optional message
      const userMessageContent = `Name: ${name.trim()}\nDisease: ${problem.trim()}${message.trim() ? `\nAdditional Info: ${message.trim()}` : ''}`;
      const userMessage = { type: 'user', content: userMessageContent, name: name.trim(), additional: message };
      const aiMessage = { type: 'ai', content: result.ai_response };
      setMessages((prev) => [...prev, userMessage, aiMessage]);
      // Call onChatComplete callback to add to history (this will trigger a refresh)
      if (onChatComplete) {
        onChatComplete({
          problem: problem.trim(),
          name: name.trim() || 'Anonymous',
          ai_response: result.ai_response,
          id: result.id
        });
      }
      // Clear input fields after successful submission
      setName('');
      setProblem('');
      setMessage('');
      
    } catch (err) {
      // Handle errors from API call
      setError(err.message || 'An unexpected error occurred');
      // Log error details to console for debugging
      console.error('Error:', err);
    } finally {
      // Set loading state to false after API call completes (success or error)
      setLoading(false);
    }
  };

  // Return JSX structure for chat component
  return (
    // Main container div with full height and flexbox layout, using complete screen with dark theme
    <div className="flex flex-col h-full w-full bg-neutral-950 min-h-0">
      {/* Chat messages area - scrollable but without visible scrollbar */}
      <div className="flex-1 overflow-y-auto scrollbar-hide min-h-0 relative">
        {/* Welcome message when no messages - fixed position */}
        {messages.length === 0 && !loading && (
          // Welcome message container with fixed positioning
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            {/* Welcome text with professional design */}
            <div className="text-center px-4 max-w-2xl">
              {/* Logo/icon with gradient */}
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl ring-4 ring-blue-500/20">
                  <svg className="w-8 h-8 md:w-10 md:h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </div>
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-100 mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Pulse AI
              </h2>
              <p className="text-gray-400 text-lg md:text-xl mb-1">
                Your Professional Medical Assistant
              </p>
              <p className="text-gray-500 text-sm md:text-base mt-2">
                How can I help you today?
              </p>
            </div>
          </div>
        )}
        {/* Messages container with max-width for better readability */}
        <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">


          {/* Display all chat messages */}
          {messages.map((msg, index) => (
            // Message container with professional ChatGPT-style layout
            <div key={index} className={`group flex gap-3 md:gap-4 ${msg.type === 'user' ? 'justify-end' : 'justify-start'} mb-6`}>
              {/* Avatar/icon area - only for AI messages */}
              {msg.type === 'ai' && (
                <div className="flex-shrink-0 w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg ring-2 ring-neutral-800">
                  {/* Medical icon with better styling */}
                  <svg className="w-4 h-4 md:w-5 md:h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </div>
              )}
              {/* Message content area */}
              <div className={`flex-1 ${msg.type === 'user' ? 'flex justify-end' : ''}`}>
                <div className={`${msg.type === 'user' ? 'max-w-[85%] md:max-w-[80%]' : 'max-w-full'}`}>
                  {/* Message bubble - professional design with subtle shadow */}
                  <div className={`px-4 py-3 md:px-5 md:py-3.5 rounded-2xl shadow-lg transition-all ${
                    msg.type === 'user' 
                      ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-sm hover:shadow-blue-500/20' 
                      : 'bg-neutral-800/90 text-gray-100 rounded-bl-sm hover:bg-neutral-800 border border-neutral-700/50'
                  }`}>
                    {/* User message content */}
                    {msg.type === 'user' && (
                      // User message content container with better typography
                      <div className="text-[15px] md:text-base leading-relaxed whitespace-pre-wrap break-words">
                        {msg.content}
                      </div>
                    )}
                    {/* AI message content */}
                    {msg.type === 'ai' && (
                      // AI message content container with better typography
                      <div className="text-[15px] md:text-base leading-relaxed whitespace-pre-wrap break-words">
                        {msg.content}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              {/* Avatar/icon area - only for user messages with profile picture */}
              {msg.type === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg ring-2 ring-blue-500/30 overflow-hidden">
                  {/* User profile picture/icon */}
                  <svg className="w-4 h-4 md:w-5 md:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              )}
            </div>
          ))}

          {/* Loading indicator */}
          {loading && (
            // Loading container with professional ChatGPT-style layout
            <div className="flex gap-3 md:gap-4 justify-start mb-6">
              {/* AI avatar with gradient */}
              <div className="flex-shrink-0 w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg ring-2 ring-neutral-800">
                {/* Medical icon */}
                <svg className="w-4 h-4 md:w-5 md:h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              {/* Loading bubble with professional styling */}
              <div className="bg-neutral-800/90 text-gray-100 px-4 py-3 md:px-5 md:py-3.5 rounded-2xl rounded-bl-sm shadow-lg border border-neutral-700/50">
                {/* Loading spinner with smooth animation */}
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1.5">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input form area - fixed at bottom with three-field form */}
      <div className="border-t border-neutral-800 bg-neutral-950 flex-shrink-0">
        {/* Form element for user input */}
        <form
          onSubmit={handleSubmit}
          // Disable browser autocomplete/autofill for the form
          autoComplete="off"
          className="max-w-3xl mx-auto px-4 py-3"
        >
          {/* Error message display above form */}
          {error && (
            // Error message container with red styling
            <div className="mb-3 bg-red-950/40 border border-red-500/60 text-red-200 px-3 py-2 rounded-lg text-sm">
              {/* Error message text */}
              {error}
            </div>
          )}
          {/* Form fields container with compact spacing */}
          <div className="space-y-3">
            {/* Compact form layout - two columns on larger screens */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Name field (required) */}
              <div className="flex flex-col">
                <label htmlFor="name" className="text-xs font-medium text-gray-300 mb-1.5">
                  Name <span className="text-red-400">*</span>
                </label>
                <input
                  // Set input type to text
                  type="text"
                  // Set input id for label association
                  id="name"
                  // Set input name attribute
                  name="name"
                  // Bind input value to name state variable
                  value={name}
                  // Update name state when input changes
                  onChange={(e) => {
                    setName(e.target.value);
                    // Clear error when user starts typing
                    if (fieldErrors.name) {
                      setFieldErrors({ ...fieldErrors, name: false });
                      setError('');
                    }
                  }}
                  // Placeholder text to guide user
                  placeholder="Enter your name"
                  // Apply Tailwind classes for styling with dark theme and error state
                  className={`w-full bg-neutral-800 border rounded-lg px-3 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 transition-all text-sm ${
                    fieldErrors.name
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
                      : 'border-neutral-700 focus:border-blue-500 focus:ring-blue-500/20'
                  }`}
                  // Disable input during loading state
                  disabled={loading}
                  // Make field required for form validation
                  required
                />
              </div>

              {/* Disease field (required) */}
              <div className="flex flex-col">
                <label htmlFor="disease" className="text-xs font-medium text-gray-300 mb-1.5">
                  Disease <span className="text-red-400">*</span>
                </label>
                <input
                  // Set input type to text
                  type="text"
                  // Set input id for label association
                  id="disease"
                  // Set input name attribute
                  name="disease"
                  // Bind input value to problem state variable
                  value={problem}
                  // Update problem state when input changes
                  onChange={(e) => {
                    setProblem(e.target.value);
                    // Clear error when user starts typing
                    if (fieldErrors.disease) {
                      setFieldErrors({ ...fieldErrors, disease: false });
                      setError('');
                    }
                  }}
                  // Placeholder text to guide user
                  placeholder="Describe your disease"
                  // Apply Tailwind classes for styling with dark theme and error state
                  className={`w-full bg-neutral-800 border rounded-lg px-3 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 transition-all text-sm ${
                    fieldErrors.disease
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
                      : 'border-neutral-700 focus:border-blue-500 focus:ring-blue-500/20'
                  }`}
                  // Disable input during loading state
                  disabled={loading}
                  // Make field required for form validation
                  required
                />
              </div>
            </div>

            {/* Message field (optional) - full width */}
            <div className="flex flex-col">
              <label htmlFor="message" className="text-xs font-medium text-gray-300 mb-1.5">
                Message <span className="text-gray-500 text-xs">(Optional)</span>
              </label>
              <textarea
                // Set input id for label association
                id="message"
                // Set input name attribute
                name="message"
                // Bind input value to message state variable
                value={message}
                // Update message state when input changes
                onChange={(e) => setMessage(e.target.value)}
                // Placeholder text to guide user
                placeholder="Any additional information or questions..."
                // Apply Tailwind classes for styling with dark theme
                className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm leading-5 resize-none min-h-[60px] max-h-[120px] overflow-y-auto scrollbar-hide"
                // Disable input during loading state
                disabled={loading}
                rows={3}
              />
            </div>

            {/* Submit button */}
            <div className="flex justify-end pt-1">
              <button
                // Set button type to submit to trigger form submission
                type="submit"
                // Disable button during loading state or if required fields are empty
                disabled={loading || !name.trim() || !problem.trim()}
                // Apply Tailwind classes for styling with conditional disabled state
                className={`px-5 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
                  // Use blue gradient background when enabled, gray when disabled
                  loading || !name.trim() || !problem.trim()
                    ? 'bg-neutral-700 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-blue-500/50'
                }`}
              >
                {loading ? (
                  // Loading state with spinner
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white"></div>
                    <span>Processing...</span>
                  </div>
                ) : (
                  // Normal state with send text
                  'Submit'
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

// Export ChatComponent as default export
export default ChatComponent;
