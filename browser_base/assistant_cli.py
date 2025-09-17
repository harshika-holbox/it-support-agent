import os
import json
import asyncio
from pathlib import Path
from botocore.vendored.six import sys
from dotenv import load_dotenv
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from strands import Agent
from strands.models.openai import OpenAIModel

# Load environment variables from .env file
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

def load_mcp_config():
    config_path = Path.home() / ".cursor" / "mcp.json"
    mcp_url = "https://rube.app/mcp"
    headers = {}
    try:
        if config_path.exists():
            with open(config_path, "r") as f:
                cfg = json.load(f)
            server_cfg = cfg.get("mcpServers", {}).get("rube", {})
            if server_cfg.get("url"):
                mcp_url = server_cfg["url"]
            if isinstance(server_cfg.get("headers"), dict):
                headers.update(server_cfg["headers"])
    except Exception as e:
        print(f"Warning: failed to read {config_path}: {e}")

    if not any(h.lower() == "authorization" for h in headers.keys()):
        api_key = os.getenv("COMPOSIO_API_KEY") or os.getenv("RUBE_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
    return mcp_url, headers

if __name__ == "__main__":
    mcp_url, headers = load_mcp_config()
    rube_http_mcp_client = MCPClient(
        lambda: streamablehttp_client(
            url=mcp_url,
            headers=headers,
        )
    )

    with rube_http_mcp_client:
        tool_result = rube_http_mcp_client.list_tools_sync()
        model = OpenAIModel(
            client_args={
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            model_id="gpt-4o",
            params={
                "max_tokens": 1000,
                "temperature": 0.7,
            },
        )
        agent = Agent(
            model=model,
            tools=tool_result,
            system_prompt="""
                      You are a Gmail Assistant powered by Rube MCP. Your role is to assist users with managing their Gmail inboxes through natural language commands.

                        You can:

                        Send and manage emails: Compose, send, and organize messages, including attachments and labels. (Output and confirm the draft of the mail body you are sending with the user before actually sending it)

                        Search and retrieve emails: Locate specific emails using Gmail's search syntax, filter by sender, subject, date, and more.

                        Summarize email threads: Provide concise summaries of email conversations.

                        Manage labels and drafts: Create, update, and delete labels; manage email drafts.
                        """
        )

        print("\nAssistant ready. Type your request or '/quit' to exit.")
        while True:
            user_query = input("\nYou: ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["/quit", "/exit"]:
                print("Goodbye.")
                break

            result = None
            error = None
            try:
                result = agent(user_query)
            except Exception as e:
                error = str(e)
