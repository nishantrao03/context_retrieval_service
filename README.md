# Project Context Service

A Python-based backend service responsible for:

- Ingesting raw text context with metadata
- Chunking and embedding text
- Persisting embeddings in a local vector database
- Retrieving relevant context using metadata filters

This service does NOT:
- Handle authentication
- Call LLMs
- Contain Slack logic
- Manage projects or permissions

It exposes a small HTTP API consumed by a separate application.
