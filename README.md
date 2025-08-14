# PULSE: Personalized Updates & Learning System for (Health) Experts

**PULSE** is an AI-powered agent that delivers timely, personalized news and updates tailored for healthcare professionals.  
Built with **Python** and **Streamlit**, it offers a seamless interface, smart filtering, and topic tracking to help users stay current on research, trends, and breaking health news.

---

## 🚀 Features

- **Personalized Content Delivery** – Curated news and learning suggestions based on your specialties and preferences.
- **AI Agent Architecture** – News Agent delivers up-to-date news related to your field, and Chat Agent answers any questions related to your field
- **Interactive Web App** – Built in Streamlit for intuitive display and chat function
---

## 🛠️ Setup Instructions

### 1. Clone the repository
    git clone https://github.com/jamesignac/PULSE.git
    cd PULSE 
### 2. Set up environment
    python3 -m venv venv
    source venv/bin/activate      
    venv\Scripts\activate
### 3. Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
### 4. Required environment variables
    TAVILY_API_KEY="your-tavily-api-key"
    DATABASE_URL="your-sqlite-url"
    SECRET_KEY="your_secret_key"
    GOOGLE_API_KEY="your-google-api-key"
### 5. Run the application
    streamlit run app.py
