# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY app/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY app/ .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PORT 8080

# Run main.py when the container launches
CMD ["python", "main.py"]
