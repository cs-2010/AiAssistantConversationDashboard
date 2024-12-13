# 🔍 Conversation Analytics Dashboard

A Streamlit-based dashboard for analyzing conversation data stored in MongoDB. This application provides an intuitive interface to explore conversation details, context entries, and message history.

## Features

- **Raw Data View**: Displays conversation data in a three-column layout
  - Conversation Details
  - Context Entries
  - Message History
- **Formatted View**: (Coming soon) Will provide a more readable format of the conversation data

## Prerequisites

- Python 3.8+
- MongoDB database with conversation data
- MongoDB connection URI

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the `MONGO_URI` in `.env` with your MongoDB connection string

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Enter a conversation ID in the input field and click "Load" to view the conversation data.

## Environment Variables

- `MONGO_URI`: MongoDB connection string (required)

## Dependencies

- streamlit==1.29.0
- pymongo==4.6.1
- python-dotenv==1.0.0
- dnspython==2.7.0