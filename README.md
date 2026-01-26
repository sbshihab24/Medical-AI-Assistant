# MediConsult Elite - AI Medical Assistant

An AI-powered medical consultation platform using Flask and OpenAI's GPT-4o with vision capabilities.

## ✨ Features

- **Text Chat** - Medical consultation with context-aware responses
- **Document Analysis** - Upload lab reports and prescriptions for AI analysis
- **Session Management** - Persistent conversation history
- **Emergency Detection** - Automatic alerts for critical symptoms
- **Responsive Design** - Works on desktop, tablet, and mobile

## 📁 Project Structure

```
Medical_AI_Assistant/
├── app.py                 # Flask backend
├── requirements.txt       # Dependencies
├── .env                   # API keys (create this)
├── templates/
│   └── index.html        # Main UI
└── static/
    ├── css/style.css
    └── js/script.js
```

## 🛠️ Tech Stack

- **Backend**: Flask, OpenAI API
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Libraries**: Marked.js, FontAwesome

## 🚀 Quick Start

1. **Clone & Setup**
   ```bash
   git clone <repository-url>
   cd Medical_AI_Assistant
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate    # Mac/Linux
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key
   ```

4. **Run**
   ```bash
   python app.py
   ```
   Visit: `http://127.0.0.1:5000`

## 📡 API Endpoints

### `POST /api/chat`
Send a message to the AI consultant.

```json
{
  "message": "I have a headache",
  "session_id": "sess_abc123_1234567890"
}
```

### `POST /api/upload`
Upload medical documents (lab reports, prescriptions).

Form data:
- `file`: Image or PDF
- `session_id`: Session ID

Both endpoints return:
```json
{
  "response": "AI analysis here..."
}
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "OpenAI API Key not found" | Add `OPENAI_API_KEY` to `.env` and restart |
| Files not uploading | Check file size and format (JPG, PNG, PDF) |
| Session lost on restart | Use in-memory storage; add database for persistence |
| CORS errors | Flask-CORS is enabled; check browser console |

## 📋 Dependencies

```
Flask==3.0.0
flask-cors==4.0.0
openai==1.35.0
python-dotenv==1.0.0
werkzeug==3.0.1
```

## ⚠️ Important Notes

- **NOT a real medical service** - Always consult licensed physicians
- **Educational purposes only** - AI provides general information
- **Emergency situations** - Call 911/999 for urgent conditions
- **In-memory storage** - Sessions lost on server restart
- **Development only** - Not suitable for production deployment

## 📝 License

For educational and personal use only.
