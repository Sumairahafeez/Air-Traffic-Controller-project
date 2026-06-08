FROM python:3.9-slim

# Force python to output logs immediately so you can read real error logs
ENV PYTHONUNBUFFERED=1

# Install modern system dependencies for OpenCV and YOLO
USER root
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set up the mandatory Hugging Face user permission scheme
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy dependency definition and install
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the backend source files
COPY --chown=user . /app

# Open the network port required by Spaces
EXPOSE 7860

# Launch using Gunicorn to route traffic correctly
CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:7860", "--timeout", "120", "app:app"]