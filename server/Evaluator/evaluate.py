import ollama

class LLAMA3Evaluator:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def evaluate(self, assignment_text: str, topic: str) -> dict:
        prompt = f"""
You are an expert academic evaluator.

A student has submitted the following assignment:

\"\"\"{assignment_text}\"\"\"

Evaluate the assignment based on:
- Relevance to the topic: {topic}
- Grammar and spelling
- Structure (introduction, body, conclusion)
- Originality and clarity

For each criterion, provide:
- A score out of 25
- A short comment

Then, provide:
- A total score out of 100
- 3 short and helpful general feedback points

Format strictly like this:
Relevance: <score>/25 - <comment>
Grammar and Spelling: <score>/25 - <comment>
Structure: <score>/25 - <comment>
Originality and Clarity: <score>/25 - <comment>
Total Score: <score>/100
Feedback:
- <feedback 1>
- <feedback 2>
- <feedback 3>
"""
        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "evaluation_details": response['message']['content']
        }

