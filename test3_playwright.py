import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.genai import types
from mcp import StdioServerParameters

async def main():
    """Main asynchronous function to run the Playwright agent."""
    load_dotenv()

    print("Python executable:", sys.executable)
    print("Python sys.path:", sys.path)
    print("✅ ADK components imported successfully.")
    
    playwright_mcp_tool = None
    try:
        retry_config = types.HttpRetryOptions(
            attempts=5,                    
            exp_base=5,                     
            initial_delay=1,                
            max_delay=30,                   
            jitter=0.1,                     
            http_status_codes=[            
                408,  
                429,  
                500,  
                502,  
                503,  
                504,  
            ],
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

        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        model = LiteLlm(
            model="openai/gpt-4o",
            temperature=0.05,  
            top_p=0.98,      
            max_retries=5,  
            timeout=30,     
            request_timeout=60, 
        )
        
        print("✅ Playwright MCP Tool created successfully")
        agent_instructions = """
        You are a helpful web insurance automation agent. Use the playwright MCP Tool to navigate through the web pages and achieve required objective
        """
        if not openai_api_key:
            print("Error: OPENAI_API_KEY not found in environment variables.")
            return
            
        playwright_agent = LlmAgent(
            model=model,
            name="playwright_agent",
            instruction=agent_instructions,
            tools=[playwright_mcp_tool],
        )

        print("🚀 Starting the Playwright agent...")
        print("Type 'exit' or 'quit' to end the session\n")
        
        runner = InMemoryRunner(agent=playwright_agent, app_name="agents")
        c = 0
        print("Agent: Hello! I'm your Playwright assistant. What would you like me to help you with today?")

        response = await runner.run_debug("navigate to Login to 'https://www.royalsundaram.in/MOPIS/Login.jsp'", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("Enter username and password, user name is 'invictus_insurance' password is 'SundaramRoyal&323', click on sign in after both username and password are entered", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("From dashboard, click 'Rating Calculator' in side menu", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("Select 'New Business' icon under 'Type of Policy' then choose 'Private Car passenger' from the list of options presented, then click on the private car icon", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("enter vehicle number MH 02 FR 1294 and click on get started, note that there a 4 text boxes for the vehicle number input, add MH to first, 02 to the next one and so on", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("⁠Click Proceed on the popup that follows, do this for any popups that come up.", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("On the Policy details page, scroll down to the ‘Previous Insurance and Pre Inspection Details’, and set yesterday’s date under ‘Previous Policy Expiry Date’. Once the date is set, click ‘next’.", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("On The side menu that shows up, click on ‘proceed’. Say yes to any popups that come up.", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("on the vpc_comprehensive page, set distance to ‘unlimited km’ and Click on the ‘Freeze Quote Button.", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("On the side menu that comes up, enter name ‘ketan’, last name: ‘k’ , whatsapp number: 9999999999, and click on submit.", verbose=True)
        # print(f"\nAgent: {response}\n")
        response = await runner.run_debug("click on ‘policy documents’ dropdown, and choose ‘print quote’", verbose=True)
        # print(f"\nAgent: {response}\n")
        res = await runner.run_debug("download the generated pdf", verbose=True)
        # print(f"\nAgent: {res}\n")
        print(f"\nAgent: {response}\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ('exit', 'quit'):
                    print("\nAgent: Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
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
