#syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10.14-bookworm

# Set the working directory in the container
WORKDIR /vara-backend

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

COPY . .

CMD flask run -h 0.0.0.0 -p 5000