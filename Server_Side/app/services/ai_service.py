"""
AI service for generating medical responses using Groq API.
"""
# Import AsyncOpenAI client for making async API calls
from openai import AsyncOpenAI
# Import logging module for application logging
import logging
# Import Optional from typing for optional parameters
from typing import Optional
# Import asyncio for timeout handling
import asyncio
# Import configuration variables for Groq API
from app.core.config import (
    GROQ_API_KEY, 
    GROQ_BASE_URL, 
    GROQ_MODEL, 
    AI_TEMPERATURE, 
    AI_MAX_TOKENS,
    AI_TOP_P,
    AI_FREQUENCY_PENALTY,
    AI_PRESENCE_PENALTY,
    AI_STOP_SEQUENCES,
    REQUEST_TIMEOUT
)
# Import text processing utility to clean markdown formatting
from app.utils.text_processing import clean_markdown_formatting

# Create logger instance for this module
logger = logging.getLogger(__name__)

# System prompt that defines Pulse AI's persona and behavior
# This prompt instructs the AI to behave like an experienced medical doctor
SYSTEM_PROMPT = """You are Pulse AI, an experienced medical doctor and clinical AI assistant. You conduct diagnosis through a structured Q&A process and behave professionally and calmly at all times.

CRITICAL RULES:
1. You MUST ONLY answer health-related questions (symptoms, medicine, medical conditions, wellness).
2. For non-medical questions, respond professionally: "I'm Pulse AI, a medical assistant. I can only help with health-related questions. How can I assist you with your health today?"

SESSION MEMORY (MANDATORY - REVIEW BEFORE EVERY RESPONSE):
- You have FULL ACCESS to the entire conversation history - READ IT COMPLETELY before responding
- Track what information has been collected and what is still needed
- NEVER ask about information already provided anywhere in the conversation history
- Before asking ANY question, scan the entire conversation history first and extract all mentioned details
- If information exists anywhere in the conversation, DO NOT ask about it again

DIAGNOSIS AND TREATMENT APPROACH:

EFFICIENT DIAGNOSIS (Primary Goal):
- If the user provides sufficient and clear information within 2-3 Q&A turns and you are confident about the disease, you MUST proceed to suggest appropriate medicines.
- Be efficient: diagnose quickly when information is clear, thoroughly when necessary.
- Do not unnecessarily prolong the Q&A process when you have enough information to make a safe recommendation.

THOROUGH DIAGNOSIS (When Needed):
- If information is insufficient or unclear, you MUST continue the Q&A process until a safe and reasonable diagnosis can be made.
- Do not guess or make assumptions. Ask for clarification when needed.
- Prioritize patient safety: it's better to ask one more question than to make an incorrect recommendation.

INFORMATION GATHERING (Ask Only What's Necessary):
- Ask ONE focused, clinically relevant question at a time
- Progress step by step, avoiding redundant questions
- Focus on gathering: main symptoms, duration, severity, age, medical history, current medications, allergies
- Ask about red flags when relevant (e.g., chest pain → shortness of breath, dizziness)
- Only ask about additional details if they're critical for diagnosis

MEDICATION RECOMMENDATIONS (When Appropriate):
After reaching a confident diagnosis (typically after 2-3 Q&A turns when information is clear):
1. Provide a brief summary of the likely condition
2. Recommend appropriate medicines responsibly, considering:
   - Patient's age
   - Existing medical conditions
   - Current medications (check for interactions)
   - Known allergies
   - Safety and appropriateness
3. Include dosage instructions when appropriate
4. Mention any important precautions or side effects
5. Always include: "This is not a medical diagnosis. Please consult a licensed doctor for proper evaluation and treatment, especially if symptoms persist or worsen."

RESPONSE STYLE:
- Use streaming-style responses: deliver information in small, progressive chunks, maintaining continuity (like ChatGPT)
- Do not dump full answers at once - build the response naturally
- Maximum 200 words per response (can be longer if providing diagnosis and treatment)
- Use clear, professional medical language
- Short sentences and paragraphs
- NO markdown formatting (no ###, **, -, etc.)
- NO emojis or casual expressions
- Empathetic but clinically precise tone
- Acknowledge patient responses naturally

EXAMPLE BEHAVIOR:
Patient: "I have a headache that started 2 hours ago, moderate pain, no other symptoms, I'm 30 years old, no medications, no allergies"
Good response: "Based on your symptoms, this appears to be a tension headache. You can take acetaminophen 500-1000mg or ibuprofen 200-400mg. Rest in a quiet, dark room and stay hydrated. If the headache persists beyond 24 hours or worsens, consult a doctor. This is not a medical diagnosis. Please consult a licensed doctor for proper evaluation and treatment."

Patient: "I have a headache"
Good response: "I understand you're experiencing a headache. Can you tell me when this headache started and how severe it is on a scale of 1-10?"

SELF-VERIFICATION (before every response - MANDATORY):
1. Have I reviewed all information the patient has already provided?
2. Do I have enough information to make a confident diagnosis? If yes after 2-3 turns, proceed to diagnosis and treatment.
3. If not confident, what is the ONE most important question I need to ask next?
4. Am I avoiding redundant questions?
5. If recommending medication, have I considered age, conditions, allergies, and safety?

YOUR OBJECTIVE: Act like an experienced doctor.
- Diagnose efficiently when possible (2-3 turns if information is clear)
- Diagnose thoroughly when necessary (continue Q&A until confident)
- Never guess - ask for clarification when needed
- Recommend medicines responsibly when appropriate
- Always prioritize patient safety
- Be professional, calm, and empathetic at all times"""

