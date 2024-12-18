import streamlit as st
from src.styles import (
    USER_COLORS, ASSISTANT_COLORS, CONTEXT_COLORS,
    TOPIC_CAPSULE_STYLE, CODE_BLOCK_STYLE, LANGUAGE_FLAGS
)
from src.utils import escape_html_preserve_markdown, format_timestamp
import json
import re

def format_footnotes(content: str, footnotes: dict) -> str:
    """Format footnotes by embedding them directly in the content.
    
    Args:
        content (str): Message content with footnote references
        footnotes (dict): Dictionary of footnote references
        
    Returns:
        str: Content with embedded footnotes
    """
    if not footnotes:
        return content
        
    # Find footnote references in the content (e.g., [^1], [^1^], [^note], or 1↩)
    pattern = r'\[\^([^\]^]+)\^?\]|\d+↩'
    
    def replace_footnote(match):
        ref = match.group(1) if match.group(1) else match.group(0).replace('↩', '')
        if ref in footnotes:
            footnote = footnotes[ref]
            # Check if footnote is an image
            if footnote.strip().startswith('!['):
                # Embed image directly
                return f'\n<div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">{footnote}</div>\n'
            else:
                # Embed text footnote with styling
                return f' <span style="background-color: #f8f9fa; padding: 4px 8px; border-radius: 3px; border-left: 2px solid #6c757d; margin: 0 4px; font-size: 0.9em;">({footnote})</span>'
        return match.group(0)
    
    # Replace all footnote references with their content
    formatted_content = re.sub(pattern, replace_footnote, content)
    
    # Remove the "Footnotes" section and everything after it
    footnotes_pattern = r'\n\s*Footnotes\s*\n.*$'
    formatted_content = re.sub(footnotes_pattern, '', formatted_content, flags=re.DOTALL)
    
    return formatted_content

def format_system_message(content: str) -> str:
    """Format system message content by properly handling boundary markers and metadata.
    
    Args:
        content (str): Raw system message content with boundary markers
        
    Returns:
        str: Formatted message content with improved readability
    """
    # Define the pattern to match JSON metadata between boundary markers
    pattern = r'--boundary-[a-f0-9]+\s*({\s*"source":[^}]+})\s*boundary-[a-f0-9]+\s*'
    
    # Split content into text blocks and metadata
    text_blocks = re.split(pattern, content)
    
    formatted_parts = []
    
    # Process each part
    for i in range(len(text_blocks)):
        part = text_blocks[i].strip()
        if not part:
            continue
            
        if part.startswith('{') and part.endswith('}'):
            # This is a metadata block
            try:
                metadata = json.loads(part)
                source = metadata.get("source", "N/A")
                reason = metadata.get("reason", "N/A")
                
                formatted_parts.append(
                    f'<div style="margin: 4px 0; padding: 6px; background-color: #f8f9fa; border-left: 3px solid #6c757d; font-size: 0.9em; color: #666;">'
                    f'📚 <strong>Source:</strong> {source}<br>'
                    f'💡 <strong>Context:</strong> {reason}'
                    f'</div>'
                )
            except json.JSONDecodeError:
                continue
        else:
            # This is a text block
            # Clean up whitespace while preserving intentional line breaks
            lines = [line.strip() for line in part.split('\n')]
            # Remove empty lines at start and end
            while lines and not lines[0]:
                lines.pop(0)
            while lines and not lines[-1]:
                lines.pop()
                
            # Join non-empty lines with appropriate spacing
            cleaned_text = ''
            current_block = []
            in_code_block = False
            
            for j, line in enumerate(lines):
                if line.startswith('```'):
                    if in_code_block:
                        # End of code block
                        current_block.append(line)
                        cleaned_text += escape_html_preserve_markdown('\n'.join(current_block))
                        current_block = []
                        in_code_block = False
                    else:
                        # Start of code block
                        if current_block:
                            cleaned_text += escape_html_preserve_markdown(' '.join(current_block))
                            current_block = []
                        current_block.append(line)
                        in_code_block = True
                elif in_code_block:
                    current_block.append(line)
                else:
                    # Check if line starts with a list marker or heading
                    is_list_or_heading = bool(re.match(r'^[#*\-\d]+[.)\s]', line))
                    
                    if not line:  # Empty line indicates section break
                        if current_block:
                            if cleaned_text and not cleaned_text.endswith('</p>'):
                                cleaned_text += escape_html_preserve_markdown(' '.join(current_block))
                            current_block = []
                        if j > 0 and j < len(lines) - 1:  # Don't add breaks at start or end
                            cleaned_text += '<br>'
                    elif is_list_or_heading:
                        if current_block:
                            cleaned_text += escape_html_preserve_markdown(' '.join(current_block))
                            current_block = []
                            cleaned_text += '<br>'
                        current_block.append(line)
                    else:
                        current_block.append(line)
            
            # Handle any remaining text
            if current_block:
                if in_code_block:
                    cleaned_text += escape_html_preserve_markdown('\n'.join(current_block))
                else:
                    cleaned_text += escape_html_preserve_markdown(' '.join(current_block))
            
            if cleaned_text:
                formatted_parts.append(
                    f'<div style="margin: 4px 0;">{cleaned_text}</div>'
                )
    
    return "\n".join(formatted_parts)

