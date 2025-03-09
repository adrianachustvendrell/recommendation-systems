from huggingface_hub import InferenceClient

# Initialize the client
client = InferenceClient(token="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")

# Function to generate description for an item
def generate_description(item_name):
    result = client.text_generation(
        model="google/gemma-2-2b-it",
        prompt=f"Descríbeme en español {item_name} de Valencia en tres frases todo en un párrafo. Hazlo atractivo para turistas. Quiero que toda la descripción esté en un párrafo; no quiero ningún bullet point. También quiero que sea en castellano.",
    )
    return result