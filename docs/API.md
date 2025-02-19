# API Documentation

## 📚 Table of Contents
- [Overview](#overview)
- [Endpoints](#endpoints)
- [Authentication](#authentication)
- [Examples](#examples)

## Overview
Extrix provides a REST API for data extraction. The API is built with FastAPI and supports both synchronous and asynchronous operations.

## Endpoints

### POST /extract
Extract data from a document.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: Document file (PDF, DOCX, etc.)
  - `config`: JSON string containing extraction configuration

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "config={\"languages\":[\"fr\"],\"model\":\"gemini-1.5-pro\"}"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "result": null,
  "error": null
}
```

### GET /status/{job_id}
Get the status of an extraction job.

**Request:**
- Method: `GET`
- Parameters:
  - `job_id`: UUID of the extraction job

```bash
curl "http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "result": {
    // Extracted data according to model schema
  },
  "error": null
}
```

## Authentication
Currently, the API doesn't require authentication. For production use, implement appropriate authentication mechanisms.

## Examples
See [examples](EXAMPLES.md) for more detailed API usage examples.
