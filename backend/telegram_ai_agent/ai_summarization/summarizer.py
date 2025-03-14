import google.generativeai as genai
from django.conf import settings
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class GeminiSummarizer:
    """
    Class to handle summarization of messages using Google's Gemini 2.0 Flash model
    """
    def __init__(self):
        # Configure the Gemini API with the API key from settings
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            logger.error("GOOGLE_API_KEY not set in environment variables")
            raise ValueError("GOOGLE_API_KEY not set in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _prepare_messages_for_summarization(self, messages: List[Dict[str, Any]]) -> str:
        """
        Prepare messages for summarization by formatting them into a structured text
        
        Args:
            messages: List of message dictionaries with sender_name, date, and text
            
        Returns:
            str: Formatted text ready for summarization
        """
        formatted_messages = []
        
        for msg in messages:
            # Format date to readable string
            date_str = msg['date'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Format message
            formatted_msg = f"[{date_str}] {msg['sender_name']}: {msg['text']}"
            formatted_messages.append(formatted_msg)
        
        return "\n".join(formatted_messages)
    
    def _create_summarization_prompt(self, formatted_messages: str, group_name: str, 
                                    start_date: datetime, end_date: datetime) -> str:
        """
        Create a prompt for the Gemini model to summarize the messages
        
        Args:
            formatted_messages: Formatted message text
            group_name: Name of the Telegram group
            start_date: Start date of the messages
            end_date: End date of the messages
            
        Returns:
            str: Complete prompt for the model
        """
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        prompt = f"""
        You are an AI assistant tasked with summarizing Telegram group chat messages.
        
        Please create a comprehensive summary of the following messages from the Telegram group "{group_name}" 
        for the period from {start_date_str} to {end_date_str}.
        
        The summary should:
        1. Identify the main topics and themes discussed
        2. Highlight key information and important announcements
        3. Note any significant decisions or conclusions reached
        4. Mention active participants and their main contributions
        5. Organize information in a clear, structured format
        6. Be comprehensive yet concise
        
        Here are the messages to summarize:
        
        {formatted_messages}
        
        Please provide only the summary without any introductory text or explanations about the summarization process.
        """
        
        return prompt
    
    async def generate_summary(self, messages: List[Dict[str, Any]], group_name: str, 
                              start_date: datetime, end_date: datetime) -> str:
        """
        Generate a summary of messages using Gemini 2.0 Flash
        
        Args:
            messages: List of message dictionaries with sender_name, date, and text
            group_name: Name of the Telegram group
            start_date: Start date of the messages
            end_date: End date of the messages
            
        Returns:
            str: Generated summary
        """
        try:
            # Prepare messages
            formatted_messages = self._prepare_messages_for_summarization(messages)
            
            # Create prompt
            prompt = self._create_summarization_prompt(
                formatted_messages, group_name, start_date, end_date
            )
            
            # Generate summary
            response = await self.model.generate_content_async(prompt)
            
            # Extract and return the summary text
            summary = response.text
            
            logger.info(f"Successfully generated summary for {group_name} from {start_date} to {end_date}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
