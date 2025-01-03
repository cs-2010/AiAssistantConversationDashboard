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

def estimate_tokens(text: str) -> int:
    """
    Estimates the number of tokens in a text string.
    This is a simple heuristic - actual token count may vary.
    
    Args:
        text (str): Input text to estimate tokens for
        
    Returns:
        int: Estimated number of tokens
    """
    # Simple heuristic: ~4 characters per token on average
    return len(text) // 4

def create_conversation_prompt(messages: List[Dict[str, str]], max_tokens: int = 6000) -> str:
    """
    Creates a formatted prompt from conversation messages with token count control.
    
    Args:
        messages (List[Dict[str, str]]): List of message dictionaries containing 'role' and 'content'.
        max_tokens (int, optional): Maximum tokens for the prompt. Defaults to 6000 (Groq's TPM limit).
    
    Returns:
        str: Formatted prompt string.
    """
    prompt_start = "Please provide a concise summary of the following conversation. Focus on the key points and main topics discussed:\n\n"
    estimated_prompt_tokens = estimate_tokens(prompt_start)
    
    truncated_messages = []
    total_tokens = estimated_prompt_tokens
    
    # Reserve 40% of max tokens for model response and system overhead
    working_token_limit = int(max_tokens * 0.6)
    
    for msg in messages:
        role = msg.get('role', 'unknown').lower()
        content = msg.get('content', 'No content')
        
        message_format = f"{role.title()}: {content}\n"
        message_tokens = estimate_tokens(message_format)
        
        if total_tokens + message_tokens <= working_token_limit:
            truncated_messages.append(message_format)
            total_tokens += message_tokens
        else:
            # If we can't fit the full message, try to include a portion
            remaining_tokens = working_token_limit - total_tokens
            if remaining_tokens > 100:  # Only include partial if we have room for meaningful content
                chars_to_include = remaining_tokens * 4
                truncated_content = content[:chars_to_include]
                truncated_messages.append(f"{role.title()}: {truncated_content}...\n")
            break
    
    final_prompt = prompt_start + "".join(truncated_messages)
    # Add a note if messages were truncated
    if len(truncated_messages) < len(messages):
        final_prompt += "\n[Note: Some messages were truncated to fit within token limits]"
    
    return final_prompt

def summarize_conversation_groq(
    conversation_details: Dict[str, Any],
    contexts: List[Dict[str, Any]],
    messages: List[Dict[str, str]],
    *,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: Optional[int] = 1000,
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
        max_tokens (Optional[int], optional): Maximum number of tokens to generate. Defaults to 1000.
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
        
        # Create prompt with Groq's TPM limit in mind
        prompt = create_conversation_prompt(messages, max_tokens=6000)  # Groq's current TPM limit
        
        chat_completion: ChatCompletion = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that creates concise, informative summaries of conversations. Focus on the key points and main topics discussed."
            },
            {
                "role": "user",
                "content": prompt
            }],
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
        error_msg = str(e)
        st.error(f"Error while generating summary: {error_msg}")
        if "rate_limit_exceeded" in error_msg.lower():
            return "Unable to generate summary: The conversation is too long for the current token limits. Please try summarizing a shorter conversation."
        return "Failed to generate summary due to an error."
