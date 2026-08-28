# AI-Powered ERP Stock Agent

An AI-powered stock management assistant built with Python and FastAPI. The project combines LLMs, RAG, vector search, tool calling, and ERP integration to provide intelligent responses to stock-related questions.

## 🚀 Features

- LLM-powered AI assistant
- RAG-based company policy search
- Embeddings and vector search
- AI Agent tool calling
- ERP API integration
- PostgreSQL database
- REST API
- JWT authentication
- Local LLM integration with Ollama

## 🧠 AI & RAG

The application uses a local LLM through Ollama.

The RAG pipeline retrieves relevant information from company policy documents using embeddings and vector search.

Available AI tools:

- `get_product_stock`
- `get_low_stock_products`
- `search_company_policy`
- `get_erp_product`

## 🔗 ERP Integration

The application communicates with an ERP API using HTTP requests.

The ERP integration supports:

- Product lookup
- Stock information
- Product category
- Product price
- API authentication
- Error handling

## 🏗️ Architecture

User → FastAPI → AI Service → Ollama LLM

The AI service can interact with:

- Product Stock Tool
- Low Stock Tool
- ERP Tool
- Company Policy RAG

## 🛠️ Tech Stack

### AI & Machine Learning

Python · Ollama · Llama 3.2 · LLM · RAG · Embeddings · Vector Search · AI Agents

### Backend

FastAPI · REST API · SQLAlchemy · PostgreSQL · HTTPX

### Database

PostgreSQL · Alembic

### Tools

Git · GitHub · VS Code · Postman

## 📂 Project Structure

stock-api/
├── ai/
│   ├── rag/
│   ├── ai_service.py
│   ├── llm_service.py
│   └── tools.py
├── repositories/
├── services/
│   └── erp_service.py
├── tests/
├── alembic/
├── database.py
├── main.py
├── models.py
├── schemas.py
└── security.py

## 🔐 Authentication

The API uses JWT-based authentication for protected endpoints.

Available authentication endpoints:

- `POST /auth/register`
- `POST /auth/login`

## 📡 API Endpoints

### Products

- `GET /products`
- `POST /products`
- `GET /products/{product_id}`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`

### ERP

- `GET /erp/products/{product_name}`
- `GET /mock-erp/products/{product_name}`

### AI

- `POST /ai/chat`

## 💬 Example

**User:**

What is the current stock level of iPhone 15?

**AI Response:**

iPhone 15 has 10 units currently in stock.

## 🎯 Purpose

This project demonstrates how LLMs, RAG, vector search, AI agents, REST APIs, and ERP systems can be combined into a practical enterprise software solution.

## 🔮 Future Improvements

- Multi-agent architecture
- MCP integration
- Azure OpenAI
- Cloud-based LLM deployment
- CI/CD pipelines
- Advanced AI monitoring and evaluation
