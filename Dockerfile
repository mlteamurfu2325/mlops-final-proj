# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port on which the FastAPI app will run
EXPOSE 8000

# Set environment variables (if needed)
# ENV ENV_VAR_NAME=value

# Default command to run the FastAPI app using uvicorn
CMD ["uvicorn", "src.api.review_predict:app", "--host", "0.0.0.0", "--port", "8000"]
