import sys

from .server import logger, mcp


def main():
    """Main entry point for the Snowflake Cortex Agent."""

    try:
        # Register the MCP server and start it
        logger.info("Starting Cortex Agent MCP server...")
        logger.info("Press Ctrl+C to stop the server")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