def get_sentiment_widget(sentiment: str) -> str:
    """Generate HTML for sentiment indicator widget using emojis."""
    sentiment_emojis = {
        'positive': '😊',
        'neutral': '😐',
        'negative': '😔'
    }
    emoji = sentiment_emojis.get(sentiment, sentiment_emojis['neutral'])
    return emoji

def format_topic_capsule(topic: str) -> str:
    """Format a single topic as a capsule."""
    return f'<span style="background-color: {TOPIC_CAPSULE_STYLE["bg_color"]}; color: {TOPIC_CAPSULE_STYLE["text_color"]}; padding: {TOPIC_CAPSULE_STYLE["padding"]}; border-radius: {TOPIC_CAPSULE_STYLE["border_radius"]}; border: 1px solid {TOPIC_CAPSULE_STYLE["border_color"]}; margin: {TOPIC_CAPSULE_STYLE["margin"]};">{topic}</span>'

def get_unity_topics_widget(topics: list) -> str:
    """Generate HTML for Unity topics widget."""
    if not topics:
        return ''
    formatted_topics = [format_topic_capsule(topic) for topic in topics]
    return f'🎮 {" ".join(formatted_topics)}'

def get_external_knowledge_widget(classification: dict) -> str:
    """Generate HTML for external knowledge widget with tooltip."""
    knowledge_level = classification.get('external_knowledge', 'none')
    knowledge_emojis = {
        'none': '📝',
        'intermediate': '📚',
        'advanced': '🎓'
    }
    emoji = knowledge_emojis.get(knowledge_level, knowledge_emojis['none'])
    return f'{emoji} {knowledge_level}'

