# Use an official PyTorch runtime as a base image
FROM pytorch/pytorch:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for PyAudio
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create a non-root user and switch to it
RUN useradd -m myuser
USER myuser

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Uvicorn
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

# Start Uvicorn on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
