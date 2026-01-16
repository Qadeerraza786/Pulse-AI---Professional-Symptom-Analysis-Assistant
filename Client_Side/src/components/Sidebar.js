// Import React library for building UI components
import React, { useState, useRef, useEffect } from 'react';
// Import axios library for making HTTP requests to backend API
import axios from 'axios';

// Sidebar component for navigation and chat history
function Sidebar({ chatHistory, loadingHistory, onNewChat, onSelectChat, onChatUpdate, onChatDelete }) {
  // State variable to track if sidebar is collapsed on mobile
  const [isOpen, setIsOpen] = useState(true);
  // State variable to track which chat's menu is open
  const [openMenuId, setOpenMenuId] = useState(null);
  // State variable to track which chat is being renamed
  const [renamingChatId, setRenamingChatId] = useState(null);
  // State variable to store the new name for renaming
  const [newChatName, setNewChatName] = useState('');
  // State variable to track which chat is being deleted (null if none)
  const [deletingChat, setDeletingChat] = useState(null);
  // State variable to track if delete is in progress
  const [isDeleting, setIsDeleting] = useState(false);
  // Ref to detect clicks outside the menu
  const menuRef = useRef(null);

  // Function to handle three-dot menu click
  const handleMenuClick = (e, chatId) => {
    // Prevent event bubbling to parent button
    e.stopPropagation();
    // Toggle menu open/close
    setOpenMenuId(openMenuId === chatId ? null : chatId);
  };

  // Function to handle rename
  const handleRename = async (e, chat) => {
    // Prevent event bubbling
    e.stopPropagation();
    // Set the chat being renamed and initialize with current problem
    setRenamingChatId(chat.id || chat._id);
    setNewChatName(chat.problem || 'Untitled Chat');
    // Close the menu
    setOpenMenuId(null);
  };

  // Function to save rename
  const handleSaveRename = async (e, chatId) => {
    // Prevent event bubbling
    e.stopPropagation();
    // Check if new name is provided
    if (newChatName.trim()) {
      try {
        // Call onChatUpdate callback to update the chat
        if (onChatUpdate) {
          await onChatUpdate(chatId, { problem: newChatName.trim() });
        }
        // Reset renaming state on success
        setRenamingChatId(null);
        setNewChatName('');
      } catch (err) {
        // Log error if rename fails
        console.error('Error renaming chat:', err);
        // Keep renaming state active so user can try again
      }
    } else {
      // If name is empty, cancel rename
      setRenamingChatId(null);
      setNewChatName('');
    }
  };

  // Function to cancel rename
  const handleCancelRename = (e) => {
    // Prevent event bubbling
    e.stopPropagation();
    // Reset renaming state
    setRenamingChatId(null);
    setNewChatName('');
  };

  // Function to handle pin/unpin
  const handlePin = async (e, chat) => {
    // Prevent event bubbling
    e.stopPropagation();
    // Close the menu first
    setOpenMenuId(null);
    try {
      // Call onChatUpdate callback to toggle pin status
      if (onChatUpdate) {
        await onChatUpdate(chat.id || chat._id, { pinned: !chat.pinned });
      }
    } catch (err) {
      // Log error if pin fails
      console.error('Error pinning chat:', err);
      // Error handling is done in App.js, no need for alert here
    }
  };

  // Function to handle delete click (opens confirmation modal)
  const handleDelete = (e, chat) => {
    // Prevent event bubbling
    e.stopPropagation();
    // Close the menu first
    setOpenMenuId(null);
    // Set the chat to be deleted (opens modal)
    setDeletingChat(chat);
  };

  // Function to confirm and execute delete
  const handleConfirmDelete = async () => {
    // Check if there's a chat to delete
    if (!deletingChat) return;
    
    // Set deleting state to show loading
    setIsDeleting(true);
    try {
      // Call onChatDelete callback to delete the chat
      if (onChatDelete) {
        await onChatDelete(deletingChat.id || deletingChat._id);
      }
      // Close modal after successful deletion
      setDeletingChat(null);
    } catch (err) {
      // Log error if delete fails
      console.error('Error deleting chat:', err);
      // Note: Error handling is done in App.js, so we just close the modal
      setDeletingChat(null);
    } finally {
      // Reset deleting state
      setIsDeleting(false);
    }
  };

  // Function to cancel delete
  const handleCancelDelete = () => {
    // Close modal without deleting
    setDeletingChat(null);
    setIsDeleting(false);
  };

  // Effect to close menu when clicking outside
  useEffect(() => {
    // Function to handle click outside
    const handleClickOutside = (event) => {
      // Check if click is outside the menu
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        // Close the menu
        setOpenMenuId(null);
      }
      // Check if click is outside the rename input (cancel rename)
      if (renamingChatId && !event.target.closest('.relative.group')) {
        // Cancel rename if clicking outside
        setRenamingChatId(null);
        setNewChatName('');
      }
    };
    // Add event listener if menu is open or renaming
    if (openMenuId || renamingChatId) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    // Cleanup event listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [openMenuId, renamingChatId]);

  // Effect to handle Escape key for closing delete modal
  useEffect(() => {
    // Function to handle Escape key press
    const handleEscape = (event) => {
      // Check if Escape key is pressed and modal is open
      if (event.key === 'Escape' && deletingChat) {
        // Cancel delete and close modal
        setDeletingChat(null);
        setIsDeleting(false);
      }
    };
    // Add event listener if delete modal is open
    if (deletingChat) {
      document.addEventListener('keydown', handleEscape);
    }
    // Cleanup event listener
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [deletingChat]);

  // Return JSX structure for sidebar
  return (
    // Sidebar container with dark background, fixed width, and full height
    <div className={`bg-neutral-900 border-r border-neutral-800 text-gray-100 h-screen flex flex-col transition-all duration-300 ${isOpen ? 'w-64' : 'w-0'} overflow-hidden`}>
      {/* Top section with logo, app name, and optional menu toggle */}
      <div className="h-16 border-b border-neutral-800 flex items-center px-4 flex-shrink-0">
        {/* Logo and text container */}
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          {/* Logo mark with medical gradient */}
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 items-center justify-center shadow-md flex flex-shrink-0">
            <span className="text-white text-lg font-semibold">⚕️</span>
          </div>
          {/* App name and subtitle */}
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-semibold tracking-wide text-gray-100 leading-tight">
              Pulse AI
            </span>
            <span className="text-xs text-gray-400 leading-tight">
              Professional medical assistant
            </span>
          </div>
        </div>
        {/* Menu toggle button for mobile */}
        <button
          // Toggle sidebar visibility on mobile
          onClick={() => setIsOpen(!isOpen)}
          // Apply Tailwind classes for styling
          className="md:hidden text-gray-400 hover:text-gray-100 ml-2 flex-shrink-0"
        >
          {/* Hamburger menu icon */}
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Navigation links section */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-hide">
        {/* New Chat button */}
        <button
          // Handle new chat creation
          onClick={(e) => {
            // Prevent any event bubbling
            e.preventDefault();
            e.stopPropagation();
            // Call onNewChat handler if provided
            if (onNewChat) {
              // Call handler to reset chat
              onNewChat();
            } else {
              // Log warning if handler is not provided
              console.warn('onNewChat handler is not provided');
            }
          }}
          // Apply Tailwind classes for styling with hover effects, light gray border, and centered content
          className="w-full flex items-center justify-center space-x-3 px-3 py-2 mb-2 rounded-lg border border-neutral-700 hover:bg-neutral-800 text-gray-100 hover:text-white transition-colors cursor-pointer active:bg-neutral-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          // Ensure button is accessible
          type="button"
          aria-label="Start a new chat"
        >
          {/* Pencil icon for new chat */}
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          {/* New chat text */}
          <span className="text-sm font-medium">New chat</span>
        </button>

        {/* Chat history section */}
        <div className="mt-6">
          {/* Section heading */}
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-3">
            Your chats
          </h3>
          {/* Chat history list */}
          <div className="space-y-1">
            {/* Show loading state while fetching chat history */}
            {loadingHistory ? (
              // Loading indicator
              <div className="flex items-center justify-center px-3 py-4">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
                <span className="text-xs text-gray-500 ml-2">Loading...</span>
              </div>
            ) : chatHistory && chatHistory.length > 0 ? (
              // Render chat history items
              chatHistory.map((chat) => {
                const chatId = chat.id || chat._id;
                const isRenaming = renamingChatId === chatId;
                const isMenuOpen = openMenuId === chatId;
                
                return (
                  // Chat item container with relative positioning for menu
                  <div key={chatId} className="relative group">
                    {/* Individual chat item button */}
                    <div className="flex items-center gap-2 w-full px-3 py-2 rounded-lg hover:bg-neutral-800 border border-gray-600 hover:border-gray-500 transition-colors">
                      {/* Chat content area */}
                      {isRenaming ? (
                        // Rename input field
                        <div className="flex-1 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                          <input
                            // Bind input value to new chat name
                            value={newChatName}
                            // Update new chat name when input changes
                            onChange={(e) => setNewChatName(e.target.value)}
                            // Handle Enter key to save, Escape to cancel
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault();
                                handleSaveRename(e, chatId);
                              } else if (e.key === 'Escape') {
                                e.preventDefault();
                                handleCancelRename(e);
                              }
                            }}
                            // Auto-focus on input
                            autoFocus
                            // Apply Tailwind classes for styling
                            className="flex-1 bg-neutral-800 border border-blue-500 rounded px-2 py-1 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                            // Stop propagation to prevent chat selection
                            onClick={(e) => e.stopPropagation()}
                          />
                          {/* Save button */}
                          <button
                            // Handle save rename
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSaveRename(e, chatId);
                            }}
                            // Apply Tailwind classes for styling
                            className="p-1 text-blue-400 hover:text-blue-300"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </button>
                          {/* Cancel button */}
                          <button
                            // Handle cancel rename
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCancelRename(e);
                            }}
                            // Apply Tailwind classes for styling
                            className="p-1 text-gray-400 hover:text-gray-300"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      ) : (
                        // Chat title button
                        <button
                          // Handle chat selection
                          onClick={() => onSelectChat(chat)}
                          // Apply Tailwind classes for styling
                          className="flex-1 text-left text-gray-200 hover:text-white transition-colors text-sm truncate"
                        >
                          {/* Display pinned indicator if chat is pinned */}
                          {chat.pinned && (
                            <span className="inline-block mr-2 text-blue-400">📌</span>
                          )}
                          {/* Display chat title or problem description */}
                          {chat.problem || 'Untitled Chat'}
                        </button>
                      )}
                      
                      {/* Three-dot menu button on the right */}
                      <button
                        // Handle menu click
                        onClick={(e) => handleMenuClick(e, chatId)}
                        // Apply Tailwind classes for styling
                        className="flex-shrink-0 p-1 rounded hover:bg-neutral-700 text-gray-400 hover:text-gray-200 transition-colors"
                        // Prevent chat selection when clicking menu
                        onMouseDown={(e) => e.stopPropagation()}
                      >
                        {/* Three-dot icon */}
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </button>
                    </div>
                    
                    {/* Dropdown menu */}
                    {isMenuOpen && (
                      // Menu container with absolute positioning (aligned to right)
                      <div 
                        ref={menuRef}
                        className="absolute right-0 top-full mt-1 w-48 bg-neutral-800 border border-neutral-700 rounded-lg shadow-xl z-50"
                        // Stop propagation to prevent closing
                        onClick={(e) => e.stopPropagation()}
                      >
                        {/* Menu items */}
                        <div className="py-1">
                          {/* Rename option */}
                          <button
                            // Handle rename click
                            onClick={(e) => handleRename(e, chat)}
                            // Apply Tailwind classes for styling with hover effects
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-200 hover:bg-neutral-700 hover:text-white transition-colors cursor-pointer"
                            // Prevent event bubbling
                            onMouseDown={(e) => e.stopPropagation()}
                          >
                            {/* Pencil icon */}
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            {/* Rename text */}
                            <span>Rename</span>
                          </button>
                          
                          {/* Pin option */}
                          <button
                            // Handle pin click
                            onClick={(e) => handlePin(e, chat)}
                            // Apply Tailwind classes for styling with hover effects
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-200 hover:bg-neutral-700 hover:text-white transition-colors cursor-pointer"
                            // Prevent event bubbling
                            onMouseDown={(e) => e.stopPropagation()}
                          >
                            {/* Pin icon */}
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                            </svg>
                            {/* Pin text */}
                            <span>{chat.pinned ? 'Unpin' : 'Pin'}</span>
                          </button>
                          
                          {/* Delete option */}
                          <button
                            // Handle delete click
                            onClick={(e) => handleDelete(e, chat)}
                            // Apply Tailwind classes for styling with red text and hover effects
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-400 hover:bg-neutral-700 hover:text-red-300 transition-colors cursor-pointer"
                            // Prevent event bubbling
                            onMouseDown={(e) => e.stopPropagation()}
                          >
                            {/* Trash icon */}
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            {/* Delete text */}
                            <span>Delete</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              // Empty state message when no chat history
              <p className="text-xs text-gray-500 px-3 py-2">No chat history</p>
            )}
          </div>
        </div>
      </div>

      {/* User profile section at bottom */}
      <div className="p-4 border-t border-neutral-800">
        {/* User profile container */}
        <div className="flex items-center space-x-3">
          {/* User avatar circle */}
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
            {/* User initials (placeholder) */}
            UR
          </div>
          {/* User name and status */}
          <div className="flex-1 min-w-0">
            {/* User name text */}
            <p className="text-sm font-medium text-gray-100 truncate">User</p>
            {/* User status text */}
            <p className="text-xs text-gray-400">Free</p>
          </div>
        </div>
      </div>

      {/* Custom Delete Confirmation Modal */}
      {deletingChat && (
        // Modal backdrop (overlay)
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={handleCancelDelete}
        >
          {/* Modal content container */}
          <div 
            className="bg-neutral-800 border border-neutral-700 rounded-xl shadow-2xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="mb-4">
              {/* Warning icon */}
              <div className="w-12 h-12 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              {/* Modal title */}
              <h3 className="text-lg font-semibold text-gray-100 text-center mb-2">
                Delete Chat?
              </h3>
              {/* Modal message */}
              <p className="text-sm text-gray-400 text-center">
                Are you sure you want to delete <span className="text-gray-200 font-medium">"{deletingChat.problem || 'Untitled Chat'}"</span>? This action cannot be undone.
              </p>
            </div>

            {/* Modal actions */}
            <div className="flex gap-3">
              {/* Cancel button */}
              <button
                onClick={handleCancelDelete}
                disabled={isDeleting}
                className="flex-1 px-4 py-2.5 bg-neutral-700 hover:bg-neutral-600 text-gray-100 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              {/* Delete button */}
              <button
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                className="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isDeleting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <span>Delete</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Export Sidebar component as default export
export default Sidebar;
