"""
Payment Portal Frontend
Streamlit interface for payment processing
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Payment Portal",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 2rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
    }
    .info-box {
        background-color: #DBEAFE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .payment-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = "http://localhost:8000"  # Change to your backend URL

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'last_order_id' not in st.session_state:
    st.session_state.last_order_id = None

# Helper functions
def call_backend(endpoint, method="GET", data=None):
    """Helper to call backend API"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def simulate_webhook(order_id, status="success"):
    """Simulate sending a webhook (for demo purposes)"""
    webhook_data = {
        "event": "payment.captured",
        "order_id": order_id,
        "payment_id": f"pay_{int(time.time())}",
        "amount": 100.0,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/webhooks/payment",
            json=webhook_data,
            timeout=5
        )
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        st.error(f"Cannot connect to backend: {str(e)}")

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">💳 Payment Portal Demo</h1>', unsafe_allow_html=True)
    st.markdown("A complete payment gateway integration demonstration")
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to:",
            ["Make Payment", "Transaction History", "API Testing", "Architecture"]
        )
        
        st.markdown("---")
        st.subheader("API Status")
        
        # Health check
        health_data = call_backend("/api/v1/health")
        if health_data:
            st.success(f"✅ Backend: {health_data['status']}")
            st.info(f"Transactions: {health_data['transactions_count']}")
        else:
            st.error("❌ Backend unavailable")
        
        st.markdown("---")
        st.caption("Built with FastAPI + Streamlit")
        st.caption("For demonstration purposes only")
    
    # Page routing
    if page == "Make Payment":
        show_payment_page()
    elif page == "Transaction History":
        show_transactions_page()
    elif page == "API Testing":
        show_api_testing_page()
    elif page == "Architecture":
        show_architecture_page()

