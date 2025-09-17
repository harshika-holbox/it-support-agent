import requests
import json

def query_rube_mcp(query: str, mcp_url: str = "https://rube.app/mcp") -> str:
    """
    Query the Rube MCP server with a simple question.
    
    Args:
        query: The question or prompt to send
        mcp_url: The MCP server URL
        
    Returns:
        The response from the MCP server
    """
    try:
        payload = {
            "query": query,
            "context": {}
        }
        
        response = requests.post(
            mcp_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("success", False):
            response_data = result.get("response", {})
            return response_data.get("answer", response_data.get("text", "No answer found"))
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        return f"Request failed: {str(e)}"

if __name__ == "__main__":
    question = "What is the capital of France?"
    answer = query_rube_mcp(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")
