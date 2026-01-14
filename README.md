# Pulse-AI - Professional Diseases Analysis Assistant

A production-ready medical chatbot application that allows users to input their medical data, receive AI-powered diagnoses and recommendations, and store all interactions in a MongoDB database.

## 📸 Screenshots

<div align="center">

### Welcome Screen
![Welcome Screen](docs/images/Welcom_Screen.png)
*Clean, professional welcome interface with intuitive form layout*

### Chat Interface  
![Chat Interface](docs/images/Chat_Interface.png)
*Interactive chat experience with AI-powered medical analysis and chat history management*

</div>

## Features

- **Professional Medical AI**: Doctor-like responses with concise, clinical guidance
- **Patient Data Collection**: Captures name, problem, and optional additional information
- **AI-Powered Diagnosis**: Uses Groq LLaMA 3.3 70B to analyze symptoms and provide recommendations
- **Chat History Management**: View, rename, pin, and delete previous chat sessions
- **Data Persistence**: All chat sessions are stored in MongoDB with timestamps
- **Modern UI**: Clean, responsive React frontend with Tailwind CSS (dark theme)
- **Professional Modals**: Custom delete confirmation dialogs (no browser popups)
- **Legal Compliance**: Includes medical disclaimers in all responses

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework for building REST APIs
- **MongoDB**: NoSQL database with Motor for asynchronous operations
- **Pydantic**: Data validation and serialization
- **Groq API**: LLaMA 3.3 70B Versatile model for medical analysis

### Frontend
- **React.js**: UI library for building interactive interfaces
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Axios**: HTTP client for API communication

## Project Structure

```
Pulse_AI/
├── backend/
│   ├── app/                      # Application package
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app instance and configuration
│   │   ├── api/                 # API routes
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # All API endpoints
│   │   ├── models/              # Data models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic models for validation
│   │   ├── core/                # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Application configuration
│   │   │   └── database.py      # MongoDB connection
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   └── ai_service.py   # AI/Groq integration
│   │   └── utils/               # Utility functions
│   │       ├── __init__.py
│   │       └── text_processing.py  # Text cleaning utilities
│   ├── main.py                  # Entry point (imports app.main)
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Virtual environment (not in git)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatComponent.js  # Main chat interface
│   │   │   └── Sidebar.js        # Navigation and chat history
│   │   ├── services/
│   │   │   └── api.js            # API service layer
│   │   ├── utils/                # Utility functions
│   │   ├── App.js                # Root React component
│   │   ├── index.js              # React entry point
│   │   └── index.css              # Global styles with Tailwind
│   ├── public/
│   │   └── index.html            # HTML template
│   ├── package.json              # Node.js dependencies
│   ├── tailwind.config.js        # Tailwind configuration
│   └── postcss.config.js         # PostCSS configuration
├── docs/
│   └── images/                   # Screenshots and assets
│       ├── Welcom_Screen.png
│       └── Chat_Interface.png
└── README.md                     # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB (local installation or MongoDB Atlas account)
- Groq API key ([Get one here](https://console.groq.com/keys))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd Server_Side
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the backend directory:**
   ```env
   MONGO_URI=mongodb://localhost:27017
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Start MongoDB (if running locally):**
   ```bash
   # Windows (if installed as service, it should start automatically)
   # Or use MongoDB Compass

   # macOS (using Homebrew)
   brew services start mongodb-community

   # Linux
   sudo systemctl start mongod
   ```

6. **Run the FastAPI server:**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   uvicorn main:app --reload --port 8000
   ```
   
   **Important:** The `uvicorn` command must be run from the `backend` directory where `main.py` is located.

   The API will be available at `http://localhost:8000`
   API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Client_Side
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## API Endpoints

### POST `/api/chat`
Submit patient information and receive AI medical response.

**Request Body:**
```json
{
  "name": "John Doe",
  "problem": "I have a persistent headache for 3 days",
  "message": "The pain is worse in the morning"
}
```

**Response:**
```json
{
  "patient_name": "John Doe",
  "problem": "I have a persistent headache for 3 days",
  "additional_info": "The pain is worse in the morning",
  "ai_response": "Based on your symptoms...",
  "timestamp": "2024-01-15T10:30:00",
  "id": "507f1f77bcf86cd799439011"
}
```

