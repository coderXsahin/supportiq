# SupportIQ
AI-Powered IT Incident & Ticket Automation Platform
## Overview
SupportIQ is a full-stack IT support automation platform that automatically:
- Classifies IT incidents using Machine Learning
- Predicts ticket priority
- Detects duplicate tickets
- Calculates SLA deadlines
- Provides resolution suggestions
- Tracks ticket status
- Displays support statistics through a React dashboard
## Technology Stack
Backend:
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- scikit-learn
Frontend:
- React
- Vite
- Recharts
- Nginx
DevOps:
- Docker
- Docker Compose
Testing:
- pytest
## Architecture
React Frontend
      |
      v
FastAPI Backend
      |
      +------ Machine Learning
      |
      +------ Ticket Automation
      |
      +------ PostgreSQL
## Machine Learning
SupportIQ uses:
TF-IDF + Logistic Regression
to classify tickets into:
- Network
- Database
- Application
- Security
- Hardware
- Access/Login
The current model achieved approximately 85% test accuracy.
## Ticket Automation
When a ticket is created:
New Ticket
    ↓
Duplicate Detection
    ↓
ML Category Prediction
    ↓
Priority Prediction
    ↓
SLA Calculation
    ↓
Resolution Suggestion
    ↓
PostgreSQL
## Duplicate Detection
Duplicate detection combines:
- TF-IDF similarity
- Keyword similarity
- Basic text normalization
Example:
Similarity: 0.6314
Duplicate detected: True
## SLA Monitoring
Tickets can have:
- ON_TRACK
- AT_RISK
- BREACHED
SLA states.
## API
Main endpoints:
GET /health
POST /tickets/
GET /tickets/
GET /tickets/{ticket_id}
PUT /tickets/{ticket_id}
DELETE /tickets/{ticket_id}
POST /tickets/check-duplicate
GET /tickets/stats/summary
GET /tickets/stats/categories
GET /tickets/stats/priorities
GET /tickets/stats/statuses
GET /tickets/{ticket_id}/sla
POST /ml/predict
## Docker
The application is fully containerized.
Containers:
- supportiq-frontend
- supportiq-backend
- supportiq-postgres
Run:
docker compose up -d
Frontend:
http://localhost:5173
Backend:
http://localhost:8001
Swagger API documentation:
http://localhost:8001/docs
## Testing
Run:
python -m pytest -q
Current result:
8 passed
## Project Structure
backend/
|
+-- app/
|   +-- api/
|   +-- database/
|   +-- ml/
|   +-- models/
|   +-- schemas/
|   +-- services/
|
+-- frontend/
+-- tests/
+-- Dockerfile
+-- docker-compose.yml
+-- requirements.txt
+-- README.md

## Key Engineering Concepts
- REST APIs
- Machine Learning
- PostgreSQL
- SQLAlchemy
- Ticket automation
- Incident classification
- Duplicate detection
- SLA monitoring
- React dashboard
- Docker
- Automated testing
## Author
Sahin Khatoon
Narula Institute of Technology
