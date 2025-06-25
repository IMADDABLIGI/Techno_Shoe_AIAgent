# 🤖👟 Techno_Shoe_AIAgent

An intelligent e-commerce platform that revolutionizes online shoe shopping through AI-powered conversations. This full-stack application combines modern web technologies with artificial intelligence to create personalized shopping experiences while automatically capturing qualified leads for business growth.

## 🎯 Project Overview

Techno_Shoe_AIAgent is a cutting-edge shoe store that leverages AI technology to understand customer needs through natural conversations. The AI agent helps customers discover the perfect shoes while intelligently collecting their contact information for sales team follow-up, creating a seamless bridge between customer service and lead generation.

## ✨ Key Features

### 🤖 Intelligent AI Shopping Assistant
- Natural language processing for customer inquiries
- Context-aware product recommendations
- Multi-turn conversation handling
- Personalized shopping experience

### 👟 Smart Product Discovery
- AI-powered shoe search and filtering
- Budget-based recommendations
- Style and preference matching
- Real-time inventory integration

### 📊 Automated Lead Generation
- Intelligent customer information capture
- Interest-based lead qualification
- Conversation history tracking
- Sales team integration

### 💬 Real-Time Chat Interface
- Instant AI responses
- Mobile-responsive design
- Seamless user experience
- Modern chat UI/UX

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern component-based UI
- **Vite** - Lightning-fast development and build tool
- **JavaScript/JSX** - Interactive user interface
- **CSS3** - Responsive and modern styling

### Backend
- **Python 3.8+** - Server-side logic and AI integration
- **Flask** - Lightweight web framework
- **AI Integration** - Intelligent conversation handling
- **RESTful API** - Clean data communication

### Database
- **MongoDB** - NoSQL database for flexible data storage
- **Collections**: Shoes catalog, customer information, chat history
- **Document-based** - Perfect for varying product specifications

## 🚀 Getting Started

### Prerequisites
```bash
Node.js >= 16.0.0
Python >= 3.8
MongoDB (local or cloud)
```

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Techno_Shoe_AIAgent.git
   cd Techno_Shoe_AIAgent
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
   Backend will run on `http://localhost:5000`

4. **Database Setup**
   - Install MongoDB locally or use MongoDB Atlas
   - Create database: `techno_shoe_db`
   - Collections will be created automatically

### Environment Configuration

**Backend `.env`:**
```env
MONGODB_URI=mongodb://localhost:27017/techno_shoe_db
AI_API_KEY=your_ai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

**Frontend `.env`:**
```env
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Techno_Shoe_AIAgent
```

## 💡 How It Works

### Customer Journey Flow
1. **Landing** → Customer visits the shoe store website
2. **Engagement** → AI chatbot greets and asks about shoe preferences
3. **Discovery** → AI searches and presents matching shoes from database
4. **Interest** → Customer expresses interest in specific products
5. **Capture** → AI politely collects customer contact information
6. **Storage** → Customer data and preferences saved to MongoDB
7. **Follow-up** → Sales team receives qualified leads for conversion

### Sample AI Conversation
```
🤖 AI: "Welcome to Techno Shoes! I'm here to help you find the perfect shoes. What type of shoes are you looking for today?"

👤 Customer: "I need comfortable running shoes for daily jogging, budget around $120"

🤖 AI: "Perfect! I found 3 excellent running shoes within your budget that are highly rated for comfort and daily use..."

👤 Customer: "The Nike Air Zoom looks great! Can you tell me more?"