### GET `/api/sessions`
Retrieve all chat sessions from the database.

**Response:**
```json
[
  {
    "patient_name": "John Doe",
    "problem": "...",
    "ai_response": "...",
    "timestamp": "...",
    "id": "..."
  }
]
```

### GET `/api/sessions/{session_id}`
Retrieve a specific chat session by ID.

### PATCH `/api/sessions/{session_id}`
Update a chat session (rename or pin/unpin).

**Request Body:**
```json
{
  "problem": "New chat name"  // Optional: for renaming
  // OR
  "pinned": true  // Optional: for pinning/unpinning
}
```

### DELETE `/api/sessions/{session_id}`
Delete a chat session from the database.

## Usage

1. **Start both backend and frontend servers** (see setup instructions above)

2. **Open your browser** and navigate to `http://localhost:3000`

3. **Fill in the form:**
   - Enter your name (required)
   - Describe your medical problem (required)
   - Add any additional information (optional)

4. **Click "Submit"** to receive AI-powered analysis

5. **View the response** which includes:
   - Concise clinical assessment
   - Likely diagnosis
   - Specific recommendations (rest, home remedies, medications)
   - Warning signs to watch for
   - Legal medical disclaimer

6. **Manage your chat history:**
   - Click "New chat" to start a fresh conversation
   - Click any chat in the sidebar to view previous conversations
   - Use the three-dot menu on any chat to:
     - **Rename**: Change the chat title
     - **Pin**: Keep important chats at the top
     - **Delete**: Remove unwanted chats (with professional confirmation modal)

## Important Notes

### Medical Disclaimer
⚠️ **This application is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.**

### AI Behavior
- Pulse AI is configured to **only answer health-related questions**
- It will refuse to answer questions about politics, coding, sports, or other non-medical topics
- Responses are **concise and doctor-like** - direct, clinical, and professional (under 200 words)
- All responses include appropriate medical disclaimers

### Data Storage
- All chat sessions are stored in MongoDB
- Each session includes patient name, problem, additional info, AI response, timestamp, and pin status
- Chat history persists across application restarts
- Sessions can be renamed, pinned, or deleted
- Pinned chats appear at the top of the chat history list

## Troubleshooting

### Backend Issues

**MongoDB Connection Error:**
- Ensure MongoDB is running: `mongosh` or check MongoDB Compass
- Verify `MONGO_URI` in `.env` file is correct
- For MongoDB Atlas, use connection string format: `mongodb+srv://username:password@cluster.mongodb.net/`

**Groq API Error:**
- Verify `GROQ_API_KEY` is set correctly in `.env`
- Check your Groq account has sufficient credits/quota
- Ensure API key has proper permissions
- Verify the model name is correct (`llama-3.3-70b-versatile`)

**Port Already in Use:**
- Change port in uvicorn command: `uvicorn main:app --reload --port 8001`
- Update frontend API URL in `ChatComponent.js` accordingly

### Frontend Issues

**CORS Errors:**
- Ensure backend CORS middleware includes your frontend URL
- Check `allow_origins` in `main.py` includes `http://localhost:3000`

**API Connection Failed:**
- Verify backend server is running on port 8000
- Check browser console for detailed error messages
- Ensure no firewall is blocking the connection

**Tailwind Styles Not Loading:**
- Run `npm install` to ensure all dependencies are installed
- Check `tailwind.config.js` content paths are correct
- Restart the React development server

## Development

### Running in Production

**Backend:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
npm run build
# Serve the build folder using a static file server
```

### Environment Variables

Create a `.env` file in the `backend` directory with:
- `MONGO_URI`: MongoDB connection string
- `GROQ_API_KEY`: Your Groq API key

## License

This project is for educational purposes. Please ensure compliance with medical regulations in your jurisdiction before deploying for production use.

## Support

For issues or questions, please check:
- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- MongoDB Documentation: https://docs.mongodb.com/
- OpenAI API Documentation: https://platform.openai.com/docs/
