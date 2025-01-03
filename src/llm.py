"""
This module handles interactions with the LLM.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

def summarize_conversation(conversation_details, contexts, messages):
    """
    Summarizes the conversation using an LLM.

    Args:
        conversation_details (dict): Details about the conversation.
        contexts (list): List of context entries.
        messages (list): List of messages in the conversation.

    Returns:
        str: A summary of the conversation.
    """
    return "This is a placeholder summary."

def summarize_conversation_groq(conversation_details, contexts, messages):
    """
    Summarizes the conversation using the GROQ API.

    Args:
        conversation_details (dict): Details about the conversation.
        contexts (list): List of context entries.
        messages (list): List of messages in the conversation.

    Returns:
        str: A summary of the conversation.
    """
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = "Summarize the following conversation:\n"
    
    truncated_messages = []
    total_length = 0
    max_length = 1000  # Set a maximum length for the prompt
    
    for msg in messages:
        role = msg.get('role', 'unknown').lower()
        content = msg.get('content', 'No content')
        
        message_length = len(f"{role.title()}: {content}\n")
        
        if total_length + message_length <= max_length:
            truncated_messages.append(f"{role.title()}: {content}\n")
            total_length += message_length
        else:
            remaining_length = max_length - total_length
            if remaining_length > 0:
                truncated_content = content[:remaining_length]
                truncated_messages.append(f"{role.title()}: {truncated_content}...\n")
            break
    
    prompt += "".join(truncated_messages)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    
    return chat_completion.choices[0].message.content
