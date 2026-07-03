FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    sqlite3 \\
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir .

# Expose Streamlit port
EXPOSE 8501

# Command to run the dashboard by default
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]
