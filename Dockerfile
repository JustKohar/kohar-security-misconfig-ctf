# Use a small Python image
FROM python:3.12-slim

# Ensure output is flushed (useful for logs)
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose the port the app listens on
EXPOSE 5000

# Default command: run the Flask app
CMD ["python", "app.py"]

