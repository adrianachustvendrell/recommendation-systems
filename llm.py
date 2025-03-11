from huggingface_hub import InferenceClient
import time

# Initialize the client
client = InferenceClient(token="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")

# Function to generate description for an item
def generate_description(item_name, retries=3, delay=5):
    for attempt in range(retries):
        try:
            result = client.text_generation(
                model="microsoft/phi-4",
                prompt=f"Descríbeme en español {item_name} de Valencia en tres frases todo en un párrafo. Hazlo atractivo para turistas. Quiero que toda la descripción esté en un párrafo; no quiero ningún bullet point. También quiero que sea en castellano.",
            )
            return result['generated_text']
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                raise e