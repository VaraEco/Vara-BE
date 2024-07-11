FROM python:3.10

EXPOSE 8000/tcp

RUN mkdir /vara-backend
# Set the working directory in the container
WORKDIR /vara-backend

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

COPY . .

CMD [ "gunicorn","-c", "gunicorn.conf.py","--bind", "0.0.0.0:80", "app:app" ]