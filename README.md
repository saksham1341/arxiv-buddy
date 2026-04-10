# Arxiv Buddy

**A Multi-Agent AI Research Assistant for Scientific Literature**

Arxiv Buddy is an end-to-end **agentic AI system for scientific paper discovery, retrieval, comprehension, and conversational learning** built around arXiv papers.

It combines **specialized AI agents, a semantic knowledge base, PDF parsing pipelines, and a real-time chat interface** to help users search, learn, and interact with research papers efficiently.

---

## Features

### Multi-Agent Architecture

The system uses specialized agents orchestrated through **LangGraph**:

* **Orchestrator Agent**
  Handles conversation flow, intent understanding, routing, and agent coordination.

* **Searcher Agent**
  Generates optimized search queries, fetches relevant arXiv papers, and ranks results.

* **Learner Agent**
  Reads PDFs, extracts content, chunks documents, and converts them into structured knowledge.

This separation improves reasoning quality, modularity, and maintainability.

---

## Knowledge Base Pipeline

A dedicated **vector knowledge base microservice** powers semantic retrieval.

### Pipeline

1. Fetch research paper PDF
2. Parse using **PyMuPDF**
3. Chunk text into semantically meaningful sections [WIP]
4. Generate embeddings
5. Store in vector database
6. Retrieve relevant sections during conversation

This enables **context-aware question answering over scientific papers**.

---

## Real-Time Conversational Experience

The backend streams responses using **Server-Sent Events (SSE)** for a smooth real-time chat experience.

Users can:

* ask questions about papers
* request summaries
* continue contextual conversations
* receive streaming responses as the agents reason

---

## Tech Stack

### Backend

* Python
* FastAPI
* LangGraph
* LangChain
* PostgreSQL
* AsyncIO
* SSE
* ProcessPoolExecutor

### AI / Retrieval

* LLM-based agent workflows
* Semantic search
* Embeddings
* Vector retrieval
* PDF parsing

### Frontend

* React
* TypeScript
* Vite
* React Router

---

## System Architecture

Frontend (React)
→ FastAPI Agent Server
→ Multi-Agent Workflow
→ Search + PDF Learning Pipeline
→ Knowledge Base Server
→ Semantic Retrieval

---

## Key Engineering Highlights

* Built a **multi-agent research workflow**
* Designed a **separate knowledge base service**
* Implemented **async streaming responses**
* Used **process pools for CPU-heavy PDF parsing**
* Built a **production-style microservice architecture**
* Developed **full-stack real-time chat UX**
