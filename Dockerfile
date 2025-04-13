FROM python:3.12

# Environment setup
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy and install system dependencies
COPY packages.txt .
# Install system dependencies and FFmpeg
RUN apt-get update && \
    apt-get install -y \
    gnupg \
    curl \
    tesseract-ocr && \
    # Add the FFmpeg repository
    curl -fsSL https://packages.ffmpeg.org/ffmpeg-release.pub.key | tee /etc/apt/trusted.gpg.d/ffmpeg.asc && \
    echo "deb http://packages.ffmpeg.org/debian/ buster main" | tee /etc/apt/sources.list.d/ffmpeg.list && \
    apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY . .

# Copy Streamlit secrets file to expected path
RUN mkdir -p /root/.streamlit
COPY .streamlit/secrets.toml /root/.streamlit/secrets.toml

# Expose Streamlit's default port
EXPOSE 8501

# Health check endpoint
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "ui/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]