FROM python:3.6.5

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt from the current directory into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# List all tasks when the container launches
CMD ["python3", "-m", "web"]