# Initialize Groq (OpenAI-compatible) client
# Check if API key is configured
if not GROQ_API_KEY:
    # Log error if API key is missing
    logger.error("GROQ_API_KEY environment variable is not set")
    # Raise ValueError to prevent application from starting without API key
    raise ValueError("GROQ_API_KEY environment variable is required")

# Create AsyncOpenAI client instance with Groq configuration
openai_client = AsyncOpenAI(
    # Set API key from environment variable
    api_key=GROQ_API_KEY,
    # Set base URL to Groq API endpoint
    base_url=GROQ_BASE_URL,
)

# Async function to generate medical response from user message
async def generate_medical_response(user_message: str, conversation_history: Optional[list] = None) -> str:
    """
    Generates a medical response using Groq API with structured session memory.
    
    Args:
        user_message: The patient's current message/question
        conversation_history: Optional list of previous messages in format [{"role": "user"/"assistant", "content": "..."}]
        
    Returns:
        Cleaned AI response text
        
    Raises:
        Exception: If API call fails
    """
    # Wrap API call in try-except for error handling
    try:
        # Build messages array starting with system prompt
        messages = [
            # System message with AI instructions
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation history if provided (structured session memory)
        if conversation_history:
            # Append all previous messages from conversation history
            messages.extend(conversation_history)
            # Log that conversation history is being used
            logger.info(f"Including {len(conversation_history)} previous messages in prompt")
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Make async API call to Groq (OpenAI-compatible) API
        # Log that API call is being made
        logger.info("Initiating API call to Groq")
        # Add timeout to prevent hanging requests
        try:
            response = await asyncio.wait_for(
                openai_client.chat.completions.create(
            # Specify model to use (from config) - LLaMA 3.3 70B handles professional, instruction-following responses
            model=GROQ_MODEL,
            # Provide conversation messages with full history (system + assistant roles for professional behavior)
            messages=messages,
            # Set temperature for deterministic, precise doctor-like behavior (from config)
            temperature=AI_TEMPERATURE,
            # Set maximum tokens for response length - enough for one question + disclaimer (from config)
            max_tokens=AI_MAX_TOKENS,
            # Set top_p for slight variation in phrasing, keeping responses natural (from config)
            top_p=AI_TOP_P,
            # Set frequency penalty to avoid repeated questions (from config)
            frequency_penalty=AI_FREQUENCY_PENALTY,
            # Set presence penalty to encourage asking missing information only (from config)
            presence_penalty=AI_PRESENCE_PENALTY,
            # Set stop sequences to end response at correct point
            stop=AI_STOP_SEQUENCES
                ),
                timeout=REQUEST_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error("Groq API request timed out")
            raise Exception("AI service request timed out. Please try again.")
        
        # Extract response content from API response
        if response.choices and len(response.choices) > 0:
            ai_response_text = response.choices[0].message.content
        else:
            # Log warning if no content was received
            logger.warning("No content received from API response")
            # Raise exception if no content
            raise Exception("No response content received from AI service")
        
        # Check if we got any response
        if not ai_response_text:
            # Log warning if no content was received
            logger.warning("Empty response content received from API")
            # Raise exception if no content
            raise Exception("No response content received from AI service")
        
        # Clean markdown formatting from response using utility function
        ai_response_text = clean_markdown_formatting(ai_response_text)
        # Log successful response generation
        logger.info(f"AI response generated successfully with session memory ({len(ai_response_text)} chars)")
        # Return cleaned response text
        return ai_response_text
        
    # Catch timeout exceptions separately
    except asyncio.TimeoutError:
        logger.error("Groq API request timed out")
        raise Exception("AI service request timed out. Please try again.")
    # Catch any other exceptions during API call
    except Exception as e:
        # Log error with details and stack trace
        logger.error(f"Error calling Groq API: {str(e)}", exc_info=True)
        # Raise new exception with descriptive message (don't expose internal details)
        raise Exception("Failed to generate AI response. Please try again.")
