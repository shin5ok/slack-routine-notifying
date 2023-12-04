import vertexai
from vertexai.language_models import TextGenerationModel

vertexai.init(project="shingo-ar-test23111701", location="us-central1")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison")
response = model.predict(
    """
����ˤ���
    """,
    **parameters
)
print(f"Response from Model: {response.text}")

