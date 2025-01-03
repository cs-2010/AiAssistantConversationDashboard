"""
Utility functions for the AI Assistant Conversation Dashboard.
"""

import re
import html
import functools
from datetime import datetime
from src.styles import CODE_BLOCK_STYLE, DATETIME_FORMAT

# Regular expressions for markdown parsing
_code_block_regex = re.compile(r'```[\s\S]*?```|`[^`]+`')
_html_tag_regex = re.compile(r'</?(div|span|p)[^>]*>')
_bold_regex = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
_italic_regex = re.compile(r'\*(.+?)\*|_(.+?)_')

@functools.lru_cache(maxsize=128)
def escape_html_preserve_markdown(text: str) -> str:
    """Escape HTML while preserving markdown formatting.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Escaped text with preserved markdown
    """
    try:
        # Store code blocks temporarily
        code_blocks = []
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"CODE_BLOCK_{len(code_blocks)-1}_PLACEHOLDER"
        
        # Save code blocks before processing
        processed = re.sub(_code_block_regex, save_code_block, text)
        
        # Replace HTML tags with their escaped versions
        processed = processed.replace('&', '&amp;')\
                           .replace('<', '<')\
                           .replace('>', '>')\
                           .replace('"', '"')\
                           .replace("'", '&#39;')
        
        # Clean up any remaining problematic tags
        processed = re.sub(_html_tag_regex, '', processed)
        
        # Restore code blocks with proper formatting
        def format_code_block(match):
            index = int(match.group(1))
            block = code_blocks[index]
            if block.startswith('```'):
                # Multi-line code block
                code_content = block[3:-3].strip()  # Remove ``` and trim
                language = code_content.split('\n')[0] if code_content else ''
                code = code_content[len(language):].strip() if language else code_content
                return f'''<div style="background-color: {CODE_BLOCK_STYLE['bg_color']}; border: 1px solid {CODE_BLOCK_STYLE['border_color']}; border-radius: 4px; margin: 8px 0; padding: 8px 12px; font-family: monospace; white-space: pre-wrap; color: {CODE_BLOCK_STYLE['text_color']};"><code class="language-{language}">{html.escape(code)}</code></div>'''
            else:
                # Inline code
                code = block[1:-1]  # Remove backticks
                return f'<code style="background-color: {CODE_BLOCK_STYLE["bg_color"]}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{html.escape(code)}</code>'
        
        processed = re.sub(r'CODE_BLOCK_(\d+)_PLACEHOLDER', format_code_block, processed)
        
        # Handle other markdown elements (bold, italic, etc.)
        processed = re.sub(_bold_regex, r'<strong>\1\2</strong>', processed)  # Bold
        processed = re.sub(_italic_regex, r'<em>\1\2</em>', processed)  # Italic
        
        return processed
    except Exception as e:
        return f'Error processing message content: {str(e)}'

def format_timestamp(timestamp) -> str:
    """Format Unix timestamp to human-readable datetime string."""
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp/1000).strftime(DATETIME_FORMAT)
        return timestamp
    except:
        return 'N/A'

def save_groq_prompt(prompt: str, metadata: dict = None, base_dir: str = "prompts") -> str:
    """Save a GROQ prompt to a file for analysis.
    
    Args:
        prompt (str): The prompt text to save
        metadata (dict, optional): Additional metadata to save with the prompt. Defaults to None.
        base_dir (str, optional): Base directory for saving prompts. Defaults to "prompts".
        
    Returns:
        str: Path to the saved prompt file
    """
    import os
    import json
    from datetime import datetime
    
    # Get the project root directory (where the src folder is)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create prompts directory in project root
    prompts_dir = os.path.join(project_root, base_dir)
    os.makedirs(prompts_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groq_prompt_{timestamp}.txt"
    filepath = os.path.join(prompts_dir, filename)
    
    # Format metadata for better readability
    formatted_metadata = {
        "timestamp": timestamp,
        "metadata": {
            "Model Configuration": {
                "model": metadata.get("model", "unknown"),
                "temperature": metadata.get("temperature", "N/A"),
                "max_tokens": metadata.get("max_tokens", "N/A"),
                "top_p": metadata.get("top_p", "N/A"),
                "presence_penalty": metadata.get("presence_penalty", "N/A"),
                "frequency_penalty": metadata.get("frequency_penalty", "N/A")
            },
            "Conversation Details": {
                "conversation_id": metadata.get("conversation_id", "unknown"),
                "number_of_messages": metadata.get("num_messages", 0),
                "number_of_contexts": metadata.get("num_contexts", 0),
                "estimated_tokens": metadata.get("estimated_tokens", 0)
            }
        } if metadata else {}
    }
    
    # Format the content for the file
    content = []
    content.append("=" * 80)
    content.append("METADATA")
    content.append("=" * 80)
    content.append(json.dumps(formatted_metadata, indent=2, ensure_ascii=False))
    content.append("\n" + "=" * 80)
    content.append("PROMPT")
    content.append("=" * 80)
    content.append(prompt)
    content.append("\n" + "=" * 80)
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
        
    return filepath
