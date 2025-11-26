import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.genai import types
from mcp import StdioServerParameters

async def main():
    """Main asynchronous function to run the Playwright agent."""
    load_dotenv()
    google_api_key = os.environ.get("GEMINI_API_KEY")
    if not google_api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        return

    print("Python executable:", sys.executable)
    print("Python sys.path:", sys.path)
    print("✅ ADK components imported successfully.")
    
    playwright_mcp_tool = None
    try:
        retry_config = types.HttpRetryOptions(
            attempts=5,
            exp_base=7,
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],
        )

        playwright_server_params = StdioServerParameters(
            command="npx",
            args=["@playwright/mcp@latest"]
        )

        playwright_mcp_tool = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=playwright_server_params,
                timeout=60
            )
        )

        generate_content_config = types.GenerateContentConfig(
            temperature=0.05,
            top_k=5,
            top_p=0.98
        )

        print("✅ Playwright MCP Tool created successfully")
        agent_instructions = """
        You are a helpful web insurance automation agent. Use the playwright MCP Tool to navigate through the web pages and achieve required objective
        """
        
        playwright_agent = LlmAgent(
            model=Gemini(model="gemini-2.5-flash", api_key=google_api_key, retry_options=retry_config, generate_content_config=generate_content_config),
            name="playwright_agent",
            instruction=agent_instructions,
            tools=[playwright_mcp_tool],
        )

        runner_prompt = """

        """
        
        print("🚀 Starting the Playwright agent...")
        print("Type 'exit' or 'quit' to end the session\n")
        
        runner = InMemoryRunner(agent=playwright_agent, app_name="agents")
        c = 0
        # Initial system prompt
        print("Agent: Hello! I'm your Playwright assistant. What would you like me to help you with today?")
        response = await runner.run_debug("navigate to Login to 'https://www.royalsundaram.in/MOPIS/Login.jsp'", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("Enter username and password, user name is 'invictus_insurance' password is 'SundaramRoyal&323', click on sign in after both username and password are entered", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("From dashboard, click 'Rating Calculator' in side menu", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("Select 'New Business' icon under 'Type of Policy' and choose 'Private Car passenger' in the list of options present below", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("enter vehicle number GA 07 E 1252 and search for quote, note that there a 4 text boxes for the vehicle number input, add GA to first, 07 to the next one and so on", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("click on 'Get Quote' button", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("verify the proposal form and proceed", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("fill in the missing required fields with plausible values ", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("click on freeze quote button", verbose=True)
        # print(f"\nAgent: {response}\n")
        # response = await runner.run_debug("click on 'Download' button", verbose=True)
        # print(f"\nAgent: {response}\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Check for exit conditions
                if user_input.lower() in ('exit', 'quit'):
                    print("\nAgent: Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
                # response = await runner.run_debug("take a snapshot of the web page", verbose=True)
                response = await runner.run_debug(user_input, verbose=True)
                print(f"\nAgent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nAgent: Session ended by user.")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                continue
                
        return "Session ended"
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
    finally:
        print("✅ Cleanup completed")

async def run_main():
    """Wrapper function to properly handle cleanup of asyncio tasks."""
    try:
        return await main()
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        return None
    finally:
        print("\nCleaning up resources...")

if __name__ == "__main__":
    try:
        asyncio.run(run_main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        print("Script interrupted by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        loop = asyncio.get_event_loop()
        tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
        if tasks:
            for task in tasks:
                task.cancel()
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        if loop.is_running() and not loop.is_closed():
            loop.close()
