// Import React library for building UI components
import React from 'react';

// Header component for top navigation bar
function Header() {
  // Return JSX structure for header
  return (
    // Header container with light background and strong bottom border
    <header className="bg-white border-b border-gray-900 h-16 flex items-center px-4 flex-shrink-0 shadow-sm">
      {/* Header content aligned with sidebar (visual spacer on left) */}
      <div className="w-64 flex-shrink-0"></div>
      <div className="flex-1 h-full flex items-center justify-end text-xs text-gray-600 pr-4">
        {/* Reserved for future status or actions */}
      </div>
    </header>
  );
}

// Export Header component as default export
export default Header;
