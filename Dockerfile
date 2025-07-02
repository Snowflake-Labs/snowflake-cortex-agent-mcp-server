FROM ghcr.io/astral-sh/uv:python3.12-alpine

LABEL org.opencontainers.image.source=https://github.com/kameshsampath/snowflake-cortex-mcp-server
LABEL org.opencontainers.image.description="Snowflake Cortex MCP Server(Experimental) - A server to handle Cortex Agent requests"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Create non-root user and group
RUN addgroup -S mcpuser && adduser -S -G mcpuser mcpuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Copy project files
COPY . /app/

# Change ownership to mcpuser
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Install project dependencies and the package itself
RUN uv sync --no-dev

# Command to run the server using the installed script
CMD ["uv", "run", "snowflake-cortex-agent"]
