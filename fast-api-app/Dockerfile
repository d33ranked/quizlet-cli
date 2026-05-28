# Use an official, lightweight Python base image
FROM python:3.11-slim

# Set system environment variables to optimize Python inside containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establish our working directory inside the container image
WORKDIR /code

# Copy over the requirements file first to take advantage of Docker layer caching
COPY ./requirements.txt /code/requirements.txt

# Install the application dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire app folder into the container working directory
COPY ./app /code/app

# Expose the internal port that Uvicorn binds to
EXPOSE 8000

# Run Uvicorn when the container launches, pointing to our application entry point
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]