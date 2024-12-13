# 🔍 Conversation Analytics Dashboard

A Streamlit-based dashboard for analyzing conversation data stored in MongoDB. This application provides an intuitive interface to explore conversation details, context entries, and message history with both raw data and formatted views.

## Features

- **Dual View Interface**:
  - Raw Data View: Displays conversation data in a three-column layout
    - Conversation Details
    - Context Entries
    - Message History
  - Formatted View: Provides a beautifully styled conversation interface with:
    - User and Assistant messages clearly distinguished
    - Timestamps in human-readable format
    - Markdown support in messages
    - Expandable context entries

- **Data Handling**:
  - HTML escaping for secure content display
  - Markdown preservation in formatted messages
  - Proper handling of code blocks and inline code
  - Unix timestamp conversion to readable dates

- **User Interface**:
  - Clean, modern design with proper spacing
  - Responsive layout
  - Clear visual hierarchy
  - Emoji support for better readability
  - Mobile-friendly design

## Prerequisites

- Python 3.8+
- MongoDB database with conversation data
- MongoDB connection URI

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AiAssistantConversationDashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the `MONGO_URI` in `.env` with your MongoDB connection string

## Usage

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

4. Enter a conversation ID in the input field and click "Load" to view the conversation data

## Environment Variables

- `MONGO_URI`: MongoDB connection string (required)
  - Format: `mongodb+srv://<username>:<password>@<cluster-url>/<database>?retryWrites=true&w=majority`

## Dependencies

- streamlit==1.29.0: Web application framework
- pymongo==4.6.1: MongoDB driver for Python
- python-dotenv==1.0.0: Environment variable management
- dnspython==2.7.0: DNS support for MongoDB connection

## Project Structure

```
AiAssistantConversationDashboard/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env.example       # Example environment variables
├── .gitignore        # Git ignore rules
└── Docs/             # Documentation files
    ├── context.md
    ├── conversationDetail.md
    └── messageHistory.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.