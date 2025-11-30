from openai import OpenAI

class Summarizer:
    def __init__(self):
        self.client = OpenAI()

    def summarize(self, topic, documents, depth="Short"):
        joined = "\n\n".join(documents)

        prompt = f"""
You are a research analyst. Produce a structured research report.

TOPIC: {topic}

DEPTH: {depth}

SOURCE TEXT:
{joined}

OUTPUT FORMAT STRICTLY:
---
SUMMARY:
<150-250 word summary>

KEY INSIGHTS:
- bullet 1
- bullet 2
- bullet 3

PROS:
- pro 1
- pro 2

CONS:
- con 1
- con 2

CITATIONS:
- source 1
- source 2
---
"""

        resp = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You produce structured, factual research."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=900
        )

        return resp.choices[0].message.content


