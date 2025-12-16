import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT

from dotenv import load_dotenv

load_dotenv()

# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    #TODO:
    # 1. Create MCP client and open connection to the MCP server (use `async with {YOUR_MCP_CLIENT} as mcp_client`),
    #    mcp_server_url="http://localhost:8005/mcp"
    client = MCPClient(mcp_server_url="http://localhost:8005/mcp")
    async with client as mcp_client:
    # 2. Get Available MCP Resources and print them
        print("Resources")
        resources: list[Resource] = await mcp_client.get_resources()
    # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
        print("Tools")
        tools: list[dict] = await mcp_client.get_tools()
        for tool in tools:
            print(json.dumps(tool, indent=2))
    # 4. Create DialClient
        dial_client = DialClient(
            api_key=os.getenv("DIAL_API_KEY"),
            endpoint="https://ai-proxy.lab.epam.com",
            tools=tools,
            mcp_client=mcp_client
        )
    # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
        messages: list[Message] = [
            Message(
                    role=Role.SYSTEM,
                    content=SYSTEM_PROMPT
                )
        ]
    # 6. Add to messages Prompts from MCP server as User messages
        print("Prompts")
        prompts: list[Prompt] = await mcp_client.get_prompts() 
        for prompt in prompts:
            content = await mcp_client.get_prompt(prompt.name)
            print(content)
            messages.append(
                Message(
                    role=Role.USER,
                    content=f"## Prompt from MCP server:\n{prompt.description}\n{content}"
                )
            )
    # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
    
        print("Type question or 'exit' to exit.")
        while True:
            user_input = input("\n> ").strip()
            if user_input.lower() == 'exit':
                break

            messages.append(
                Message(
                    role=Role.USER,
                    content=user_input
                )
            )

            ai_message: Message = await dial_client.get_completion(messages)
            messages.append(ai_message)

if __name__ == "__main__":
    asyncio.run(main())
