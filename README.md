# 🤖 WhatsApp AI Bot

A high-performance WhatsApp bot built with **FastAPI** and **Python**, integrated with **OpenAI's GPT models** to provide intelligent, automated responses. This project handles real-time messaging, background processing, and system monitoring via email alerts.

## 🚀 Features

-   **AI-Powered Conversations**: Integrates with OpenAI (GPT-3.5/4/Custom) for smart replies.
-   **WhatsApp Integration**: Uses the WhatsApp Business Cloud API for sending/receiving messages.
-   **Async Processing**: Handles message processing in the background to ensure the webhook returns a `200 OK` response instantly (prevents timeouts).
-   **User Experience**: Features "Typing..." indicators and "Read" receipts to make the bot feel more human.
-   **Error Monitoring**: Automatically emails the admin when critical errors occur (with rate limiting to prevent spam).
-   **Context Awareness**: Maintains conversation threading context (basic implementation).

## 🛠️ Tech Stack

-   **Framework**: FastAPI (high-performance, easy to learn, fast to code, ready for production)
-   **Server**: Uvicorn (ASGI server)
-   **Language**: Python 3.9+
-   **Libraries**: `openai`, `requests`, `python-dotenv`, `pydantic`

## 📋 Prerequisites

Before you begin, ensure you have:
1.  **Python 3.8+** installed.
2.  A **Meta/Facebook Developer Account** with a WhatsApp Business App set up.
3.  An **OpenAI API Key**.
4.  An **SMTP Server** (e.g., Gmail, SendGrid) for error alerts.

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Tripathiraj1/whatapp_integration
    cd whatapp_integration
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add the following keys:

    ```ini
    # OpenAI Settings
    GPT_API=your_openai_api_key_here

    # WhatsApp Business API Settings
    PHONE_NUMBER_ID=your_whatsapp_phone_number_id
    WHATSAPP_ACCESS_TOKEN=your_permanent_access_token
    VERIFY_TOKEN=your_custom_verify_token_for_webhooks

    # Email Alert Settings (SMTP)
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    EMAIL=your_email@gmail.com
    PASSWORD=your_email_app_password
    ADMIN_EMAIL=admin_email_to_notify@example.com
    ALERT_INTERVAL=3600  # Time in seconds to suppress duplicate error alerts
    ```

## 🏃‍♂️ Running the Bot

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

## 🔗 Webhook Configuration

1.  Expose your local server to the internet (for development) using a tool like **ngrok**:
    ```bash
    ngrok http 8000
    ```
2.  Go to your **Meta Developer App Dashboard** > **WhatsApp** > **Configuration**.
3.  Edit the **Webhook** configuration:
    -   **Callback URL**: `https://<your-ngrok-url>/webhook`
    -   **Verify Token**: The `VERIFY_TOKEN` you set in your `.env` file.
4.  Subscribe to **messages** webhook fields.

## 📂 Project Structure

```
├── main.py              # Main application entry point (FastAPI app)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── .gitignore           # Git ignore rules
└── config/              # (Legacy/Optional) Django configuration files
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
