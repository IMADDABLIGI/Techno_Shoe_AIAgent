#!/bin/bash

# Create Techno Shoes React App Setup Script
echo "🚀 Setting up Techno Shoes React App..."

# Create the React app with Vite
npm create vite@latest shoes-frontend -- --template react
cd shoes-frontend

# Install dependencies
npm install
npm install axios lucide-react

# Remove default files
rm src/App.css src/index.css

# Create index.css with Tailwind CDN
cat > src/index.css << 'EOF'
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#root {
  min-height: 100vh;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Animation classes */
.slide-in {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.bounce-in {
  animation: bounceIn 0.6s ease-out;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
EOF

# Create main App.jsx
cat > src/App.jsx << 'EOF'
import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, ShoppingBag, Star, Heart, ShoppingCart } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const ShoeCard = ({ shoe, onAddToCart }) => {
  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300 hover:shadow-2xl bounce-in">
      <div className="relative">
        <img
          src={shoe.image_url}
          alt={shoe.name}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-4 right-4">
          <button className="bg-white/80 backdrop-blur-sm p-2 rounded-full hover:bg-white transition-colors">
            <Heart className="w-5 h-5 text-gray-600 hover:text-red-500" />
          </button>
        </div>
        {shoe.in_stock && (
          <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
            In Stock
          </div>
        )}
      </div>
      
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg text-gray-800 leading-tight">{shoe.name}</h3>
          <span className="text-2xl font-bold text-indigo-600">{shoe.price} DH</span>
        </div>
        
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
            {shoe.brand}
          </span>
          <div className="flex items-center space-x-1">
            {renderStars(shoe.rating)}
            <span className="text-sm text-gray-600 ml-1">({shoe.rating})</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <span className="text-gray-500">Category:</span>
            <p className="font-medium text-gray-800">{shoe.category}</p>
          </div>
          <div>
            <span className="text-gray-500">Color:</span>
            <p className="font-medium text-gray-800">{shoe.color}</p>
          </div>
          <div>
            <span className="text-gray-500">Gender:</span>
            <p className="font-medium text-gray-800">{shoe.gender}</p>
          </div>
          <div>
            <span className="text-gray-500">Sizes:</span>
            <p className="font-medium text-gray-800">{shoe.sizes.join(', ')}</p>
          </div>
        </div>
        
        <button
          onClick={() => onAddToCart(shoe)}
          disabled={!shoe.in_stock}
          className={`w-full py-3 px-4 rounded-xl font-semibold flex items-center justify-center space-x-2 transition-all ${
            shoe.in_stock
              ? 'bg-indigo-600 hover:bg-indigo-700 text-white transform hover:scale-105'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          <ShoppingCart className="w-5 h-5" />
          <span>{shoe.in_stock ? 'Add to Cart' : 'Out of Stock'}</span>
        </button>
      </div>
    </div>
  );
};

const ChatMessage = ({ message, isUser, shoes }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 slide-in`}>
      <div className={`flex max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser ? 'bg-indigo-600 ml-3' : 'bg-orange-500 mr-3'
        }`}>
          {isUser ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
        </div>
        
        <div className={`rounded-2xl px-6 py-4 ${
          isUser 
            ? 'bg-indigo-600 text-white' 
            : 'bg-white text-gray-800 shadow-lg'
        }`}>
          <p className="leading-relaxed whitespace-pre-wrap">{message}</p>
          
          {shoes && shoes.length > 0 && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {shoes.map((shoe, index) => (
                <ShoeCard
                  key={shoe._id || index}
                  shoe={shoe}
                  onAddToCart={(shoe) => console.log('Add to cart:', shoe)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message
    setMessages([{
      id: 1,
      message: "Hello! Welcome to Techno Shoes in Casablanca Sidi Maarouf! 👋\n\nI'm Amine, your shoe shopping assistant. How can I help you find the perfect shoes today?\n\nYou can tell me about:\n• The occasion (running, work, casual, sports)\n• Your preferred brand or style\n• Your budget range in DH\n• Your size (EU sizes from 36-47) and color preferences\n• Or just ask for recommendations!",
      isUser: false,
      shoes: null
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      message: inputMessage,
      isUser: true,
      shoes: null
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: inputMessage,
        session_id: sessionId
      });

      const assistantMessage = {
        id: Date.now() + 1,
        message: response.data.message,
        isUser: false,
        shoes: response.data.shoes_data
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        message: "Sorry, I'm having trouble connecting right now. Please try again!",
        isUser: false,
        shoes: null
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-orange-500 p-2 rounded-xl">
                <ShoppingBag className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Techno Shoes</h1>
                <p className="text-white/80 text-sm">Casablanca Sidi Maarouf</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-white font-medium">Chat with Amine</p>
              <p className="text-white/80 text-sm">Your AI Shopping Assistant</p>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        <div className="bg-white/10 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 h-full flex flex-col">
          
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg.message}
                isUser={msg.isUser}
                shoes={msg.shoes}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-6">
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white rounded-2xl px-6 py-4 shadow-lg">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-6 border-t border-white/20">
            <div className="flex space-x-4">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about shoes, brands, sizes, or anything else..."
                className="flex-1 bg-white rounded-2xl px-6 py-4 text-gray-800 placeholder-gray-500 resize-none focus:outline-none focus:ring-4 focus:ring-indigo-300 shadow-lg"
                rows="2"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className={`px-8 py-4 rounded-2xl font-semibold flex items-center space-x-2 transition-all transform ${
                  inputMessage.trim() && !isLoading
                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white hover:scale-105 shadow-lg'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <Send className="w-5 h-5" />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white/10 backdrop-blur-md border-t border-white/20 py-4">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-white/80 text-sm">
            Powered by AI • Techno Shoes © 2024 • Casablanca, Morocco
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
EOF

# Update index.html to include Tailwind CDN
cat > index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Techno Shoes - AI Shopping Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            fontFamily: {
              'inter': ['Inter', 'sans-serif'],
            },
            animation: {
              'bounce': 'bounce 1s infinite',
              'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
          }
        }
      }
    </script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

# Update main.jsx
cat > src/main.jsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# Create additional components directory
mkdir -p src/components

# Create a LoadingSpinner component
cat > src/components/LoadingSpinner.jsx << 'EOF'
import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex justify-center items-center py-8">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-indigo-200 border-solid rounded-full animate-spin"></div>
        <div className="absolute top-0 left-0 w-12 h-12 border-4 border-indigo-600 border-solid rounded-full border-t-transparent animate-spin"></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
EOF

# Create an ErrorMessage component
cat > src/components/ErrorMessage.jsx << 'EOF'
import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
      <div className="flex-1">
        <p className="text-red-800 text-sm">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center space-x-1 text-red-600 hover:text-red-800 text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
EOF

# Create a typing indicator component
cat > src/components/TypingIndicator.jsx << 'EOF'
import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start space-x-3">
        <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="bg-white rounded-2xl px-6 py-4 shadow-lg">
          <div className="flex space-x-2 items-center">
            <span className="text-gray-600 text-sm">Amine is typing</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
EOF

# Create package.json scripts section
cat > package.json << 'EOF'
{
  "name": "shoes-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.1.0",
    "eslint": "^8.53.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.4",
    "vite": "^4.5.0"
  }
}
EOF

# Create vite.config.js
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
EOF

# Create README.md
cat > README.md << 'EOF'
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
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment variables
.env
.env.local
.env.production

# Build output
build/
EOF

echo "✅ Project setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Install dependencies: npm install"
echo "2. Start development server: npm run dev"
echo "3. Setup your Flask backend with the provided server.py"
echo "4. Make sure MongoDB is running and configured"
echo ""
echo "🌟 Your Techno Shoes app will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Happy coding! 👟✨"