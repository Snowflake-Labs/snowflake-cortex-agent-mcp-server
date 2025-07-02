import json
import logging
import os
import re
import uuid
from typing import Any, Dict, List, Tuple

import httpx
from mcp.server.fastmcp import Context, FastMCP

from .payload_util import PayloadUtil

# Configure logging to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp_cortex_agent")

# Load values from environment variables or secrets
SEMANTIC_MODEL_FILE = os.getenv("SEMANTIC_MODEL_FILE")
CORTEX_SEARCH_SERVICE = os.getenv("CORTEX_SEARCH_SERVICE")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_PAT = os.getenv("SNOWFLAKE_PASSWORD")
AGENT_LLM_MODEL = os.getenv("CORTEX_AGENT_LLM_MODEL", "claude-3-5-sonnet")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")


# Required environment variables
required_env_vars = {
    "SEMANTIC_MODEL_FILE": SEMANTIC_MODEL_FILE,
    "CORTEX_SEARCH_SERVICE": CORTEX_SEARCH_SERVICE,
    "SNOWFLAKE_PASSWORD": SNOWFLAKE_PAT,
    "SNOWFLAKE_ACCOUNT": SNOWFLAKE_ACCOUNT,
}

for var_name, var_value in required_env_vars.items():
    if not var_value:
        raise ValueError(f"Set {var_name} environment variable")

mcp = FastMCP("snowflake_cortex_agent")

# Create SNOWFLAKE_ACCOUNT_URL with proper DNS formatting (replace underscores with dashes)
SNOWFLAKE_ACCOUNT_URL = (
    f"https://{re.sub(r'_', '-', SNOWFLAKE_ACCOUNT)}.snowflakecomputing.com"  # type: ignore
)

# Headers for API requests
API_HEADERS = {
    "Authorization": f"Bearer {SNOWFLAKE_PAT}",
    "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    "Content-Type": "application/json",
}


async def handle_response(resp: httpx.Response) -> Tuple[str, str, List[Dict]]:
    """
    Process SSE stream lines, extracting any 'delta' payloads,
    regardless of whether the JSON contains an 'event' field.
    """
    logger.info("Processing SSE response...")
    text, sql, citations = "", "", []
    async for raw_line in resp.aiter_lines():
        if not raw_line:
            continue
        raw_line = raw_line.strip()
        # only handle data lines
        if not raw_line.startswith("data:"):
            continue
        payload = raw_line[len("data:") :].strip()
        if payload in ("", "[DONE]"):
            continue
        try:
            evt = json.loads(payload)
        except json.JSONDecodeError:
            continue
        # Grab the 'delta' section, whether top-level or nested in 'data'
        delta = evt.get("delta") or evt.get("data", {}).get("delta")
        if not isinstance(delta, dict):
            continue
        for item in delta.get("content", []):
            t = item.get("type")
            if t == "text":
                text += item.get("text", "")
            elif t == "tool_results":
                for result in item["tool_results"].get("content", []):
                    if result.get("type") == "json":
                        j = result["json"]
                        text += j.get("text", "")
                        # capture SQL if present
                        if "sql" in j:
                            sql = j["sql"]
                        # capture any citations
                        for s in j.get("searchResults", []):
                            citations.append(
                                {
                                    "source_id": s.get("source_id"),
                                    "doc_id": s.get("doc_id"),
                                }
                            )
        logger.debug(f"Processed line: {raw_line}")
    return text, sql, citations


async def execute_sql(sql: str) -> Dict[str, Any]:
    """Execute SQL using the Snowflake SQL API.

    Args:
        sql: The SQL query to execute

    Returns:
        Dict containing either the query results or an error message
    """
    try:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Prepare the SQL API request
        sql_api_url = f"{SNOWFLAKE_ACCOUNT_URL}/api/v2/statements"
        sql_payload = {
            "statement": sql.replace(";", ""),
            "timeout": 60,  # 60 second timeout
            "warehouse": SNOWFLAKE_WAREHOUSE,
        }

        async with httpx.AsyncClient() as client:
            sql_response = await client.post(
                sql_api_url,
                json=sql_payload,
                headers=API_HEADERS,
                params={"requestId": request_id},
            )

            if sql_response.status_code == 200:
                logger.info(f"SQL executed successfully: {sql}")
                return sql_response.json()
            else:
                return {"error": f"SQL API error: {sql_response.text}"}
    except Exception as e:
        return {"error": f"SQL execution error: {e}"}


