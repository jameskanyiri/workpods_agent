# Workpods Agent

AI workspace agent for the Workpods platform, built with LangGraph. Handles project management, task tracking, milestone coordination, and document generation through structured workflows and domain-specific skills.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) (for production)
- API keys: OpenAI, Anthropic, Tavily, LangSmith
- [ngrok](https://ngrok.com/) (for WhatsApp webhook in development)

---

## Environment Configuration

Create a `.env` file in the project root:

```dotenv
# LLM Providers
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

# LangSmith
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=workpods_agent

# LangGraph
LANGGRAPH_API_URL=http://localhost:2024

# Thread Configuration
THREAD_NAMESPACE=6ba7b810-9dad-11d1-80b4-00c04fd430c8

# WhatsApp Configuration
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

---

## Quick Start (Development)

### 1. Install dependencies

```bash
uv sync
```

### 2. Start the LangGraph dev server

```bash
langgraph dev
```

You should see:

```
        Welcome to

╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

- API: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API Docs: http://127.0.0.1:2024/docs
```

### 3. Access the agent

| Interface | URL |
|-----------|-----|
| API | http://localhost:2024 |
| LangGraph Studio | https://smith.langchain.com/studio/?baseUrl=http://localhost:2024 |
| API Docs | http://localhost:2024/docs |
| WhatsApp Webhook | http://localhost:2024/webhook |

---

## WhatsApp Integration

The agent exposes a `/webhook` endpoint for WhatsApp Cloud API integration, allowing users to interact with Workpods Agent directly via WhatsApp.

### Setup

#### 1. Start the LangGraph server

```bash
langgraph dev
```

#### 2. Expose the server with ngrok

In a separate terminal:

```bash
ngrok http --url=your-subdomain.ngrok-free.app 2024
```

This gives you a public HTTPS URL like:
```
https://your-subdomain.ngrok-free.app -> http://localhost:2024
```

#### 3. Configure Meta webhook

1. Go to the [Meta App Dashboard](https://developers.facebook.com)
2. Navigate to **WhatsApp > Configuration**
3. Set the **Webhook URL** to: `https://your-subdomain.ngrok-free.app/webhook`
4. Set the **Verify Token** to match your `WHATSAPP_VERIFY_TOKEN` in `.env`
5. Subscribe to the `messages` webhook field

#### 4. Test it

Send a message to your WhatsApp Business number. The agent will:
1. Receive the message via the webhook
2. Mark it as read (typing indicator)
3. Process it through the LangGraph agent
4. Send the AI response back via WhatsApp

### Verify webhook manually

```bash
# Test webhook verification
curl "http://localhost:2024/webhook?hub.mode=subscribe&hub.verify_token=your_verify_token&hub.challenge=test123"
# Should return: test123

# Test incoming message (simulated)
curl -X POST http://localhost:2024/webhook \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"254700000000","text":{"body":"Hello"},"id":"wamid.test123"}]}}]}]}'
```

---

## Production (Docker)

### Build and run

```bash
docker-compose up --build
```

### Exposed services

| Service | Host Port | Container Port | Description |
|---------|-----------|----------------|-------------|
| Workpods Agent | 8120 | 8000 | LangGraph API |
| PostgreSQL | 5430 | 5432 | Persistent database |
| Redis | 6379 | 6379 | Cache / state store |

### Production access

| Interface | URL |
|-----------|-----|
| API | http://localhost:8120 |
| API Docs | http://localhost:8120/api/v1/docs |
| LangGraph Studio | https://smith.langchain.com/studio/?baseUrl=http://localhost:8120 |

---

## Project Structure

```
src/
├── agent.py                  # Main agent definition
├── whatsapp/                 # WhatsApp integration
│   ├── webapp.py             # Starlette app with webhook endpoints
│   ├── whatsapp_client.py    # WhatsApp Cloud API client
│   └── agent_client.py       # LangGraph SDK client
├── state/                    # Agent state schema
├── context/                  # Agent context (user, company, LLM)
├── prompt/                   # Dynamic system prompt
├── llm/                      # LLM selection middleware
├── middleware/                # Context injection middleware
├── tools/                    # Agent tools
├── subagents/                # Delegated task agents
├── skills/                   # Domain-specific workflows
│   ├── project/              # Project management skill
│   ├── task/                 # Task management skill
│   └── milestone/            # Milestone tracking skill
└── utils/
```

---

## License

This project is part of the Workpods platform ecosystem.
