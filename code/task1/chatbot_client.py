import time
import json
import re
from openai import OpenAI

# Define the API client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="API_KEY",
)


# Function to send messages to the chatbot and receive responses
def ask_chatbot(prompt, table_content, max_retries, wait_time):
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n{table_content}"
                        }
                    ]
                }
            ],
        )
        
        # Check if the response is valid
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        # Wait before retrying
        time.sleep(wait_time)
    
    # If it fails after all attempts, return a default value or raise an exception
    print("Error: No valid response obtained after several attempts.")
    return None


# Function to recover an incomplete response by asking the model to continue
def ask_chatbot_recovery(prompt, continuation_prompt, max_retries, wait_time):
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n{continuation_prompt}"
                        }
                    ]
                }
            ],
        )
        
        # Check if the response is valid
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        # Wait before retrying
        time.sleep(wait_time)
    
    # If it fails after all attempts, return a default value or raise an exception
    print("Error: No valid response obtained after several attempts.")
    return None


# Function to check if a JSON response is complete
def is_response_complete(response):
    try:
        # Use a regex to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return False
        
        # Try to parse the JSON
        json.loads(json_match.group(0))
        return True
    except json.JSONDecodeError as e:
        return False


# Function to recover an incomplete response by asking the model to continue
def recover_incomplete_response(prompt, incomplete_response, table_content):
    continuation_prompt = f"Continue the incomplete response:\n{incomplete_response}\nFrom the table:\n{table_content}"
    continuation = ask_chatbot_recovery(prompt, continuation_prompt, 10, 10)
    if continuation:
        return incomplete_response + continuation
    return "{}"