from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import re
from typing import List, Optional
import glob
from pathlib import Path

load_dotenv()

app = FastAPI(title="Agentic Code Expert")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

LM_STUDIO_API_URL = os.getenv("LM_STUDIO_API_URL", "http://192.168.56.1:1234")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "meta-llama-3.1-8b-instruct")

class CodeRequest(BaseModel):
    prompt: str
    technology: str | None = None
    context_files: List[str] = []

class FileCreationRequest(BaseModel):
    path: str
    content: str
    description: str

class CodebaseAnalysisRequest(BaseModel):
    directory: str
    query: str

def read_file_content(file_path: str) -> str:
    """Read and return the content of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_file_context(files: List[str]) -> str:
    """Get the content of specified files for context"""
    context = []
    for file in files:
        if os.path.exists(file):
            content = read_file_content(file)
            context.append(f"File: {file}\n```\n{content}\n```\n")
    return "\n".join(context)

def create_file(path: str, content: str) -> bool:
    """Create a new file with the specified content"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating file: {str(e)}")

def analyze_directory(directory: str) -> list:
    """Analyze a directory and return information about files"""
    # Only look at core project files
    core_files = [
        'App.js',              # Main React component
        'App.jsx',
        'App.tsx',
        'index.js',            # Entry point
        'index.jsx',
        'index.tsx',
        'components/*.js',      # React components
        'components/*.jsx',
        'components/*.tsx',
        'pages/*.js',          # Page components
        'pages/*.jsx',
        'pages/*.tsx',
        'styles/*.css',        # Stylesheets
        'styles/*.scss'
    ]
    
    files = []
    try:
        # First check root directory
        root_files = ['package.json']  # Only check package.json in root
        for file in root_files:
            full_path = os.path.join(directory, file)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                files.append({
                    'path': full_path,
                    'name': file,
                    'relative_path': file,
                    'size': os.path.getsize(full_path)
                })

        # Then check src directory for core files
        src_dir = os.path.join(directory, 'src')
        if os.path.exists(src_dir):
            for pattern in core_files:
                if '*' in pattern:
                    # Handle patterns with wildcards
                    base_dir = os.path.dirname(pattern)
                    file_pattern = os.path.basename(pattern)
                    search_dir = os.path.join(src_dir, base_dir)
                    if os.path.exists(search_dir):
                        for file in os.listdir(search_dir):
                            if file.endswith(file_pattern.replace('*', '')):
                                full_path = os.path.join(search_dir, file)
                                if os.path.isfile(full_path):
                                    rel_path = os.path.join('src', base_dir, file)
                                    files.append({
                                        'path': full_path,
                                        'name': file,
                                        'relative_path': rel_path,
                                        'size': os.path.getsize(full_path)
                                    })
                else:
                    # Handle direct file matches
                    full_path = os.path.join(src_dir, pattern)
                    if os.path.exists(full_path) and os.path.isfile(full_path):
                        rel_path = os.path.join('src', pattern)
                        files.append({
                            'path': full_path,
                            'name': pattern,
                            'relative_path': rel_path,
                            'size': os.path.getsize(full_path)
                        })
                        
        print("Found files:", [f['relative_path'] for f in files])  # Debug log
    except Exception as e:
        print(f"Error scanning directory: {str(e)}")
    
    return files

def ask_llm(prompt: str) -> str:
    """Send a prompt to LM-Studio and get the response"""
    try:
        print(f"Sending request to LLM at: {LM_STUDIO_API_URL}")
        response = requests.post(
            f"{LM_STUDIO_API_URL}/v1/chat/completions",
            json={
                "model": LM_STUDIO_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert developer and code architect. Analyze code, suggest improvements, and provide complete solutions. Format code blocks using triple backticks with language tags."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False
            }
        )
        print(f"LLM Response status: {response.status_code}")
        print(f"LLM Response content: {response.text[:500]}...")  # Print first 500 chars
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        print(f"Extracted content: {content[:500]}...")  # Print first 500 chars
        return content
    except requests.exceptions.RequestException as e:
        print(f"LLM Request Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with LM-Studio: {str(e)}")
    except Exception as e:
        print(f"Unexpected LLM Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error with LM-Studio: {str(e)}")

def extract_code_blocks(text: str) -> list[dict]:
    """Extract code blocks and their explanations from the LLM response"""
    # Split by code blocks (marked by triple backticks)
    parts = re.split(r'```(\w*)\n(.*?)```', text, flags=re.DOTALL)
    
    blocks = []
    current_explanation = parts[0].strip()
    
    for i in range(1, len(parts), 3):
        if i + 1 >= len(parts):
            break
            
        language = parts[i].strip() or "plaintext"
        code = parts[i + 1].strip()
        next_text = parts[i + 2].strip() if i + 2 < len(parts) else ""
        
        blocks.append({
            "type": "code",
            "language": language,
            "content": code
        })
        
        if next_text:
            blocks.append({
                "type": "explanation",
                "content": next_text
            })
    
    if current_explanation:
        blocks.insert(0, {
            "type": "explanation",
            "content": current_explanation
        })
    
    return blocks

