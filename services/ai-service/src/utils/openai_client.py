import os
from typing import List, Dict, Optional
import openai
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def moderate_content(text: str) -> Dict:
    """
    Check content for inappropriate content using OpenAI's moderation API.
    """
    try:
        response = await client.moderations.create(input=text)
        return response.results[0]
    except Exception as e:
        # Log error and return safe default
        print(f"Moderation API error: {e}")
        return {"flagged": False, "categories": {}, "category_scores": {}}

async def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 150
) -> Optional[str]:
    """
    Generate chat completion using OpenAI's GPT model.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4",  # or gpt-3.5-turbo based on requirements
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        # Log error and return None
        print(f"Chat completion API error: {e}")
        return None

async def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment of user messages to gauge satisfaction.
    """
    try:
        messages = [
            {"role": "system", "content": "Analyze the sentiment of the following text and return a JSON with 'sentiment' (positive/negative/neutral) and 'score' (0-1)."},
            {"role": "user", "content": text}
        ]
        response = await chat_completion(messages)
        return eval(response) if response else {"sentiment": "neutral", "score": 0.5}
    except Exception as e:
        # Log error and return neutral sentiment
        print(f"Sentiment analysis error: {e}")
        return {"sentiment": "neutral", "score": 0.5}
