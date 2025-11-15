# Portfolio FIFO Analyzer Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY portfolio_analyzer.py .
COPY examples/ ./examples/

# Create directories for data and output
RUN mkdir -p csvs output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["python", "portfolio_analyzer.py"]
CMD ["--help"]
