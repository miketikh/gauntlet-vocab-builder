#!/usr/bin/env python3
"""
Test script for LLM service and OpenAI integration.

This script tests:
1. OpenAI API connection
2. LangChain ChatOpenAI initialization
3. Simple prompt/response
4. Recommendation prompt template
5. Token usage tracking
6. Error handling

Usage:
    python3 scripts/test_llm.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.llm import (
    get_llm,
    test_llm_connection,
    estimate_cost,
    token_tracker,
    reset_llm,
)
from prompts.recommendations import (
    RECOMMENDATION_PROMPT,
    SIMPLE_TEST_PROMPT,
    format_word_list,
    format_challenging_words,
)
from models.recommendations import VocabularyRecommendation


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ {message}")


async def test_basic_connection():
    """Test 1: Basic OpenAI connection."""
    print_header("Test 1: Basic OpenAI Connection")

    try:
        result = await test_llm_connection()

        if result["success"]:
            print_success("OpenAI connection successful!")
            print_info(f"Model: {result['model']}")
            print_info(f"Response: {result['response']}")
            if result["tokens_used"]:
                print_info(f"Tokens used: {result['tokens_used']}")
            return True
        else:
            print_error(f"Connection failed: {result['error']}")
            return False

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False


async def test_simple_prompt():
    """Test 2: Simple prompt with LangChain."""
    print_header("Test 2: Simple Prompt Test")

    try:
        llm = get_llm()
        messages = SIMPLE_TEST_PROMPT.format_messages()

        start_time = time.time()
        response = await llm.ainvoke(messages)
        elapsed_time = time.time() - start_time

        print_success("Simple prompt test successful!")
        print_info(f"Response: {response.content}")
        print_info(f"Response time: {elapsed_time:.2f} seconds")

        # Track tokens if available
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            if prompt_tokens and completion_tokens:
                print_info(f"Prompt tokens: {prompt_tokens}")
                print_info(f"Completion tokens: {completion_tokens}")
                print_info(f"Total tokens: {prompt_tokens + completion_tokens}")

                # Track in global tracker
                token_tracker.add_usage(prompt_tokens, completion_tokens)

        return True

    except Exception as e:
        print_error(f"Simple prompt test failed: {str(e)}")
        return False


async def test_recommendation_prompt():
    """Test 3: Recommendation prompt template."""
    print_header("Test 3: Recommendation Prompt Test")

    try:
        # Sample data for testing
        student_grade = 7
        avg_grade_level = 6.5
        subject = "Science"

        challenging_words = format_challenging_words([
            {"word": "experiment", "grade_level": 8, "usage_count": 3},
            {"word": "hypothesis", "grade_level": 9, "usage_count": 2},
        ])

        available_words = format_word_list([
            {
                "word": "analyze",
                "grade": 7,
                "definition": "to examine something carefully and in detail"
            },
            {
                "word": "investigate",
                "grade": 7,
                "definition": "to carry out a systematic inquiry"
            },
            {
                "word": "interpret",
                "grade": 8,
                "definition": "to explain the meaning of information"
            },
            {
                "word": "synthesize",
                "grade": 9,
                "definition": "to combine separate elements into a whole"
            },
            {
                "word": "evaluate",
                "grade": 8,
                "definition": "to judge or assess the value or quality of something"
            },
        ])

        # Format the prompt
        messages = RECOMMENDATION_PROMPT.format_messages(
            student_grade=student_grade,
            avg_grade_level=avg_grade_level,
            subject=subject,
            challenging_words=challenging_words,
            available_words=available_words,
            count=3,
        )

        print_info("Sending recommendation prompt to LLM...")
        print_info(f"Student Grade: {student_grade}")
        print_info(f"Current Level: {avg_grade_level}")
        print_info(f"Subject: {subject}")
        print_info(f"Requesting: 3 recommendations")

        # Invoke LLM
        llm = get_llm()
        start_time = time.time()
        response = await llm.ainvoke(messages)
        elapsed_time = time.time() - start_time

        print_success("Recommendation prompt test successful!")
        print_info(f"Response time: {elapsed_time:.2f} seconds")

        # Parse and validate response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_text = response.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Remove first and last lines if they're code block markers
                if lines[0].startswith("```") and lines[-1].strip() == "```":
                    response_text = "\n".join(lines[1:-1])

            recommendations_data = json.loads(response_text)

            print_success(f"Parsed {len(recommendations_data)} recommendations")

            # Validate each recommendation
            for i, rec_data in enumerate(recommendations_data, 1):
                try:
                    rec = VocabularyRecommendation(**rec_data)
                    print(f"\n  Recommendation {i}:")
                    print(f"    Word: {rec.word} (Grade {rec.recommended_grade})")
                    print(f"    Replaces: {rec.current_usage}")
                    print(f"    Definition: {rec.definition}")
                    print(f"    Example: {rec.example_sentence}")
                    print(f"    Rationale: {rec.rationale}")
                except Exception as e:
                    print_error(f"  Recommendation {i} validation failed: {str(e)}")

        except json.JSONDecodeError as e:
            print_error(f"Failed to parse JSON response: {str(e)}")
            print_info("Raw response:")
            print(response.content)
            return False

        # Track tokens
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            if prompt_tokens and completion_tokens:
                print_info(f"\nToken usage:")
                print_info(f"  Prompt tokens: {prompt_tokens}")
                print_info(f"  Completion tokens: {completion_tokens}")
                print_info(f"  Total tokens: {prompt_tokens + completion_tokens}")

                # Track and estimate cost
                token_tracker.add_usage(prompt_tokens, completion_tokens)
                cost = estimate_cost(prompt_tokens, completion_tokens, "gpt-4o-mini")
                print_info(f"  Estimated cost: ${cost:.6f}")

        return True

    except Exception as e:
        print_error(f"Recommendation prompt test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test 4: Error handling."""
    print_header("Test 4: Error Handling")

    original_key = None
    try:
        # Test with invalid API key
        print_info("Testing with invalid API key...")
        original_key = os.environ.get("OPENAI_API_KEY")

        # Temporarily set invalid key
        os.environ["OPENAI_API_KEY"] = "sk-invalid-key-test"
        reset_llm()  # Reset singleton to use new key

        # This should fail with authentication error
        result = await test_llm_connection()
        print_info(f"Result success: {result['success']}")
        print_info(f"Result error: {result.get('error', 'None')}")
        if not result["success"]:
            print_success("Invalid API key properly handled")
            print_info(f"Error message: {result['error']}")
            success = True
        else:
            print_error("Invalid API key not properly handled - connection unexpectedly succeeded")
            success = False

        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
        reset_llm()  # Reset singleton to use original key

        return success

    except Exception as e:
        print_error(f"Error handling test failed: {str(e)}")
        # Make sure to restore key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
        reset_llm()
        return False


