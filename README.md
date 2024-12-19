# Backend Code Solver

A powerful backend code generator and troubleshooter that integrates with LM-Studio and Codestral-7B to provide intelligent backend solutions.

## Features

- Integration with LM-Studio API
- Backend code generation
- Code troubleshooting and debugging suggestions
- API endpoint generation
- Database schema suggestions
- Best practices recommendations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure LM-Studio:
- Make sure LM-Studio is running locally
- Load the Codestral-7B model
- Note down the API endpoint (default: http://localhost:1234/v1)

3. Run the application:
```bash
uvicorn main:app --reload
```

## Usage

The application provides several endpoints for different backend development needs:
- `/generate`: Generate backend code based on requirements
- `/troubleshoot`: Analyze and fix backend code issues
- `/optimize`: Get optimization suggestions for existing code

## Environment Variables

Create a `.env` file with the following variables:
```
LM_STUDIO_API_URL=http://localhost:1234/v1
```
