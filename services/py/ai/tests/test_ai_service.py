import json

import pytest
from common.errors import AppError


SAMPLE_QUESTIONS = [
    {
        "text": "What is Python known for?",
        "options": ["Complexity", "Simplicity", "Speed", "Verbosity"],
        "correct_index": 1,
        "explanation": "Python is known for its simplicity and readability.",
    },
    {
        "text": "What type of language is Python?",
        "options": ["Low-level", "Assembly", "High-level", "Machine"],
        "correct_index": 2,
        "explanation": "Python is a high-level programming language.",
    },
    {
        "text": "What paradigm does Python support?",
        "options": ["Only OOP", "Only functional", "Multiple paradigms", "None"],
        "correct_index": 2,
        "explanation": "Python supports multiple programming paradigms.",
    },
    {
        "text": "Is Python interpreted?",
        "options": ["Yes", "No", "Sometimes", "Only on Linux"],
        "correct_index": 0,
        "explanation": "Python is an interpreted language.",
    },
    {
        "text": "Who created Python?",
        "options": ["Linus Torvalds", "Guido van Rossum", "James Gosling", "Dennis Ritchie"],
        "correct_index": 1,
        "explanation": "Python was created by Guido van Rossum.",
    },
]


async def test_generate_quiz_cache_miss(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_quiz.return_value = None
    mock_llm.generate.return_value = (json.dumps(SAMPLE_QUESTIONS), 100, 200)

    result = await ai_service.generate_quiz(lesson_id, lesson_content)

    assert result.lesson_id == lesson_id
    assert len(result.questions) == 5
    assert result.cached is False
    assert result.model_used == "gemini-2.0-flash-lite"
    mock_cache.set_quiz.assert_called_once()


async def test_generate_quiz_cache_hit(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_quiz.return_value = json.dumps(SAMPLE_QUESTIONS)

    result = await ai_service.generate_quiz(lesson_id, lesson_content)

    assert result.lesson_id == lesson_id
    assert len(result.questions) == 5
    assert result.cached is True
    mock_llm.generate.assert_not_called()


async def test_generate_quiz_strips_markdown_fences(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_quiz.return_value = None
    wrapped = f"```json\n{json.dumps(SAMPLE_QUESTIONS)}\n```"
    mock_llm.generate.return_value = (wrapped, 100, 200)

    result = await ai_service.generate_quiz(lesson_id, lesson_content)

    assert len(result.questions) == 5
    assert result.cached is False


async def test_generate_quiz_invalid_json(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_quiz.return_value = None
    mock_llm.generate.return_value = ("not valid json", 100, 200)

    with pytest.raises(AppError) as exc_info:
        await ai_service.generate_quiz(lesson_id, lesson_content)
    assert exc_info.value.status_code == 502


async def test_generate_quiz_non_array_response(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_quiz.return_value = None
    mock_llm.generate.return_value = ('{"not": "an array"}', 100, 200)

    with pytest.raises(AppError) as exc_info:
        await ai_service.generate_quiz(lesson_id, lesson_content)
    assert exc_info.value.status_code == 502


async def test_generate_summary_cache_miss(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_summary.return_value = None
    mock_llm.generate.return_value = ("Python is a versatile language.", 50, 30)

    result = await ai_service.generate_summary(lesson_id, lesson_content)

    assert result.lesson_id == lesson_id
    assert result.summary == "Python is a versatile language."
    assert result.cached is False
    mock_cache.set_summary.assert_called_once()


async def test_generate_summary_cache_hit(ai_service, mock_llm, mock_cache, lesson_id, lesson_content):
    mock_cache.get_summary.return_value = "Cached summary text."

    result = await ai_service.generate_summary(lesson_id, lesson_content)

    assert result.summary == "Cached summary text."
    assert result.cached is True
    mock_llm.generate.assert_not_called()