def display_message(item: dict, item_type: str = 'message') -> None:
    """Display a message or context with appropriate styling.
    
    Args:
        item (dict): Message or context data to display
        item_type (str): Type of item ('message' or 'context')
    """
    if item_type == 'message':
        role = item.get('role', 'unknown').lower()
        content = item.get('content', 'No content')
        timestamp = format_timestamp(item.get('timestamp', 'N/A'))
        colors = USER_COLORS if role == 'user' else ASSISTANT_COLORS
        
        # Format footnotes if present
        if 'footnotes' in item:
            content = format_footnotes(content, item['footnotes'])
        
        # Check if content contains boundary markers and JSON metadata
        if '--boundary-' in content:
            formatted_content = format_system_message(content)
            message_html = f"""<div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;">{colors['icon']} {role.title()} | {timestamp}</div>
                <div style="color: {colors['text_color']}; background-color: {colors['content_bg']}; padding: 10px; border-radius: 5px;">{formatted_content}</div>
            </div>"""
            st.markdown(message_html, unsafe_allow_html=True)
            return
        
        # Get sentiment, Unity topics, and external knowledge from front_desk_classification_results
        classification = item.get('front_desk_classification_results', {})
        sentiment = classification.get('sentiment', 'neutral').lower()
        unity_topics = classification.get('unity_topics', [])
        
        sentiment_widget = get_sentiment_widget(sentiment)
        unity_topics_widget = get_unity_topics_widget(unity_topics)
        external_knowledge_widget = get_external_knowledge_widget(classification)
        
        # Create single-line header with all elements
        header_html = f"{colors['icon']} {role.title()} | {sentiment_widget} {unity_topics_widget} | {external_knowledge_widget} | {timestamp}"
        
        # Wrap the markdown content in a styled div
        message_html = f"""
        <div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;">
                {header_html}
            </div>
            <div style="color: {colors['text_color']}; background-color: {colors['content_bg']}; padding: 10px; border-radius: 5px;">
                <div class="markdown-content">
                    {content}
                </div>
            </div>
        </div>
        """
        
        # Add CSS to style markdown content
        st.markdown("""
        <style>
        .markdown-content h1, .markdown-content h2, .markdown-content h3, 
        .markdown-content h4, .markdown-content h5, .markdown-content h6 {
            color: inherit;
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }
        .markdown-content p {
            margin: 0.5em 0;
        }
        .markdown-content pre {
            margin: 0.5em 0;
            padding: 1em;
            background-color: rgba(255,255,255,0.9);
            border-radius: 5px;
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        .markdown-content pre code {
            all: unset;
            display: block;
        }
        .markdown-content pre * {
            text-shadow: none !important;
            box-shadow: none !important;
            background: none !important;
            border: none !important;
            outline: none !important;
        }
        .markdown-content :not(pre) > code {
            padding: 0.2em 0.4em;
            background-color: rgba(255,255,255,0.9);
            border-radius: 3px;
            border: 1px solid rgba(0,0,0,0.1);
        }
        .markdown-content ul, .markdown-content ol {
            margin: 0.5em 0;
            padding-left: 1.5em;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display the message
        st.markdown(message_html, unsafe_allow_html=True)
    else:  # context
        timestamp = format_timestamp(item.get('timestamp', 'N/A'))
        colors = CONTEXT_COLORS
        
        context_html = f"""<div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;"><strong>{colors['icon']} Context Used</strong> | {timestamp}</div>
            <details>
                <summary style="color: {colors['header_color']}; font-weight: 500; cursor: pointer; padding: 5px;">View Context Data</summary>
                <div style="color: {colors['text_color']}; margin-top: 10px; padding: 10px; border-radius: 5px; background-color: {colors['content_bg']};">{escape_html_preserve_markdown(str(item.get('data', 'No data available')))}</div>
            </details>
        </div>"""
        
        st.markdown(context_html, unsafe_allow_html=True)

def display_conversation_overview(conversation_details: dict, messages: list):
    """Display conversation overview in columns."""
    if not conversation_details:
        st.warning("No conversation details found")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("💭 Overview")
        st.write("ID:", conversation_details.get('id', conversation_details.get('conversation_id', 'Unknown')))
        st.write("Schema:", "v2" if 'history' in conversation_details else 
                          "v1" if 'message_history' in conversation_details else "Unknown")
        
        for field in ['created', 'updated']:
            if value := conversation_details.get(field):
                st.write(f"{field.capitalize()}:", format_timestamp(value))

    with col2:
        st.subheader("📊 Message Statistics")
        if messages:
            # Message counts by role
            role_counts = {}
            sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
            complexity_counts = {'none': 0, 'intermediate': 0, 'advanced': 0}
        
            for msg in messages:
                # Count by role
                role = msg.get('role', 'unknown').lower()
                role_counts[role] = role_counts.get(role, 0) + 1
                
                # Only count sentiment and complexity for user messages
                if role == 'user':
                    classification = msg.get('front_desk_classification_results', {})
                    sentiment = classification.get('sentiment', 'neutral').lower()
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                    
                    knowledge_level = classification.get('external_knowledge', 'none')
                    complexity_counts[knowledge_level] = complexity_counts.get(knowledge_level, 0) + 1
        
            # Display message counts in a compact format
            st.write(f"Total: {len(messages)} | User: {role_counts.get('user', 0)} | Assistant: {role_counts.get('assistant', 0)} | Other: {sum(role_counts.values()) - role_counts.get('user', 0) - role_counts.get('assistant', 0)}")
            
            # Display sentiment analysis
            st.write(f"Sentiment: 😊 Positive: {sentiment_counts['positive']} | 😐 Neutral: {sentiment_counts['neutral']} | 😔 Negative: {sentiment_counts['negative']}")
            
            # Display complexity analysis
            st.write(f"Complexity: 📝 Basic: {complexity_counts['none']} | 📚 Intermediate: {complexity_counts['intermediate']} | 🎓 Advanced: {complexity_counts['advanced']}")
            
        else:
            st.write("No messages found")

    with col3:
        st.subheader("🏷️ Metadata")
        first_msg = messages[0] if messages else {}
        
        # Display status indicators
        for status, (field, check) in {
            'Internal Unity': ('is_internal_unity', bool),
            'OPT Status': ('opt_status', lambda x: x.lower() == 'in')
        }.items():
            value = first_msg.get(field, False)
            st.write(f"{status}:", "✅" if (value and check(value)) else "❌")

        # Display classification data
        if messages:
            # Get language from first message
            if class_data := first_msg.get('front_desk_classification_results', {}):
                if lang := class_data.get('user_language'):
                    # Get flag emoji for the language
                    flag = LANGUAGE_FLAGS.get(lang.lower(), LANGUAGE_FLAGS['unknown'])
                    st.write("Language:", f"{flag} {lang}")
            
            # Collect all unique topics from all messages
            all_topics = set()
            for msg in messages:
                if class_data := msg.get('front_desk_classification_results', {}):
                    if topics := class_data.get('unity_topics'):
                        all_topics.update(topics)
            
            if all_topics:
                topics_html = " ".join([format_topic_capsule(topic) for topic in sorted(all_topics)])
                st.markdown(f"Topics: {topics_html}", unsafe_allow_html=True)

def display_formatted_conversation(conversation: dict, contexts: list, messages: list) -> None:
    """Display conversation data in a formatted, user-friendly way."""
    display_conversation_overview(conversation, messages)
    
    if messages:
        st.subheader("💬 Message History")
        
        # Create a dictionary of contexts indexed by their IDs
        context_dict = {ctx['id']: ctx for ctx in contexts}
        
        # Sort messages by timestamp
        timeline = []
        for msg in messages:
            timeline.append(('message', msg.get('timestamp', 0), msg))
            # If message has context, add it to timeline
            if msg.get('context_id') and msg.get('context_id') in context_dict:
                timeline.append(('context', msg.get('timestamp', 0), context_dict[msg.get('context_id')]))
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x[1])
        
        # Display items in chronological order
        for item_type, _, item in timeline:
            display_message(item, item_type)
    else:
        st.warning("No messages found in the conversation")
