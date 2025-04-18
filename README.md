# ERP BTP Light

A lightweight ERP system designed for construction companies, built with Flask (Backend) and Angular (Frontend).

## Features

- User Authentication & Authorization
- Client Management
- Project Management
- Quotation Generation
- Invoice Management
- Payment Tracking
- ERP Export System (JD Edwards compatible)
- PDF Generation for Documents

## Tech Stack

### Backend
- Python Flask
- SQLite Database
- JWT Authentication
- Flask-Mail for Email
- WeasyPrint for PDF Generation

### Frontend
- Angular 14+
- Bootstrap 5
- ng-bootstrap
- Font Awesome Icons

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+
- Git

## Project Structure

```
erp-btp-light/
├── frontend/           # Angular frontend application
├── backend/            # Flask backend application
│   ├── routes/         # API endpoints
│   ├── models/         # Database models
│   └── exports/        # Export system modules
└── requirements.txt    # Python dependencies
```

## Installation

### Development Environment

#### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd erp-btp-light
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a .env file in the backend directory:
```env
# Application Settings
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Email Configuration
MAIL_SERVER=your-smtp-server
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email

# Database
DATABASE_URL=sqlite:///db/database.sqlite
```

6. Initialize the database:
```bash
cd backend
python app.py
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
Create `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api'
};
```

3. Start the development server:
```bash
npm start
```

### Production Environment

#### Backend Deployment

1. Set up production environment variables in `.env.prod`:
```env
FLASK_ENV=production
DEBUG=False
# Configure other variables with production values
```

2. Install production dependencies:
```bash
pip install gunicorn
```

3. Start the production server:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend Deployment

1. Create production environment configuration:
Create `src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-api-domain/api'
};
```

2. Build for production:
```bash
ng build --configuration=production
```

3. Deploy the contents of `dist/` to your web server

## Running the Application

### Development

1. Start the backend server:
```bash
cd backend
python app.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Access the application at `http://localhost:4200`

### Production

1. Start the backend server using gunicorn
2. Serve the frontend build using nginx or apache
3. Access the application at your configured domain

## API Documentation

The backend provides the following API endpoints:

### Authentication
- POST /api/auth/register - Register a new user
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- GET /api/auth/user - Get current user info

### Clients
- GET /api/clients - List all clients
- GET /api/clients/<id> - Get client details
- POST /api/clients - Create new client
- PUT /api/clients/<id> - Update client
- DELETE /api/clients/<id> - Delete client

### Projects
- GET /api/projects - List all projects
- POST /api/projects - Create new project
- GET /api/projects/<id> - Get project details
- PUT /api/projects/<id> - Update project
- DELETE /api/projects/<id> - Delete project

### Exports
- GET /api/exports/pending - Get pending exports
- POST /api/exports/generate - Generate export file
- GET /api/exports/history - Get export history

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use Angular style guide for frontend code
- Write meaningful commit messages

### Testing
- Write unit tests for new features
- Run tests before submitting pull requests
- Maintain minimum 80% code coverage

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the project repository.