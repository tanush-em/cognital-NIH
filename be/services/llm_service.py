import os
from groq import Groq
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """Initialize LLM service with Groq API"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  
    
    def generate_response(self, 
                        user_message: str, 
                        context: str = "") -> Dict[str, Any]:
        """Generate AI response using Groq API"""
        try:
            system_prompt = self._build_system_prompt(context)
            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "user", "content": user_message})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                'response': ai_response,
                'confidence': 0.8,  # Default confidence
                'model': self.model,
                'tokens_used': response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                'confidence': 0.1,
                'model': self.model,
                'error': str(e)
            }
    
    def _build_system_prompt(self, context: str = "") -> str:
        """Build system prompt for telecom support"""
        base_prompt = """You are a helpful AI assistant for a telecom support system. 
        You help customers with their telecom-related questions and issues.
        
        Guidelines:
        - Be friendly, professional, and helpful
        - Provide accurate information based on the context provided
        - If you don't know something, say so and offer to connect them with a human agent
        - Keep responses concise but informative
        - Use simple, clear language
        """
        
        if context:
            base_prompt += f"\n\nRelevant information:\n{context}"
        
        return base_prompt
    
    def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment and detect frustration"""
        frustration_keywords = [
            'angry', 'frustrated', 'annoyed', 'upset', 'mad', 'irritated',
            'not working', 'broken', 'terrible', 'awful', 'horrible',
            'refund', 'cancel', 'complaint', 'sue', 'legal'
        ]
        
        message_lower = message.lower()
        frustration_score = sum(1 for keyword in frustration_keywords if keyword in message_lower)
        
        sentiment_score = min(1.0, frustration_score / len(frustration_keywords))
        
        return {
            'sentiment_score': sentiment_score,
            'is_frustrated': sentiment_score > 0.3,
            'frustration_keywords_found': [kw for kw in frustration_keywords if kw in message_lower]
        }

# Global LLM service instance
llm_service = LLMService()
