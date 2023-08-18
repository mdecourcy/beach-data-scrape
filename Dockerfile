# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside the container (if needed)
# EXPOSE 80

# Define environment variable (if needed)
# ENV VARIABLE_NAME default_value

# Run the script when the container launches
CMD ["python", "./waterquality.py"]
