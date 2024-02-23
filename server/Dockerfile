# Use an official Python runtime as a base image
FROM pytorch/pytorch:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Uvicorn
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

# Run the FastAPI app when the container launches using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]