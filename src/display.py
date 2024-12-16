"""
Display components and UI functions for the AI Assistant Conversation Dashboard.
"""

import streamlit as st
from .styles import (
    USER_COLORS, ASSISTANT_COLORS, CONTEXT_COLORS,
    TOPIC_CAPSULE_STYLE, CODE_BLOCK_STYLE, LANGUAGE_FLAGS
)
from .utils import escape_html_preserve_markdown, format_timestamp

def get_sentiment_widget(sentiment: str) -> str:
    """Generate HTML for sentiment indicator widget using emojis.
    
    Args:
        sentiment (str): Sentiment value ('positive', 'neutral', or 'negative')
        
    Returns:
        str: HTML string for sentiment widget
    """
    sentiment_emojis = {
        'positive': '😊',
        'neutral': '😐',
        'negative': '😔'
    }
    emoji = sentiment_emojis.get(sentiment, sentiment_emojis['neutral'])
    return emoji

def format_topic_capsule(topic: str) -> str:
    """Format a single topic as a capsule.
    
    Args:
        topic (str): Topic to format
        
    Returns:
        str: HTML string for topic capsule
    """
    return f'<span style="background-color: {TOPIC_CAPSULE_STYLE["bg_color"]}; color: {TOPIC_CAPSULE_STYLE["text_color"]}; padding: {TOPIC_CAPSULE_STYLE["padding"]}; border-radius: {TOPIC_CAPSULE_STYLE["border_radius"]}; border: 1px solid {TOPIC_CAPSULE_STYLE["border_color"]}; margin: {TOPIC_CAPSULE_STYLE["margin"]};">{topic}</span>'

def get_unity_topics_widget(topics: list) -> str:
    """Generate HTML for Unity topics widget.
    
    Args:
        topics (list): List of Unity topics
        
    Returns:
        str: HTML string for Unity topics widget
    """
    if not topics:
        return ''
    
    formatted_topics = [format_topic_capsule(topic) for topic in topics]
    return f'🎮 {" ".join(formatted_topics)}'

def get_external_knowledge_widget(classification: dict) -> str:
    """Generate HTML for external knowledge widget with tooltip.
    
    Args:
        classification (dict): Classification data containing external_knowledge
        
    Returns:
        str: HTML string for external knowledge widget
    """
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
        
        # Get sentiment, Unity topics, and external knowledge from front_desk_classification_results
        classification = item.get('front_desk_classification_results', {})
        sentiment = classification.get('sentiment', 'neutral').lower()
        unity_topics = classification.get('unity_topics', [])
        
        sentiment_widget = get_sentiment_widget(sentiment)
        unity_topics_widget = get_unity_topics_widget(unity_topics)
        external_knowledge_widget = get_external_knowledge_widget(classification)
        
        # Create single-line header with all elements
        header_html = f"{colors['icon']} {role.title()} | {sentiment_widget} {unity_topics_widget} | {external_knowledge_widget} | {timestamp}"
        
        message_html = f"""<div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"><div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;">{header_html}</div><div style="color: {colors['text_color']}; background-color: {colors['content_bg']}; padding: 10px; border-radius: 5px;">{escape_html_preserve_markdown(content)}</div></div>"""
        
        st.markdown(message_html, unsafe_allow_html=True)
    else:  # context
        timestamp = format_timestamp(item.get('timestamp', 'N/A'))
        colors = CONTEXT_COLORS
        
        context_html = f"""<div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"><div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;"><strong>{colors['icon']} Context Used</strong> | {timestamp}</div><details><summary style="color: {colors['header_color']}; font-weight: 500; cursor: pointer; padding: 5px;">View Context Data</summary><div style="color: {colors['text_color']}; margin-top: 10px; padding: 10px; border-radius: 5px; background-color: {colors['content_bg']};">{escape_html_preserve_markdown(str(item.get('data', 'No data available')))}</div></details></div>"""
        
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
