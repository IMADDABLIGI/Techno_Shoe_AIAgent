# 👟 Techno Shoes - AI Shopping Assistant

A modern React frontend for the Techno Shoes AI shopping assistant powered by Flask backend.

## Features

- 🤖 AI-powered shoe recommendations
- 💬 Interactive chat interface
- 🛍️ Beautiful product cards with images
- 📱 Responsive design
- ⚡ Real-time chat experience
- 🎨 Modern UI with Tailwind CSS

## Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+ (for backend)
- MongoDB connection

### Setup Instructions

1. **Clone and setup the frontend:**
   ```bash
   npm install
   npm run dev
   ```

2. **Setup the backend:**
   - Save the Flask server code as `server.py`
   - Install Python dependencies:
     ```bash
     pip install flask flask-cors python-dotenv openai pymongo requests
     ```
   - Create `.env` file with your environment variables:
     ```
     GITHUB_TOKEN=your_github_token
     CONNECTION_STRING=your_mongodb_connection_string
     DB_NAME=your_database_name
     ```
   - Run the Flask server:
     ```bash
     python server.py
     ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Project Structure

```
shoes-frontend/
├── src/
│   ├── components/
│   │   ├── LoadingSpinner.jsx
│   │   ├── ErrorMessage.jsx
│   │   └── TypingIndicator.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## API Endpoints

- `POST /api/chat` - Send chat messages
- `GET /api/health` - Health check

## Technologies Used

- **Frontend:** React, Vite, Tailwind CSS, Axios, Lucide React
- **Backend:** Flask, OpenAI API, MongoDB
- **Styling:** Tailwind CSS with custom animations
- **Icons:** Lucide React

## Environment Variables

Create a `.env` file in your backend directory:

```env
GITHUB_TOKEN=your_github_token_here
CONNECTION_STRING=mongodb://your_connection_string
DB_NAME=your_database_name
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
