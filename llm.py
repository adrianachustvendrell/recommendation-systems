from huggingface_hub import InferenceClient
import time
from groq import Groq

client = Groq(
    api_key='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',
)

# Function to generate description for an item
def generate_description(item_name, retries=3, delay=5):
    for attempt in range(retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Escribeme una breve descripción en castellano de {item_name} en Valencia. Quiero tres frases en un párrafo, sin emoticonos ni negritas ni cursivas. Hazlo atractivo para turistas.",
                    }
                ],
                model="llama-3.3-70b-versatile",
            )

            return chat_completion.choices[0].message.content
        
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                raise e