def analyze_file_chunk(file_info: dict, content: str) -> str:
    """Analyze a single file and return insights"""
    prompt = f"""Analyze this file and provide insights:

File: {file_info['path']}
Content:
```
{content}
```

Please provide:
1. File purpose and main functionality
2. Key components or configurations
3. Potential issues or improvements
"""
    try:
        return ask_llm(prompt)
    except Exception as e:
        return f"Error analyzing file: {str(e)}"

def summarize_analyses(file_analyses: list, query: str) -> dict:
    """Combine individual file analyses into a comprehensive summary"""
    summary_prompt = f"""As a project manager, review these file analyses and answer the query: "{query}"

Individual file analyses:
{chr(10).join(file_analyses)}

Please provide a comprehensive summary including:
1. Overall project status and structure
2. Key findings and insights
3. Recommended next steps
4. Potential improvements

Format your response with clear sections and bullet points."""

    try:
        summary = ask_llm(summary_prompt)
        blocks = extract_code_blocks(summary)
        if not blocks:
            blocks = [{
                "type": "explanation",
                "content": summary
            }]
        return {
            "blocks": blocks,
            "files_analyzed": len(file_analyses)
        }
    except Exception as e:
        return {
            "blocks": [{
                "type": "explanation",
                "content": f"Error generating summary: {str(e)}"
            }],
            "files_analyzed": len(file_analyses)
        }

@app.post("/generate")
async def generate_code(request: CodeRequest):
    """Generate code based on user requirements with context awareness"""
    context = get_file_context(request.context_files) if request.context_files else ""
    
    prompt = f"""Task: {request.prompt}

Technical Context: {request.technology if request.technology else 'Not specified'}

Existing Codebase Context:
{context}

Please provide:
1. Complete, working code solution
2. Explanation of the implementation
3. Integration suggestions with existing code
4. Best practices and potential improvements
"""
    
    solution = ask_llm(prompt)
    blocks = extract_code_blocks(solution)
    
    return {
        "blocks": blocks,
        "note": "Generated using LM-Studio with Meta Llama 3.1"
    }

@app.post("/analyze")
async def analyze_codebase(request: CodebaseAnalysisRequest):
    """Analyze a codebase and provide insights"""
    try:
        print(f"Analyzing directory: {request.directory}")
        if not os.path.exists(request.directory):
            print(f"Directory not found: {request.directory}")
            return {
                "blocks": [{
                    "type": "explanation",
                    "content": f"Directory not found: {request.directory}"
                }],
                "files_analyzed": 0
            }

        files = analyze_directory(request.directory)
        print(f"Found {len(files)} files")
        
        if not files:
            print("No code files found")
            return {
                "blocks": [{
                    "type": "explanation",
                    "content": f"No code files found in directory: {request.directory}"
                }],
                "files_analyzed": 0
            }

        # Analyze each file individually
        file_analyses = []
        for file in files:
            try:
                print(f"Reading file: {file['path']}")
                content = read_file_content(file['path'])
                # Truncate content if too large (keeping first and last parts)
                if len(content) > 2000:  # Adjust this threshold as needed
                    content = content[:1000] + "\n... (content truncated) ...\n" + content[-1000:]
                
                analysis = analyze_file_chunk(file, content)
                file_analyses.append(f"### Analysis for {file['name']}:\n{analysis}")
            except Exception as e:
                print(f"Error analyzing file {file['path']}: {str(e)}")
                continue

        if not file_analyses:
            print("Could not analyze any files")
            return {
                "blocks": [{
                    "type": "explanation",
                    "content": "Could not analyze any files in the directory"
                }],
                "files_analyzed": 0
            }

        # Combine individual analyses into a final summary
        print("Generating final summary")
        return summarize_analyses(file_analyses, request.query)

    except Exception as e:
        print(f"Analysis Error: {str(e)}")
        return {
            "blocks": [{
                "type": "explanation",
                "content": f"Error analyzing codebase: {str(e)}"
            }],
            "files_analyzed": 0
        }

@app.post("/create-file")
async def create_new_file(request: FileCreationRequest):
    """Create a new file with generated content"""
    if os.path.exists(request.path):
        raise HTTPException(status_code=400, detail="File already exists")
    
    prompt = f"""Create a new file: {request.path}
Description: {request.description}

Please provide:
1. Complete file content
2. Explanation of the implementation
3. Integration notes
"""
    
    solution = ask_llm(prompt)
    blocks = extract_code_blocks(solution)
    
    # Extract the first code block for the file content
    code_block = next((block for block in blocks if block["type"] == "code"), None)
    if code_block:
        create_file(request.path, code_block["content"])
    
    return {
        "blocks": blocks,
        "file_created": request.path
    }

@app.get("/")
async def root():
    """Serve the main HTML interface"""
    return FileResponse("static/index.html")
