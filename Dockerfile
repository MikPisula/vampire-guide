# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# install curl
RUN apt-get update && apt-get install -y curl

# install pdm 
RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -

# pdm sync
RUN /root/.local/bin/pdm sync

# Update pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container (if your application uses this port)
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "test_augment.py"]
