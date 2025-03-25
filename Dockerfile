# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port (8080)
EXPOSE 8080

# Define the command to run the app using Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:8080", "exp5:app"]
