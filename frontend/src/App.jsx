import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, ShoppingBag, Star, Heart, ShoppingCart } from 'lucide-react';
import axios from 'axios';

// const API_URL = 'http://localhost:5000/api';
const API_URL = import.meta.env.VITE_API_URL;

const ShoeCard = ({ shoe, onAddToCart }) => {
  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-3 h-3 sm:w-4 sm:h-4 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg overflow-hidden transform hover:scale-105 transition-all duration-300 hover:shadow-2xl bounce-in h-full flex flex-col">
      <div className="relative">
        <img
          src={shoe.image}
          alt={shoe.name}
          className="w-full h-36 sm:h-48 object-cover"
        />
        <div className="absolute top-2 right-2 sm:top-4 sm:right-4">
          <button className="bg-white/80 backdrop-blur-sm p-1.5 sm:p-2 rounded-full hover:bg-white transition-colors">
            <Heart className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 hover:text-red-500" />
          </button>
        </div>
        {shoe.in_stock && (
          <div className="absolute top-2 left-2 sm:top-4 sm:left-4 bg-green-500 text-white px-2 py-1 sm:px-3 sm:py-1 rounded-full text-xs sm:text-sm font-medium">
            In Stock
          </div>
        )}
      </div>
      
      <div className="p-3 sm:p-6 flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-sm sm:text-lg text-gray-800 leading-tight pr-2">{shoe.name}</h3>
          <span className="text-lg sm:text-2xl font-bold text-indigo-600 whitespace-nowrap">{shoe.price} DH</span>
        </div>
        
        <div className="flex items-center justify-between mb-2 sm:mb-3">
          <span className="text-xs sm:text-sm font-medium text-gray-600 bg-gray-100 px-2 py-1 sm:px-3 sm:py-1 rounded-full">
            {shoe.brand}
          </span>
          <div className="flex items-center space-x-1">
            {renderStars(shoe.rating)}
            <span className="text-xs sm:text-sm text-gray-600 ml-1">({shoe.rating})</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2 sm:gap-4 mb-3 sm:mb-4 text-xs sm:text-sm flex-grow">
          <div>
            <span className="text-gray-500">Category:</span>
            <p className="font-medium text-gray-800 text-xs sm:text-sm">{shoe.category}</p>
          </div>
          <div>
            <span className="text-gray-500">Color:</span>
            <p className="font-medium text-gray-800 text-xs sm:text-sm">{shoe.color}</p>
          </div>
          <div>
            <span className="text-gray-500">Gender:</span>
            <p className="font-medium text-gray-800 text-xs sm:text-sm">{shoe.gender}</p>
          </div>
          <div>
            <span className="text-gray-500">Sizes:</span>
            <p className="font-medium text-xs text-gray-800">{shoe.sizes.join(', ')}</p>
          </div>
        </div>
        
        <button
          onClick={() => onAddToCart(shoe)}
          disabled={!shoe.in_stock}
          className={`w-full py-2 sm:py-3 px-3 sm:px-4 rounded-lg sm:rounded-xl font-semibold flex items-center justify-center space-x-2 transition-all mt-auto text-sm sm:text-base ${
            shoe.in_stock
              ? 'bg-indigo-600 hover:bg-indigo-700 text-white transform hover:scale-105 active:scale-95'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          <ShoppingCart className="w-4 h-4 sm:w-5 sm:h-5" />
          <span>{shoe.in_stock ? 'Add to Cart' : 'Out of Stock'}</span>
        </button>
      </div>
    </div>
  );
};

const ChatMessage = ({ message, isUser, shoes }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 sm:mb-6 slide-in`}>
      <div className={`flex max-w-full sm:max-w-4xl ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-2 sm:space-x-3`}>
        <div className={`flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center ${
          isUser ? 'bg-indigo-600 ml-2 sm:ml-3' : 'bg-orange-500 mr-2 sm:mr-3'
        }`}>
          {isUser ? <User className="w-4 h-4 sm:w-5 sm:h-5 text-white" /> : <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-white" />}
        </div>
        
        <div className={`rounded-xl sm:rounded-2xl px-3 py-3 sm:px-6 sm:py-4 max-w-[85%] sm:max-w-none ${
          isUser 
            ? 'bg-indigo-600 text-white' 
            : 'bg-white text-gray-800 shadow-lg'
        }`}>
          <p className="leading-relaxed whitespace-pre-wrap text-xs sm:text-base">{message}</p>
          
          {shoes && shoes.length > 0 && (
            <div className="mt-4 sm:mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
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

  // Sending a message to the backend
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
      const response = await axios.post(`${API_URL}`, {
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

  const textareaRef = useRef(null);

  useEffect(() => {
    if (!isLoading) {
      textareaRef.current?.focus();
    }
  }, [isLoading]);

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-indigo-500 via-purple-500 to-orange-400">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="bg-orange-500 p-1.5 sm:p-2 rounded-lg sm:rounded-xl">
                <ShoppingBag className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-white">Techno Shoes</h1>
                <p className="text-white/80 text-xs sm:text-sm">Casablanca Sidi Maarouf</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-white font-medium text-xs sm:text-base">Chat with Amine</p>
              <p className="text-white/80 text-[10px] sm:text-sm">AI Shopping Assistant</p>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 max-w-6xl mx-auto w-full px-2 sm:px-4 py-3 sm:py-6">
        <div className="bg-white/10 backdrop-blur-md rounded-2xl sm:rounded-3xl shadow-2xl border border-white/20 h-full flex flex-col">
          
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg.message}
                isUser={msg.isUser}
                shoes={msg.shoes}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4 sm:mb-6">
                <div className="flex items-start space-x-2 sm:space-x-3">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-orange-500 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                  </div>
                  <div className="bg-white rounded-xl sm:rounded-2xl px-4 py-3 sm:px-6 sm:py-4 shadow-lg">
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
          <div className="p-3 sm:p-6 border-t border-white/20">
            <div className="flex space-x-2 sm:space-x-4">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about shoes..."
                className="flex-1 bg-white rounded-xl sm:rounded-2xl px-3 py-2 sm:px-6 sm:py-4 text-gray-800 placeholder-gray-500 resize-none focus:outline-none focus:ring-2 sm:focus:ring-4 focus:ring-indigo-300 shadow-lg text-xs sm:text-base"
                rows="1"
                disabled={isLoading}
                ref={textareaRef}
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className={`px-3 py-2 sm:px-8 sm:py-4 rounded-xl sm:rounded-2xl font-semibold flex items-center space-x-1 sm:space-x-2 transition-all transform text-xs sm:text-base ${
                  inputMessage.trim() && !isLoading
                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white hover:scale-105 active:scale-95 shadow-lg'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <Send className="w-4 h-4 sm:w-5 sm:h-5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white/10 backdrop-blur-md border-t border-white/20 py-3 sm:py-4">
        <div className="max-w-6xl mx-auto px-3 sm:px-4 text-center">
          <p className="text-white/80 text-xs sm:text-sm">
            Techno Shoes © 2024 • Casablanca, Morocco
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;