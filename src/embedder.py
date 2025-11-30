from openai import OpenAI

class OpenAIEmbedder:
    def __init__(self):
        self.client = OpenAI()

    def embed(self, text_list):
        resp = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text_list
        )
        return [item.embedding for item in resp.data]
