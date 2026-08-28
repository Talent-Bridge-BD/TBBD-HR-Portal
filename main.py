from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def home():
    return {"status": "MCP server running"}


@app.post("/mcp")
async def handle_mcp(request: Request):
    try:
        body = await request.json()
        method = body.get("method")

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": body.get("id", 1),
                "result": {
                    "tools": [
                        {
                            "name": "Semantic_Hybrid_Search",
                            "description": "Search HR documents",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"}
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                }
            }

        if method == "tools/call":
            query = (
                body.get("params", {})
                .get("arguments", {})
                .get("query", "")
            )

            return {
                "jsonrpc": "2.0",
                "id": body.get("id", 1),
                "result": {
                    "content": f"MCP working. Query received: {query}"
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1),
            "error": "Unknown method"
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "error": str(e)
        }
