FROM langchain/langgraph-api:3.13-wolfi

# Set a clean working directory for app code
WORKDIR /app

# Copy entire project into /app
ADD . /app

# Install the whatsapp_agent in editable mode
RUN PYTHONDONTWRITEBYTECODE=1 uv pip install --system --no-cache-dir -c /api/constraints.txt -e .

# Set LANGSERVE_GRAPHS path using the proper path to your graph
ENV LANGSERVE_GRAPHS='{"workpods_agent": "/app/src/agents/main_agent/graph.py:graph"}'

# Create minimal API module structure (used by base image expectations)
RUN mkdir -p /api/langgraph_api /api/langgraph_runtime /api/langgraph_license && \
    touch /api/langgraph_api/__init__.py /api/langgraph_runtime/__init__.py /api/langgraph_license/__init__.py

# Install API module (if needed for framework compatibility)
RUN PYTHONDONTWRITEBYTECODE=1 uv pip install --system --no-cache-dir --no-deps -e /api

# Remove pip and build tools for security and size
RUN pip uninstall -y pip setuptools wheel && \
    rm -rf /usr/local/lib/python*/site-packages/pip* /usr/local/lib/python*/site-packages/setuptools* /usr/local/lib/python*/site-packages/wheel* && \
    find /usr/local/bin -name "pip*" -delete || true && \
    rm -rf /usr/lib/python*/site-packages/pip* /usr/lib/python*/site-packages/setuptools* /usr/lib/python*/site-packages/wheel* && \
    find /usr/bin -name "pip*" -delete || true && \
    uv pip uninstall --system pip setuptools wheel && \
    rm /usr/bin/uv /usr/bin/uvx || true

# Ensure container starts in /app
WORKDIR /app

