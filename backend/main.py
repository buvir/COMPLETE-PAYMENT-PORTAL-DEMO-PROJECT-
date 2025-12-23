"""
Payment Portal Backend API
FastAPI backend with simulated payment processing
"""
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import hashlib
import uuid
from datetime import datetime
import json
from pydantic import BaseModel, Field, EmailStr 

# Initialize FastAPI app
app = FastAPI(
    title="Payment Portal API",
    description="Demo payment gateway integration backend",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database
transactions_db = []
webhook_logs = []

# Pydantic models
class PaymentRequest(BaseModel):
    """Payment request model"""
    amount: float = Field(gt=0, description="Payment amount in INR")
    currency: str = "INR"
    customer_name: str = Field(min_length=2, max_length=100)
    customer_email: str  # CHANGED: Using str instead of EmailStr
    description: Optional[str] = "Payment for services"

class PaymentResponse(BaseModel):
    """Payment response model"""
    success: bool
    order_id: str
    amount: float
    currency: str
    redirect_url: Optional[str] = None
    message: str

class Transaction(BaseModel):
    """Transaction model"""
    id: str
    order_id: str
    amount: float
    currency: str
    customer_email: str
    status: str
    created_at: datetime
    updated_at: datetime

# Helper functions
def generate_order_id(email: str) -> str:
    """Generate unique order ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email_hash = hashlib.sha256(email.encode()).hexdigest()[:6].upper()
    return f"ORD{timestamp}{email_hash}"

def simulate_payment_gateway_call(order_data: dict) -> dict:
    """Simulate calling a real payment gateway"""
    return {
        "id": f"pay_{uuid.uuid4().hex[:10]}",
        "status": "created",
        "redirect_url": f"https://payment-gateway-demo.com/pay/{order_data['order_id']}"
    }

def log_webhook(event_data: dict):
    """Log webhook events"""
    webhook_logs.append({
        **event_data,
        "received_at": datetime.now().isoformat()
    })
    print(f"🔔 Webhook logged: {event_data}")

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Payment Portal API",
        "version": "1.0.0",
        "endpoints": {
            "create_payment": "POST /api/v1/payments",
            "get_transactions": "GET /api/v1/transactions",
            "webhook": "POST /api/v1/webhooks/payment"
        }
    }

@app.post("/api/v1/payments", response_model=PaymentResponse)
async def create_payment(payment: PaymentRequest, background_tasks: BackgroundTasks):
    try:
        order_id = generate_order_id(payment.customer_email)
        
        gateway_response = simulate_payment_gateway_call({
            "order_id": order_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "customer_email": payment.customer_email
        })
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            order_id=order_id,
            amount=payment.amount,
            currency=payment.currency,
            customer_email=payment.customer_email,
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        transactions_db.append(transaction.dict())
        
        background_tasks.add_task(
            log_webhook,
            {"event": "payment_created", "order_id": order_id}
        )
        
        return PaymentResponse(
            success=True,
            order_id=order_id,
            amount=payment.amount,
            currency=payment.currency,
            redirect_url=gateway_response.get("redirect_url"),
            message=f"Payment order created. Order ID: {order_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

@app.get("/api/v1/transactions")
async def get_transactions(
    email: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    filtered_transactions = transactions_db
    
    if email:
        filtered_transactions = [t for t in filtered_transactions if t["customer_email"] == email]
    
    if status:
        filtered_transactions = [t for t in filtered_transactions if t["status"] == status]
    
    return {
        "count": len(filtered_transactions),
        "transactions": filtered_transactions[:limit]
    }

@app.post("/api/v1/webhooks/payment")
async def payment_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        order_id = payload.get("order_id")
        
        if not order_id:
            raise HTTPException(status_code=400, detail="Order ID not found")
        
        for transaction in transactions_db:
            if transaction["order_id"] == order_id:
                transaction["status"] = payload.get("status", "completed")
                transaction["updated_at"] = datetime.now().isoformat()
                break
        
        webhook_data = {
            "order_id": order_id,
            "event": payload.get("event", "payment_captured"),
            "status": payload.get("status"),
            "raw_payload": payload
        }
        
        background_tasks.add_task(log_webhook, webhook_data)
        
        return {
            "success": True,
            "message": "Webhook processed successfully",
            "order_id": order_id
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "transactions_count": len(transactions_db),
        "webhooks_count": len(webhook_logs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)