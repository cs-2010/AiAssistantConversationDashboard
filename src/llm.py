"""
This module handles interactions with the LLM using the GROQ API.
"""

import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
from groq.types.chat import ChatCompletion

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# Cache the GROQ client using Streamlit's cache_resource
@st.cache_resource
def get_groq_client() -> Groq:
    """
    Creates and caches a GROQ client instance.
    
    Returns:
        Groq: A cached instance of the GROQ client.
    """
    return Groq(api_key=GROQ_API_KEY)

def create_conversation_prompt(messages: List[Dict[str, str]], max_length: int = 1000) -> str:
    """
    Creates a formatted prompt from conversation messages with length control.
    
    Args:
        messages (List[Dict[str, str]]): List of message dictionaries containing 'role' and 'content'.
        max_length (int, optional): Maximum length for the prompt. Defaults to 1000.
    
    Returns:
        str: Formatted prompt string.
    """
    prompt = "Summarize the following conversation:\n"
    truncated_messages = []
    total_length = 0
    
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
    
    return prompt + "".join(truncated_messages)

def summarize_conversation_groq(
    conversation_details: Dict[str, Any],
    contexts: List[Dict[str, Any]],
    messages: List[Dict[str, str]],
    *,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 1.0,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
) -> str:
    """
    Summarizes the conversation using the GROQ API with configurable parameters.

    Args:
        conversation_details (Dict[str, Any]): Details about the conversation.
        contexts (List[Dict[str, Any]]): List of context entries.
        messages (List[Dict[str, str]]): List of messages in the conversation.
        model (str, optional): ID of the model to use. Defaults to "llama-3.3-70b-versatile".
        temperature (float, optional): Sampling temperature between 0 and 2. Defaults to 0.7.
        max_tokens (Optional[int], optional): Maximum number of tokens to generate. Defaults to None.
        top_p (float, optional): Nucleus sampling parameter. Defaults to 1.0.
        presence_penalty (float, optional): Penalty for token presence. Defaults to 0.0.
        frequency_penalty (float, optional): Penalty for token frequency. Defaults to 0.0.

    Returns:
        str: A summary of the conversation.
        
    Raises:
        Exception: If the API call fails or returns an unexpected response.
    """
    try:
        client = get_groq_client()
        prompt = create_conversation_prompt(messages)
        
        chat_completion: ChatCompletion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        
        if not chat_completion.choices:
            raise Exception("No completion choices returned from the API")
            
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error while generating summary: {str(e)}")
        return "Failed to generate summary due to an error."
