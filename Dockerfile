FROM python:3.6.5

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update pip3 version to latest version
RUN pip3 install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Install surround into the image
RUN python3 setup.py install