🤖 AI: "Excellent choice! The Nike Air Zoom is perfect for daily runners. To send you detailed specifications and check availability in your size, could I get your name and phone number?"
```

## 🏗️ Project Architecture

```
Techno_Shoe_AIAgent/
├── 📁 frontend/                    # React + Vite Application
│   ├── 📁 src/
│   │   ├── 📁 components/         # Reusable React components
│   │   │   ├── Chat/             # Chat interface components
│   │   │   ├── ProductCard/      # Product display components
│   │   │   └── Layout/           # Layout components
│   │   ├── 📁 pages/             # Main page components
│   │   ├── 📁 hooks/             # Custom React hooks
│   │   ├── 📁 utils/             # Utility functions
│   │   └── 📁 styles/            # CSS stylesheets
│   └── package.json
├── 📁 backend/                     # Python Flask API
│   ├── 📁 models/                # Database models
│   │   ├── shoe_model.py        # Shoe product model
│   │   └── customer_model.py    # Customer data model
│   ├── 📁 routes/                # API endpoints
│   │   ├── shoes.py             # Shoe-related endpoints
│   │   ├── chat.py              # AI chat endpoints
│   │   └── customers.py         # Customer management
│   ├── 📁 ai_agent/              # AI logic and processing
│   │   ├── conversation.py      # Chat conversation handling
│   │   ├── product_search.py    # AI product matching
│   │   └── lead_capture.py      # Customer info extraction
│   ├── 📁 utils/                 # Helper functions
│   ├── app.py                    # Main Flask application
│   └── requirements.txt          # Python dependencies
└── README.md
```

## 🔗 API Endpoints

### Shoes Management
- `GET /api/shoes` - Retrieve all available shoes
- `GET /api/shoes/<id>` - Get specific shoe details
- `POST /api/shoes/search` - AI-powered shoe search

### AI Chat System
- `POST /api/chat` - Send message to AI agent
- `GET /api/chat/history/<session>` - Retrieve chat history

### Customer Management
- `POST /api/customers` - Store customer information
- `GET /api/customers` - Retrieve customer leads
- `GET /api/customers/<id>` - Get specific customer data

## 🎨 Features Showcase

### AI Agent Capabilities
- ✅ Natural language understanding
- ✅ Product recommendation engine
- ✅ Budget-aware suggestions
- ✅ Size and style preferences
- ✅ Conversational lead capture
- ✅ Multi-language support potential

### Database Schema
**Shoes Collection:**
```javascript
{
  _id: ObjectId,
  name: "Nike Air Zoom Pegasus",
  brand: "Nike",
  price: 120.00,
  sizes: [7, 8, 9, 10, 11],
  colors: ["Black", "White", "Blue"],
  category: "Running",
  description: "...",
  image_url: "...",
  in_stock: true
}
```

**Customers Collection:**
```javascript
{
  _id: ObjectId,
  first_name: "John",
  last_name: "Doe",
  age: 28,
  phone: "+1234567890",
  interested_products: [ObjectId, ...],
  conversation_history: [...],
  created_at: ISODate,
  lead_status: "qualified"
}
```

## 🚀 Deployment

### Railway Deployment (Recommended)
1. **Prepare for deployment:**
   ```bash
   # Add Procfile for backend
   echo "web: python app.py" > backend/Procfile
   ```

2. **Deploy Backend:**
   - Connect your GitHub repo to Railway
   - Set environment variables in Railway dashboard
   - Deploy Python service

3. **Deploy Frontend:**
   - Build the frontend: `npm run build`
   - Deploy static files or use Railway for frontend service

4. **Configure Database:**
   - Use Railway's MongoDB plugin or MongoDB Atlas
   - Update connection string in environment variables

### Environment Variables for Production
```env
MONGODB_URI=your_production_mongodb_uri
AI_API_KEY=your_production_ai_key
FLASK_ENV=production
CORS_ORIGINS=your_frontend_domain
```

## 📊 Business Impact

### Revenue Generation
- **Lead Qualification**: AI identifies serious buyers vs. browsers
- **24/7 Availability**: Capture leads even outside business hours
- **Personalized Experience**: Higher conversion rates through AI recommendations

### Cost Efficiency
- **Reduced Staff Load**: AI handles initial customer inquiries
- **Automated Processes**: Lead capture without manual intervention
- **Scalable Solution**: Handle multiple customers simultaneously

### Customer Experience
- **Instant Responses**: No waiting time for customer service
- **Personalized Shopping**: AI understands individual preferences
- **Mobile-Friendly**: Shop from any device, anywhere

## 🔮 Future Enhancements

- 🎯 **Advanced AI Features**: Integration with GPT-4 or custom models
- 📊 **Analytics Dashboard**: Business intelligence and customer insights
- 🛒 **Shopping Cart**: Complete e-commerce functionality
- 💳 **Payment Integration**: Stripe/PayPal checkout system
- 📱 **Mobile App**: React Native companion app
- 🌐 **Multi-language**: International market support

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for AI capabilities
- MongoDB for flexible data storage
- React and Vite communities for excellent development tools
- Flask community for lightweight backend framework

## 📞 Contact & Support

**Developer**: [Your Name]
**Email**: your.email@example.com
**Project Link**: [https://github.com/IMADDABLIGI/Techno_Shoe_AIAgent](https://github.com/IMADDABLIGI/Techno_Shoe_AIAgent)
**Live Demo**: [Your deployed application URL]

---

**🚀 Built with cutting-edge technology for the future of e-commerce**

*Transforming online shoe shopping through AI innovation*