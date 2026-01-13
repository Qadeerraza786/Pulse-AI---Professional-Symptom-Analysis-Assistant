// Tailwind CSS configuration file
/** @type {import('tailwindcss').Config} */
module.exports = {
  // Specify content files where Tailwind classes are used
  content: [
    // Include all JavaScript and JSX files in src directory
    "./src/**/*.{js,jsx,ts,tsx}",
    // Include index.html in public directory
    "./public/index.html",
  ],
  // Theme configuration for customizing Tailwind defaults
  theme: {
    // Extend default theme with custom values
    extend: {
      // Custom colors for medical theme
      colors: {
        // Primary medical blue color
        'medical-blue': '#2563eb',
        // Secondary medical green color
        'medical-green': '#10b981',
        // Accent medical purple color
        'medical-purple': '#8b5cf6',
      },
    },
  },
  // Plugins for additional Tailwind functionality
  plugins: [],
}
