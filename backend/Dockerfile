# Multi-stage build for backend
FROM python:3.12 as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /faceapi

# Copy project files
COPY backend/pyproject.toml ./
COPY backend/faceapi ./faceapi

# Install Python dependencies
RUN pip install -U setuptools
RUN pip install onnxruntime
RUN pip install -e . -v --no-build-isolation

# Production stage
FROM python:3.12

# Install runtime dependencies including OpenCV requirements
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    ffmpeg \
    libgl1 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Create app directory
WORKDIR /faceapi

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/faceapi ./faceapi
COPY backend/pyproject.toml ./

# Install the package in production mode
RUN pip install --no-cache-dir -e .

# Copy model file
# COPY test/g_m3.onnx /faceapi/model.onnx
RUN wget https://github.com/lijunjie2232/faceapi/releases/download/v1.0.0/model_s3_v1.onnx -O /faceapi/model.onnx

# Change ownership
RUN mkdir -p /faceapi/migrations && chown -R appuser:appgroup /faceapi && chmod -R 755 /faceapi/migrations

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application using the console script entry point
CMD ["faceapi"]