def show_payment_page():
    """Display payment form and processing"""
    st.markdown('<h2 class="sub-header">💸 Make a Payment</h2>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("payment_form"):
                st.markdown('<div class="payment-card">', unsafe_allow_html=True)
                
                # Payment form
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=10.0,
                    max_value=100000.0,
                    value=100.0,
                    step=10.0
                )
                
                customer_name = st.text_input("Full Name", "John Doe")
                customer_email = st.text_input("Email", "john.doe@example.com")
                description = st.text_area("Description", "Payment for services")
                currency = st.selectbox("Currency", ["INR", "USD", "EUR"], index=0)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit_button = st.form_submit_button("Process Payment", use_container_width=True)
                with col_b:
                    clear_button = st.form_submit_button("Clear Form", use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if submit_button:
                    # Create payment payload
                    payment_data = {
                        "amount": amount,
                        "currency": currency,
                        "customer_name": customer_name,
                        "customer_email": customer_email,
                        "description": description
                    }
                    
                    # Show processing spinner
                    with st.spinner("Processing payment..."):
                        # Call backend API
                        result = call_backend("/api/v1/payments", "POST", payment_data)
                        
                        if result and result.get("success"):
                            st.session_state.last_order_id = result["order_id"]
                            
                            # Display success message
                            st.markdown(f"""
                            <div class="success-box">
                                <h3>✅ Payment Initiated Successfully!</h3>
                                <p><strong>Order ID:</strong> {result['order_id']}</p>
                                <p><strong>Amount:</strong> ₹{result['amount']} {result['currency']}</p>
                                <p><strong>Message:</strong> {result['message']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show redirect information
                            if result.get("redirect_url"):
                                st.markdown(f"""
                                <div class="info-box">
                                    <h4>Next Steps:</h4>
                                    <p>User would be redirected to payment gateway:</p>
                                    <code>{result['redirect_url']}</code>
                                    <p><small><em>In a real application, this would open Razorpay/Stripe checkout</em></small></p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Simulate webhook after delay
                            st.info("Simulating payment completion...")
                            time.sleep(2)
                            if simulate_webhook(result["order_id"]):
                                st.success("✅ Payment completed! Webhook received and processed.")
                        
                        else:
                            st.error("Payment failed. Please try again.")
                
                if clear_button:
                    st.experimental_rerun()
        
        with col2:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.subheader("How It Works")
            st.markdown("""
            1. **Fill** payment details
            2. **Submit** to FastAPI backend
            3. **Backend creates** payment order
            4. **Redirect** to payment gateway
            5. **Gateway processes** payment
            6. **Webhook notifies** backend
            7. **Backend updates** database
            8. **Show confirmation** to user
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            if st.session_state.last_order_id:
                st.subheader("Last Payment")
                st.code(f"Order ID: {st.session_state.last_order_id}")
                
                if st.button("Simulate Failed Payment"):
                    if simulate_webhook(st.session_state.last_order_id, "failed"):
                        st.error("Simulated payment failure")

def show_transactions_page():
    """Display transaction history"""
    st.markdown('<h2 class="sub-header">📊 Transaction History</h2>', unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_email = st.text_input("Filter by Email")
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All", "pending", "success", "failed"])
    with col3:
        refresh_btn = st.button("Refresh Data", type="secondary")
    
    # Fetch transactions
    endpoint = "/api/v1/transactions"
    if filter_email:
        endpoint += f"?email={filter_email}"
        if filter_status != "All":
            endpoint += f"&status={filter_status}"
    elif filter_status != "All":
        endpoint += f"?status={filter_status}"
    
    transactions_data = call_backend(endpoint)
    
    if transactions_data and transactions_data.get("transactions"):
        df = pd.DataFrame(transactions_data["transactions"])
        
        # Format datetime columns
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        if 'updated_at' in df.columns:
            df['updated_at'] = pd.to_datetime(df['updated_at'])
            df['updated_at'] = df['updated_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Display metrics
        total_amount = df['amount'].sum()
        success_count = len(df[df['status'] == 'success'])
        pending_count = len(df[df['status'] == 'pending'])
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Total Transactions", len(df))
        with metric_col2:
            st.metric("Total Amount", f"₹{total_amount:,.2f}")
        with metric_col3:
            st.metric("Success Rate", f"{(success_count/len(df)*100):.1f}%" if len(df) > 0 else "0%")
        
        # Display dataframe
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        # Charts
        st.subheader("Visualization")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            status_counts = df['status'].value_counts()
            if not status_counts.empty:
                st.bar_chart(status_counts)
        
        with chart_col2:
            if 'created_at' in df.columns and len(df) > 1:
                timeline_df = df.groupby(pd.to_datetime(df['created_at']).dt.date).size()
                st.line_chart(timeline_df)
    else:
        st.info("No transactions found. Make a payment first!")

def show_api_testing_page():
    """API testing interface"""
    st.markdown('<h2 class="sub-header">🔧 API Testing</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Create Payment", "Webhook Simulator", "API Documentation"])
    
    with tab1:
        st.subheader("Test Payment API")
        
        test_data = {
            "amount": 150.0,
            "currency": "INR",
            "customer_name": "Test User",
            "customer_email": "test@example.com",
            "description": "API Test Payment"
        }
        
        st.json(test_data)
        
        if st.button("Test Create Payment API"):
            with st.spinner("Calling API..."):
                result = call_backend("/api/v1/payments", "POST", test_data)
                if result:
                    st.success("API Call Successful!")
                    st.json(result)
    
    with tab2:
        st.subheader("Simulate Webhook")
        
        order_id = st.text_input("Order ID to simulate", 
                                value=st.session_state.last_order_id or "ORD20240320123456ABC123")
        webhook_status = st.selectbox("Webhook Status", ["success", "failed", "pending"])
        
        webhook_payload = {
            "event": "payment.captured",
            "order_id": order_id,
            "payment_id": f"pay_{int(time.time())}",
            "amount": 100.0,
            "status": webhook_status,
            "timestamp": datetime.now().isoformat()
        }
        
        st.json(webhook_payload)
        
        if st.button("Send Test Webhook"):
            with st.spinner("Sending webhook..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/webhooks/payment",
                        json=webhook_payload,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Webhook sent successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"❌ Failed: {response.status_code}")
                        st.text(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("API Endpoints")
        
        endpoints = [
            {"method": "GET", "endpoint": "/", "description": "API root"},
            {"method": "POST", "endpoint": "/api/v1/payments", "description": "Create payment"},
            {"method": "GET", "endpoint": "/api/v1/transactions", "description": "List transactions"},
            {"method": "GET", "endpoint": "/api/v1/transactions/{order_id}", "description": "Get transaction"},
            {"method": "POST", "endpoint": "/api/v1/webhooks/payment", "description": "Receive webhooks"},
            {"method": "GET", "endpoint": "/api/v1/health", "description": "Health check"},
        ]
        
        for ep in endpoints:
            st.code(f"{ep['method']} {ep['endpoint']} - {ep['description']}")
        
        st.markdown("---")
        st.info("📚 Full API documentation available at: http://localhost:8000/docs")

def show_architecture_page():
    """Display system architecture"""
    st.markdown('<h2 class="sub-header">🏗️ System Architecture</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📊 Architecture Diagram
    
    ```mermaid
    graph TB
        A[User Browser] --> B[Streamlit Frontend]
        B --> C[FastAPI Backend]
        C --> D[PostgreSQL Database]
        C --> E[Razorpay/Stripe Gateway]
        E --> F[Banking Network]
        E --> C[Webhook Callback]
        C --> G[Transaction Updates]
        G --> B[User Feedback]
    ```
    
    ### 🔄 Payment Flow Sequence
    
    1. **Frontend (Streamlit)**
       - User fills payment form
       - Validates input data
       - Sends request to backend
    
    2. **Backend (FastAPI)**
       - Receives payment request
       - Validates and processes data
       - Creates transaction record
       - Calls payment gateway API
    
    3. **Payment Gateway (Razorpay/Stripe)**
       - Processes payment securely
       - Handles card/bank transactions
       - Returns payment status
    
    4. **Webhook Processing**
       - Gateway sends async notification
       - Backend verifies signature
       - Updates transaction status
    
    5. **Database (PostgreSQL)**
       - Stores all transaction data
       - Maintains audit logs
       - Supports reporting
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Tech Stack")
        st.markdown("""
        - **Frontend:** Streamlit, HTML/CSS
        - **Backend:** FastAPI, Python
        - **Database:** PostgreSQL, SQLAlchemy
        - **Payment:** Razorpay/Stripe SDK
        - **Deployment:** Docker, AWS/Render
        - **Monitoring:** Logging, Health checks
        """)
    
    with col2:
        st.subheader("🔐 Security Features")
        st.markdown("""
        - HTTPS/TLS encryption
        - JWT authentication
        - Webhook signature verification
        - Input validation & sanitization
        - Environment variables for secrets
        - Rate limiting on APIs
        - SQL injection prevention
        """)
    
    st.markdown("---")
    st.info("💡 This is a production-ready architecture pattern that can be scaled for real-world applications.")

if __name__ == "__main__":
    main()