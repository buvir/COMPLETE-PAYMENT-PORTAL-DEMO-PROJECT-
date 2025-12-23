# COMPLETE-PAYMENT-PORTAL-DEMO-PROJECT

# 💳 Payment Portal Demo

A complete, production-ready payment gateway integration demo built with **FastAPI** (backend) and **Streamlit** (frontend). Perfect for learning full-stack web development and payment processing concepts.

## 🚀 Live Demo
- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## ✨ Features
✅ **Complete Payment Flow** - From order creation to webhook processing  
✅ **RESTful API** - FastAPI with auto-generated documentation  
✅ **Modern Dashboard** - Streamlit with real-time updates  
✅ **Database Integration** - PostgreSQL with SQLAlchemy ORM  
✅ **Webhook Handling** - Secure payment confirmation  
✅ **Docker Support** - Easy containerized deployment  
✅ **API Testing Tools** - Built-in testing interface  

## 🏗️ Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Streamlit │────▶│ FastAPI │────▶│ PostgreSQL │
│ Frontend │◀────│ Backend │◀────│ Database │
└─────────────┘ └─────────────┘ └─────────────┘
│
▼
┌─────────────┐
│ Razorpay │
│ Gateway │
└─────────────┘



## 🛠️ Installation

### Option 1: Quick Start (Without Docker)
```bash
# 1. Clone repository
git clone https://github.com/yourusername/payment-portal-demo.git
cd payment-portal-demo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start backend (Terminal 1)
cd backend
uvicorn main:app --reload

# 4. Start frontend (Terminal 2)
cd frontend
streamlit run app.py



📁 Project Structure

payment-portal-demo/
├── backend/

│   ├── main.py           # FastAPI application

│   ├── database.py       # Database models

│   └── requirements.txt  # Backend dependencies

├── frontend/

│   └── app.py           # Streamlit application

├── docker-compose.yml   # For Docker setup

├── requirements.txt     # Combined dependencies

└── README.md           # Project documentation



📖 Usage Guide
1. Make a Payment
Open http://localhost:8501

Navigate to "Make Payment"

Fill payment details

Submit and see the complete flow

2. View Transactions
Go to "Transaction History"

Filter by email/status

View analytics and charts

Download as CSV

3. Test APIs
Use "API Testing" page

Test payment creation

Simulate webhooks

Check API documentation

🔧 API Endpoints
Method	Endpoint	Description
GET	/	API information
POST	/api/v1/payments	Create payment order
GET	/api/v1/transactions	List all transactions
GET	/api/v1/transactions/{id}	Get specific transaction
POST	/api/v1/webhooks/payment	Handle payment webhooks
GET	/api/v1/health	Health check


🐳 Docker Commands
```

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose up --build backend
```


🧪 Testing

```
# Manual API testing
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "currency": "INR", "customer_email": "test@example.com"}'

# Check health
curl http://localhost:8000/api/v1/health

```
