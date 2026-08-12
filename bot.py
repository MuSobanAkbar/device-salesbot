import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from groq import Groq

# Load environment variables securely
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# checklist model to track the state of the conversation
class SalesChecklist(BaseModel):
    device_type: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    is_complete: bool = False
    

# 2. System Instructions
SYSTEM_PROMPT = """
You are a CLI sales assistant. Your job is to collect 3 details from the user:
1. Device Type (phone, tablet, laptop, etc.)
2. Brand
3. Color
Capitalise all fields first letter, appopriately in the JSON output.
Based on the conversation, update the JSON checklist:
- If a field is unknown, leave it null.
- Use the 'agent_reply' field to ask the user for missing information in a friendly way.
- If you have successfully collected all 3 details, set 'is_complete' to true, and use 'agent_reply' to say "Thank you, your order is confirmed!"
"""

def main():
    print("🤖 Welcome to the CLI Sales Bot! (Type 'quit' to exit)\n")
    
    # Initialize conversation memory
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi! I can help you buy a device. What are you looking for?"}
    ]
    
    print("Bot: Hi! I can help you buy a device. What are you looking for?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        # 3. Call the LLM with Structured Outputs
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"}, # Forces JSON output
            temperature=0.1 
        )
        
        # 4. State Management & Observability
        json_output = response.choices[0].message.content
        state = SalesChecklist.model_validate_json(json_output)
 
        # Add the agent's generated reply to memory so it remembers the chat

        
        # DEBUG VIEW: This is observability. It lets you see the bot's "brain" working.
        print(f"\n[DEBUG STATE] -> Type: {state.device_type} | Brand: {state.brand} | Color: {state.color} | Complete: {state.is_complete}")
        
        # The actual UI output

        if state.is_complete:
            break

if __name__ == "__main__":
    main()