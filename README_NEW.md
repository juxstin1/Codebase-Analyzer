# Backend Code Analyzer and Generator

A powerful tool that analyzes codebases and generates code using LM-Studio integration. Perfect for understanding project structure and generating new components.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **LM-Studio** installed and running locally with a compatible model
3. **Git** (optional, for version control)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd backend-solver
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure LM-Studio:**
   - Open LM-Studio
   - Load your preferred model (e.g., meta-llama-3.1-8b-instruct)
   - Start the local server (should be running on http://localhost:1234)

4. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   LM_STUDIO_API_URL=http://localhost:1234
   LM_STUDIO_MODEL=meta-llama-3.1-8b-instruct
   ```

5. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the application:**
   - Open your browser and go to `http://localhost:8000`
   - You should see the main interface with three tabs:
     - Code Generation
     - Codebase Analysis
     - File Creation

## Features

### 1. Codebase Analysis
- Analyzes project structure and code patterns
- Focuses on core application files (components, pages, styles)
- Provides insights and improvement suggestions

### 2. Code Generation
- Generates new code based on your requirements
- Supports multiple technologies and frameworks
- Context-aware generation using existing codebase

### 3. File Creation
- Creates new files with generated content
- Follows project conventions and patterns
- Integrates with existing codebase

## Usage Examples

1. **Analyze a Codebase:**
   - Click the "Analyze Codebase" tab
   - Enter the path to your project (e.g., `C:/Users/username/projects/my-app`)
   - Enter your query (e.g., "Review the frontend components and suggest improvements")
   - Click "Analyze"

2. **Generate Code:**
   - Click the "Generate Code" tab
   - Describe what you want to create
   - Specify the technology stack (optional)
   - Click "Generate"

3. **Create a New File:**
   - Click the "Create File" tab
   - Enter the file path and description
   - Click "Create"

## Troubleshooting

1. **Server won't start:**
   - Check if the port 8000 is available
   - Try a different port: `uvicorn main:app --reload --port 8001`

2. **LM-Studio connection error:**
   - Verify LM-Studio is running
   - Check your `.env` file configuration
   - Ensure the model is loaded in LM-Studio

3. **Analysis errors:**
   - Make sure the project path exists and is accessible
   - Check if the directory contains the expected file structure

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
