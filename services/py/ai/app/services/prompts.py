QUIZ_PROMPT_TEMPLATE = """You are an educational quiz generator. Based on the lesson content below, generate exactly 5 multiple-choice questions.

IMPORTANT: Return ONLY a valid JSON array with no additional text, markdown, or code blocks.

Each question must have this exact JSON structure:
{{"text": "question text", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "why this is correct"}}

Rules:
- Generate exactly 5 questions
- Each question has exactly 4 options
- correct_index is 0-based (0, 1, 2, or 3)
- Questions should test understanding, not memorization
- Explanation should be concise (1-2 sentences)

Lesson content:
{content}"""

SUMMARY_PROMPT_TEMPLATE = """You are an educational content summarizer. Summarize the lesson content below in 3-5 concise paragraphs.

Rules:
- Focus on key concepts and takeaways
- Use clear, student-friendly language
- Include any important definitions or formulas
- Return plain text only, no markdown headers or formatting

Lesson content:
{content}"""