async def build_payload(query: str, ctx: Context) -> Dict[str, Any]:
    """
    Build the payload for the Cortex agent using a Jinja2 template.

    Args:
        query: The user's query/question to be processed by the agent
        ctx: The MCP context for logging

    Returns:
        Dict containing the complete payload structure for the Cortex agent API

    The template generates a payload with the following structure:
    {
        "model": "<agent_llm_model>",
        "response_instruction": "You are a helpful AI assistant.",
        "experimental": {},
        "tools": [
            {
                "tool_spec": {
                    "type": "cortex_analyst_text_to_sql",
                    "name": "Analyst1"
                }
            },
            {
                "tool_spec": {
                    "type": "cortex_search",
                    "name": "Search1"
                }
            },
            {
                "tool_spec": {
                    "type": "sql_exec",
                    "name": "SQLExecutionTool"
                }
            },
            {
                "tool_spec": {
                    "type": "data_to_chart",
                    "name": "DataToChart"
                }
            }
        ],
        "tool_resources": {
            "Analyst1": {"semantic_model_file": "<semantic_model_file>"},
            "Search1": {"name": "<cortex_search_service>"}
        },
        "tool_choice": {"type": "auto"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "<user_query>"
                    }
                ]
            }
        ]
    }
    """
    await ctx.log(
        level="info",
        message=f"""Template variables:
            Agent LLM: {AGENT_LLM_MODEL}
            Query: {query}
            Semantic Model File: {SEMANTIC_MODEL_FILE}
            Cortex Search Service: {CORTEX_SEARCH_SERVICE}
            """,
        logger_name="mcp_cortex_agent",
    )
    template_vars = {
        "agent_llm_model": AGENT_LLM_MODEL,
        "query": query,
        "semantic_model_file": SEMANTIC_MODEL_FILE,
        "cortex_search_service": CORTEX_SEARCH_SERVICE,
    }

    try:
        # Load and render the payload template
        payload_util = PayloadUtil("templates")
        payload_json = payload_util.render_template(**template_vars)
        if payload_json:
            payload_util.validate_json(payload_json)
            return json.loads(payload_json)
        return {}
    except ValueError as e:
        await ctx.log(
            level="error",
            message=f"Error validating JSON payload: {e}",
            logger_name="mcp_cortex_agent",
        )
        raise ValueError(f"Error validating JSON payload: {e}")


@mcp.tool(
    description="Run the Cortex agent with a user query using REST API and stream results via SSE.",
)
async def run_cortex_agents(query: str, ctx: Context) -> Dict[str, Any]:
    """Run the Cortex agent with the given query, streaming SSE."""
    # Build your payload exactly as before
    await ctx.log(
        level="info",
        message=f"Running Cortex agent with query: {query}",
        logger_name="mcp_cortex_agent",
    )
    payload = await build_payload(query, ctx)

    await ctx.log(
        level="info",
        message=f"Agent Payload:\n{payload}",
        logger_name="mcp_cortex_agent",
    )

    # (Optional) generate a request ID if you want traceability
    request_id = str(uuid.uuid4())

    url = f"{SNOWFLAKE_ACCOUNT_URL}/api/v2/cortex/agent:run"
    # Copy your API headers and add the SSE Accept
    headers = {
        **API_HEADERS,
        "Accept": "text/event-stream",
    }

    # 1) Open a streaming POST
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            url,
            json=payload,
            headers=headers,
            params={
                "requestId": request_id
            },  # SQL API needs this, Cortex agent may ignore it
        ) as resp:
            await ctx.log(
                level="error",
                message=f"Response:\n{resp}",
                logger_name="mcp_cortex_agent",
            )
            resp.raise_for_status()
            # 2) Now resp.aiter_lines() will yield each "data: …" chunk
            text, sql, citations = await handle_response(resp)

    # 3) If SQL was generated, execute it
    results = await execute_sql(sql) if sql else None

    return {
        "text": text,
        "citations": citations,
        "sql": sql,
        "results": results,
    }
