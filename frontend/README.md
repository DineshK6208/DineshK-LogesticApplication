# Logistics Project

This project contains a logistics management system with a Django backend and a React (Vite) frontend.

## Project Structure

- `backend/`: Django application with several modules (drivers, shipments, etc.).
- `frontend/`: React application built with Vite, TypeScript, and Tailwind CSS.

## Getting Started

### Prerequisites

- Node.js & npm
- Python 3.x

### Frontend Setup

```sh
cd frontend
npm install
npm run dev
```

### Backend Setup

```sh
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Technologies Used

- **Backend**: Django, Django Rest Framework
- **Frontend**: Vite, TypeScript, React, shadcn/ui, Tailwind CSS