def print_summary():
    """Print summary of all tests."""
    print_header("Test Summary")

    stats = token_tracker.get_stats("gpt-4o-mini")

    print(f"Total requests: {stats['total_requests']}")
    print(f"Total tokens used: {stats['total_tokens']}")
    print(f"  - Prompt tokens: {stats['total_prompt_tokens']}")
    print(f"  - Completion tokens: {stats['total_completion_tokens']}")
    print(f"Estimated total cost: ${stats['estimated_cost_usd']:.6f}")

    print("\n" + "=" * 70)


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  LLM Service Test Suite")
    print("=" * 70)

    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print_error("OPENAI_API_KEY environment variable not set!")
        print_info("Please set it in your .env file")
        return 1

    # Run tests
    results = []

    # Test 1: Basic connection
    results.append(await test_basic_connection())

    # Test 2: Simple prompt
    if results[-1]:  # Only if previous test passed
        results.append(await test_simple_prompt())

    # Test 3: Recommendation prompt
    if results[-1]:  # Only if previous test passed
        results.append(await test_recommendation_prompt())

    # Test 4: Error handling
    results.append(await test_error_handling())

    # Print summary
    print_summary()

    # Overall result
    total_tests = len(results)
    passed_tests = sum(results)

    print(f"\nPassed: {passed_tests}/{total_tests} tests")

    if passed_tests == total_tests:
        print_success("All tests passed! ✓")
        return 0
    else:
        print_error(f"{total_tests - passed_tests} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
