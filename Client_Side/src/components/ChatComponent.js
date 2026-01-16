// Import React hooks for state management and side effects
import React, { useState, useEffect, useRef } from 'react';
// Import API service for making HTTP requests
import { createChat } from '../services/api';

// ChatComponent - Main component for medical chat interface
function ChatComponent({ currentChat, onChatComplete }) {
  // State variable for patient name input (required field)
  const [name, setName] = useState('');
  // State variable for medical problem input (optional field)
  const [problem, setProblem] = useState('');
  // State variable for additional message input (required field)
  const [message, setMessage] = useState('');
  // State variable for loading state during API call
  const [loading, setLoading] = useState(false);
  // State variable for error messages
  const [error, setError] = useState('');
  // State variable to track field-specific errors
  const [fieldErrors, setFieldErrors] = useState({ name: false, message: false });
  // State variable to store chat messages
  const [messages, setMessages] = useState([]);
  // State variable to track if initial submission has been made (hides Name/Disease fields)
  const [hasInitialSubmission, setHasInitialSubmission] = useState(false);
  // State variable to store initial patient info (read-only after first submission)
  const [initialPatientInfo, setInitialPatientInfo] = useState({ name: '', problem: '' });
  // State variable to track current session ID for continuing conversations
  const [currentSessionId, setCurrentSessionId] = useState(null);
  // Ref to the messages container for scrolling
  const messagesContainerRef = useRef(null);
  // Ref to the form container for scrolling
  const formRef = useRef(null);

  // useEffect hook to load selected chat from history
  useEffect(() => {
    // Check if a chat is selected
    if (currentChat) {
      // Store patient info but don't set form fields (for Q&A, message field should be empty)
      setName(currentChat.patient_name || '');
      setProblem(currentChat.problem || '');
      // Clear message field so user can type follow-up questions
      setMessage('');
      
      // Store initial patient info and mark as having initial submission (hide Name/Disease fields)
      setInitialPatientInfo({
        name: currentChat.patient_name || 'Anonymous',
        problem: currentChat.problem || 'No specific disease mentioned'
      });
      // Mark that this is an existing chat (initial submission already done)
      setHasInitialSubmission(true);
      // Store session ID for continuing conversations
      setCurrentSessionId(currentChat.id || currentChat._id || null);
      
      // Load full conversation history from messages array if available
      if (currentChat.messages && Array.isArray(currentChat.messages) && currentChat.messages.length > 0) {
        // Convert messages array to display format
        const formattedMessages = currentChat.messages.map((msg) => {
          // Extract content from formatted user messages
          let displayContent = msg.content;
          if (msg.role === 'user') {
            // Extract just the message part from formatted strings like "Patient Name: X\nMessage: Y"
            const messageMatch = displayContent.match(/Message:\s*(.+)/s);
            if (messageMatch) {
              displayContent = messageMatch[1].trim();
            } else {
              // If no "Message:" pattern, try to extract after last newline
              const lines = displayContent.split('\n');
              const lastLine = lines[lines.length - 1];
              if (lastLine && !lastLine.includes('Patient Name:') && !lastLine.includes('Problem:')) {
                displayContent = lastLine.trim();
              }
            }
          }
          
          return {
            type: msg.role === 'user' ? 'user' : 'ai',
            content: displayContent,
            name: msg.role === 'user' ? (currentChat.patient_name || 'Anonymous') : undefined
          };
        });
        setMessages(formattedMessages);
      } else {
        // Fallback to old format if messages array is not available
        const userMessageContent = currentChat.additional_info || '';
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
        setMessages([userMessage, aiMessage]);
      }
      // Scroll messages container to bottom to show latest messages
      setTimeout(() => {
        if (messagesContainerRef.current) {
          messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
      }, 100);
    } else {
      // Clear form and messages when no chat is selected (new chat)
      setName('');
      setProblem('');
      setMessage('');
      setMessages([]);
      setError('');
      setFieldErrors({ name: false, message: false });
      setLoading(false);
      // Reset initial submission state to show Name/Disease fields again
      setHasInitialSubmission(false);
      // Clear initial patient info
      setInitialPatientInfo({ name: '', problem: '' });
      // Clear session ID for new chat
      setCurrentSessionId(null);
      // Scroll messages container to top to show the welcome message
      // Use requestAnimationFrame to ensure DOM is updated before scrolling
      requestAnimationFrame(() => {
        setTimeout(() => {
          if (messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = 0;
          }
        }, 0);
      });
    }
  }, [currentChat]); // Run when currentChat changes

  // Function to handle form submission and API call
  const handleSubmit = async (e) => {
    // Prevent default form submission behavior (page refresh)
    e.preventDefault();
    
    // Validate that required fields are filled
    // Reset field errors
    setFieldErrors({ name: false, message: false });
    
    // Only validate name if this is the initial submission (Name/Disease fields are visible)
    if (!hasInitialSubmission) {
      // Check if name field is empty (only for initial submission)
      if (!name.trim()) {
        // Set error message if name is missing
        setError('Please enter your name');
        // Mark name field as having error
        setFieldErrors({ name: true, message: false });
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
    }
    
    // Check if message field is empty (always required)
    if (!message.trim()) {
      // Set error message if message is missing
      setError(hasInitialSubmission ? 'Please enter your question or message' : 'Please describe your medical issue or symptoms');
      // Mark message field as having error
      setFieldErrors({ name: false, message: true });
      // Scroll to form to show error
      setTimeout(() => {
        const formElement = document.querySelector('form');
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          // Focus on message field
          const messageField = document.getElementById('message');
          if (messageField) {
            messageField.focus();
          }
        }
      }, 100);
      // Exit function early if validation fails
      return;
    }
    
    // Clear any previous error messages
    setError('');
    setFieldErrors({ name: false, message: false });
    // Set loading state to true to show loading indicator
    setLoading(true);
    
    try {
      // Create chat using API service
      // Use stored initial patient info if this is a follow-up message
      const patientName = hasInitialSubmission ? initialPatientInfo.name : (name.trim() || 'Anonymous');
      const patientProblem = hasInitialSubmission ? (initialPatientInfo.problem !== 'No specific disease mentioned' ? initialPatientInfo.problem : null) : (problem.trim() || null);
      
      // Prepare chat data with session_id if continuing an existing conversation
      const chatData = {
        name: patientName,
        problem: patientProblem,
        message: message.trim()
      };
      
      // Add session_id if continuing an existing conversation
      if (hasInitialSubmission && currentSessionId) {
        chatData.session_id = currentSessionId;
      }
      
      // Check if this is the first submission (initial chat setup)
      const isFirstSubmission = !hasInitialSubmission;
      
      // Add user message to messages array immediately
      // For display, show only the message content (not the formatted version sent to API)
      const userMessageContent = message.trim();
      const userMessage = { 
        type: 'user', 
        content: userMessageContent, 
        name: hasInitialSubmission ? initialPatientInfo.name : (name.trim() || 'Anonymous')
      };
      
      // Add user message to messages
      setMessages((prev) => [...prev, userMessage]);
      
      // Call non-streaming API to get AI response
      const response = await createChat(chatData);
      
      // Extract AI response and session ID from response
      const aiResponse = response.ai_response || '';
      const sessionId = response.id || response._id || null;
      
      // Add AI message to messages
      setMessages((prev) => [...prev, { type: 'ai', content: aiResponse }]);
      
      // If this is the first submission, store initial patient info and hide Name/Disease fields
      if (isFirstSubmission) {
        // Store initial patient info (read-only after this)
        setInitialPatientInfo({
          name: name.trim() || 'Anonymous',
          problem: problem.trim() || 'No specific disease mentioned'
        });
        // Mark that initial submission has been made
        setHasInitialSubmission(true);
        // Store session ID for future messages
        setCurrentSessionId(sessionId);
      } else {
        // Update session ID if it changed (shouldn't happen, but just in case)
        if (sessionId && sessionId !== currentSessionId) {
          setCurrentSessionId(sessionId);
        }
      }
      
      // Scroll to bottom to show latest messages
      setTimeout(() => {
        if (messagesContainerRef.current) {
          messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
      }, 100);
      
      // Call onChatComplete callback to add to history (this will trigger a refresh)
      if (onChatComplete) {
        onChatComplete({
          problem: problem.trim() || message.trim().substring(0, 50),
          name: name.trim() || 'Anonymous',
          ai_response: aiResponse,
          id: sessionId
        });
      }
      
      // Clear message field after submission (but keep name/problem if first submission)
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
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto scrollbar-hide min-h-0 relative">
        {/* Professional Patient Information Header - compact clinical style */}
        {hasInitialSubmission && initialPatientInfo.name && (
          // Patient header container - fixed at top of messages area
          <div className="sticky top-0 z-10 bg-neutral-950/95 backdrop-blur-sm border-b border-neutral-800/50">
            {/* Compact patient info bar with clinical styling */}
            <div className="max-w-3xl mx-auto px-4 py-2.5">
              <div className="flex items-center justify-between gap-4">
                {/* Left side - patient details in compact format */}
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  {/* Patient icon/badge */}
                  <div className="flex-shrink-0 w-7 h-7 rounded-md bg-gradient-to-br from-blue-600/20 to-blue-700/20 border border-blue-500/30 flex items-center justify-center">
                    <svg className="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  {/* Patient information - compact horizontal layout */}
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {/* Patient name */}
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Patient:</span>
                      <span className="text-xs font-medium text-gray-200 truncate">{initialPatientInfo.name}</span>
                    </div>
                    {/* Divider */}
                    {initialPatientInfo.problem && initialPatientInfo.problem !== 'No specific disease mentioned' && (
                      <>
                        <span className="text-gray-600">•</span>
                        {/* Disease/Problem */}
                        <div className="flex items-center gap-1.5 min-w-0">
                          <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Condition:</span>
                          <span className="text-xs text-gray-300 truncate">{initialPatientInfo.problem}</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
                {/* Right side - session indicator (optional) */}
                <div className="flex-shrink-0">
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-green-500/10 border border-green-500/20">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></div>
                    <span className="text-[10px] font-medium text-green-400 uppercase tracking-wide">Active</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
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
        <div className={`max-w-3xl mx-auto px-4 space-y-6 ${hasInitialSubmission ? 'pt-4' : 'pt-8'} pb-8`}>


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
                      <div>
                        {/* Main AI response content */}
                        <div className="text-[15px] md:text-base leading-relaxed whitespace-pre-wrap break-words">
                          {msg.content}
                        </div>
                        {/* Professional medical disclaimer - compact and professional */}
                        <div className="mt-4 pt-3 border-t border-neutral-700/50">
                          <div className="flex items-center gap-2.5">
                            {/* Medical shield icon - compact */}
                            <div className="flex-shrink-0 w-4 h-4 rounded bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
                              <svg className="w-2.5 h-2.5 text-amber-400/90" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                              </svg>
                            </div>
                            {/* Compact disclaimer text - single line style */}
                            <p className="text-[10px] md:text-[11px] text-gray-400 leading-snug">
                              <span className="font-semibold text-amber-400/90 uppercase tracking-wide mr-1.5">Medical Disclaimer:</span>
                              <span className="text-gray-300/80"><span className="font-medium text-gray-200">Pulse-AI</span> provides informational content only and does not replace professional medical advice. Seek a qualified doctor for any medical concerns or emergency situations.</span>
                            </p>
                          </div>
                        </div>
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

      {/* Input form area - fixed at bottom with dynamic form */}
      <div ref={formRef} className="border-t border-neutral-800 bg-neutral-950 flex-shrink-0">
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
            {/* Name and Disease fields - only shown when starting new chat */}
            {!hasInitialSubmission && (
              // Container with smooth fade-in animation
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 animate-in fade-in duration-300">
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

                {/* Disease field (optional) */}
                <div className="flex flex-col">
                  <label htmlFor="disease" className="text-xs font-medium text-gray-300 mb-1.5">
                    Disease <span className="text-gray-500 text-xs">(Optional)</span>
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
                    onChange={(e) => setProblem(e.target.value)}
                    // Placeholder text to guide user
                    placeholder="Describe your disease (optional)"
                    // Apply Tailwind classes for styling with dark theme
                    className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm"
                    // Disable input during loading state
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            {/* Message field (required) - always visible */}
            <div className="flex flex-col">
              <label htmlFor="message" className="text-xs font-medium text-gray-300 mb-1.5">
                {hasInitialSubmission ? 'Continue the conversation' : 'Message'} <span className="text-red-400">*</span>
              </label>
              <textarea
                // Set input id for label association
                id="message"
                // Set input name attribute
                name="message"
                // Bind input value to message state variable
                value={message}
                // Update message state when input changes
                onChange={(e) => {
                  setMessage(e.target.value);
                  // Clear error when user starts typing
                  if (fieldErrors.message) {
                    setFieldErrors({ ...fieldErrors, message: false });
                    setError('');
                  }
                }}
                // Placeholder text to guide user - changes based on submission state
                placeholder={hasInitialSubmission ? "Ask your follow-up question or describe additional symptoms..." : "Describe your medical issue or symptoms..."}
                // Apply Tailwind classes for styling with dark theme and error state
                className={`w-full bg-neutral-800 border rounded-lg px-3 py-2 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 transition-all text-sm leading-5 resize-none min-h-[60px] max-h-[120px] overflow-y-auto scrollbar-hide ${
                  fieldErrors.message
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20'
                    : 'border-neutral-700 focus:border-blue-500 focus:ring-blue-500/20'
                }`}
                // Disable input during loading state
                disabled={loading}
                // Make field required for form validation
                required
                rows={3}
              />
            </div>

            {/* Submit button */}
            <div className="flex justify-end pt-1">
              <button
                // Set button type to submit to trigger form submission
                type="submit"
                // Disable button during loading state or if required fields are empty
                // After initial submission, only check message; before, check both name and message
                disabled={loading || (hasInitialSubmission ? !message.trim() : (!name.trim() || !message.trim()))}
                // Apply Tailwind classes for styling with conditional disabled state
                className={`px-5 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
                  // Use blue gradient background when enabled, gray when disabled
                  loading || (hasInitialSubmission ? !message.trim() : (!name.trim() || !message.trim()))
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
                  // Normal state - change text based on submission state
                  hasInitialSubmission ? 'Send' : 'Start Consultation'
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
