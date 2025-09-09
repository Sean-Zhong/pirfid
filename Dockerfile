# Use a slim version of Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

RUN apt-get update && apt-get install -y libusb-1.0-0-dev

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY cast_server.py .

# Expose the port that Flask will run on
EXPOSE 5000

# Set the command to run the Flask application
CMD ["python", "cast_server.py"]
