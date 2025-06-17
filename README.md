# Snowflake Cortex Model Context Protocol (MCP) Server (Experimental)

This project implements a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server for seamless integration with Snowflake Cortex APIs. It enables developers to access Snowflake Cortex insights directly within their development environments, such as [Visual Studio Code (VSCode)](https://code.visualstudio.com/Download).

If you do not have VSCode installed, you can [download it here](https://code.visualstudio.com/Download).

[![Install Snowflake Cortex Agent MCP Server](https://img.shields.io/badge/VS_Code-Install_Cortex_Agent_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=snowflake-cortex-agent&inputs=%5B%7B%22id%22%3A%22snowflake_account%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Snowflake%20account%20identifier%22%2C%22default%22%3A%22%22%7D%2C%7B%22id%22%3A%22snowflake_user%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Snowflake%20username%22%2C%22default%22%3A%22%22%7D%2C%7B%22id%22%3A%22snowflake_password%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Snowflake%20password%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22snowflake_warehouse%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Snowflake%20Warehouse%20name%22%2C%22default%22%3A%22COMPUTE_WH%22%7D%2C%7B%22id%22%3A%22semantic_model_file%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22The%20fully%20qualified%20Snowflake%20stage%20path%20to%20the%20semantic%20model%20file%22%2C%22default%22%3A%22%22%7D%2C%7B%22id%22%3A%22cortex_search_service%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22The%20fully%20qualified%20name%20of%20Cortex%20Search%20Service%22%2C%22default%22%3A%22%22%7D%2C%7B%22id%22%3A%22cortex_agent_llm_model%22%2C%22type%22%3A%22pickString%22%2C%22description%22%3A%22The%20LLM%20model%20to%20use%20for%20Cortex%20Agent%22%2C%22default%22%3A%22snowflake-arctic%22%2C%22options%22%3A%5B%22claude-3-7-sonnet%22%2C%22deepseek-r1%22%2C%22mistral-large2%22%2C%22llama3.1-405b%22%2C%22snowflake-llama3.1-405b%22%2C%22snowflake-llama3.3-70b%22%2C%22snowflake-arctic%22%2C%22mixtral-8x7b%22%2C%22jamba-Instruct%22%2C%22llama3.2-1b%22%2C%22llama3.2-70b%22%2C%22llama3.2-3b%22%2C%22llama3.1-8b%22%2C%22mistral-7b%22%2C%22gemma-7b%22%5D%7D%5D&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22--name%22%2C%22snowflake-cortex-agent%22%2C%22-e%22%2C%22SNOWFLAKE_ACCOUNT_URL%22%2C%22-e%22%2C%22SNOWFLAKE_USER%22%2C%22-e%22%2C%22SNOWFLAKE_PASSWORD%22%2C%22-e%22%2C%22SEMANTIC_MODEL_FILE%22%2C%22-e%22%2C%22CORTEX_SEARCH_SERVICE%22%2C%22-e%22%2C%22SNOWFLAKE_WAREHOUSE%22%2C%22-e%22%2C%22CORTEX_AGENT_LLM_MODEL%22%2C%22ghcr.io%2Fkameshsampath%2Fsnowflake-cortex-mcp-server%3Alatest%22%5D%2C%22env%22%3A%7B%22SNOWFLAKE_ACCOUNT_URL%22%3A%22https%3A%2F%2F%24%7Binput%3Asnowflake_account%7D.snowflakecomputing.com%22%2C%22SNOWFLAKE_USER%22%3A%22%24%7Binput%3Asnowflake_user%7D%22%2C%22SNOWFLAKE_PASSWORD%22%3A%22%24%7Binput%3Asnowflake_password%7D%22%2C%22SEMANTIC_MODEL_FILE%22%3A%22%24%7Binput%3Asemantic_model_file%7D%22%2C%22CORTEX_SEARCH_SERVICE%22%3A%22%24%7Binput%3Acortex_search_service%7D%22%2C%22SNOWFLAKE_WAREHOUSE%22%3A%22%24%7Binput%3Asnowflake_warehouse%7D%22%2C%22CORTEX_AGENT_LLM_MODEL%22%3A%22%24%7Binput%3Acortex_agent_llm_model%7D%22%7D%7D)

> [!IMPORTANT]
>
> - **Disclaimer:** This project is experimental and intended for development and evaluation purposes only. **It is not officially supported by Snowflake**.
> - This is still a work in progress and may not be suitable for production use. Use at your own risk.

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (ensure MCP is enabled)
- [Snowflake Account](https://signup.snowflake.com/)

## Quick Start (Easy-way)

Click "Install Cortex Agent Server" badge

**(OR)**

Run the Snowflake Cortex MCP Server using Docker, follow these steps:

1. **Pull the Docker image:**

    ```bash
    docker pull ghcr.io/kameshsampath/snowflake-cortex-mcp/server:latest
    ```

2. **Run the Docker container:**

    There is a `.env.template` file in the repository that you can copy to `.env` and fill in the required values for your Snowflake account, user, password, warehouse, semantic model file, Cortex search service, and LLM model. This will help you avoid typing them directly in the command line.

    ```bash
    docker run -it --rm --name snowflake-cortex-agent \
      --env-file .env \
      ghcr.io/kameshsampath/snowflake-cortex-mcp/server:latest
    ```

    This command will start the Snowflake Cortex MCP Server in a Docker container, allowing you to interact with it using the Model Context Protocol.

## MCP Client Configuration

Now from any MCP compatible client, such as [VSCode](https://code.visualstudio.com/Download) or [Claude Desktop](https://www.anthropic.com/claude/desktop), add the following MCP server configuration:

```json
{
  "mcpServers": {
    "snowflake-cortex-agent": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--name",
        "snowflake-cortex-agent",
        "-e",
        "SNOWFLAKE_ACCOUNT_URL",
        "-e",
        "SNOWFLAKE_USER",
        "-e",
        "SNOWFLAKE_PASSWORD",
        "-e",
        "SEMANTIC_MODEL_FILE",
        "-e",
        "CORTEX_SEARCH_SERVICE",
        "-e",
        "SNOWFLAKE_WAREHOUSE",
        "-e",
        "CORTEX_AGENT_LLM_MODEL",
        "ghcr.io/kameshsampath/snowflake-cortex-mcp/server:latest"
      ],
      "env": {
        "SNOWFLAKE_ACCOUNT_URL": "https://${input:snowflake_account}.snowflakecomputing.com",
        "SNOWFLAKE_USER": "${input:snowflake_user}",
        "SNOWFLAKE_PASSWORD": "${input:snowflake_password}",
        "SEMANTIC_MODEL_FILE": "${input:semantic_model_file}",
        "CORTEX_SEARCH_SERVICE": "${input:cortex_search_service}",
        "SNOWFLAKE_WAREHOUSE": "${input:snowflake_warehouse}",
        "CORTEX_AGENT_LLM_MODEL": "${input:cortex_agent_llm_model}"
      }
    }
  }
}
```

> [!TIP]
> The repo already has one [.vscode/mcp.json](.vscode/mcp.json) that helps you get started with the MCP server configuration in VSCode.

## Building and Running Locally(Hard-way)

To build and run the Snowflake Cortex MCP Server locally using [uv](https://github.com/astral-sh/uv):

1. **Clone the repository:**

    ```bash
    git clone https://github.com/kameshsampath/snowflake-cortex-mcp-server.git
    cd snowflake-cortex-mcp-server
    ```

2. **Create and activate a Python virtual environment:**

    ```bash
    uv venv
    source .venv/bin/activate
    ```

3. **Install dependencies with uv:**

    ```bash
    uv sync
    ```

4. **Set required environment variables:**

    ```bash
    export SNOWFLAKE_ACCOUNT_URL="https://<your_account>.snowflakecomputing.com"
    export SNOWFLAKE_USER="<your_username>"
    export SNOWFLAKE_PASSWORD="<your_password>"
    export SNOWFLAKE_WAREHOUSE="<your_warehouse>"
    export SEMANTIC_MODEL_FILE="<stage_path_to_semantic_model>"
    export CORTEX_SEARCH_SERVICE="<cortex_search_service_name>"
    export CORTEX_AGENT_LLM_MODEL="<llm_model_name>"
    ```

5. **Run the MCP server:**

    ```bash
    uv run snowflake_cortex_mcp_server
    ```

The server should now be running locally and ready to accept MCP requests.

## References

- [Model Context Protocol Introduction](https://modelcontextprotocol.io/introduction)
- [Snowflake Cortex Agents Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [VSCode MCP Servers Guide](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
