FROM python:3.14-slim

WORKDIR /app

# Install Python dependencies first
RUN pip install --no-cache-dir fastmcp mcp python-dotenv aiofile

# Install uvicorn and other runtime deps  
RUN pip install --no-cache-dir uvicorn httpx pydantic pydantic-settings sqlite-utils click cyclopts

# Copy app files
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Run HTTP server
CMD ["python", "http_server.py"]