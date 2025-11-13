"""
Prompt templates for vocabulary recommendations.

This module contains LangChain prompt templates used to generate
personalized vocabulary recommendations for students.
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


# System message for the vocabulary educator assistant
SYSTEM_MESSAGE = """You are an expert vocabulary educator specializing in middle school education (grades 6-8).

Your role is to analyze student writing and provide personalized vocabulary recommendations that:
1. Match the student's current reading level and grade
2. Are appropriate for the subject matter
3. Represent a natural progression from words the student currently uses
4. Include clear context and examples
5. Explain why each word is a good fit for this particular student

You should be encouraging and specific in your recommendations, helping students expand their vocabulary in meaningful ways."""


# Prompt template for generating vocabulary recommendations
RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MESSAGE),
    ("human", """Analyze the following student information and generate personalized vocabulary recommendations.

**Student Profile:**
- Grade Level: {student_grade}
- Current Vocabulary Level: Grade {avg_grade_level}
- Subject: {subject}

**Student's Challenging Words:**
{challenging_words}

**Available Higher-Grade Words for Consideration:**
{available_words}

**Task:**
Generate {count} vocabulary word recommendations that would help this student improve their vocabulary.

For each recommendation, provide:
1. **word**: The recommended vocabulary word (must be from the available words list)
2. **recommended_grade**: The grade level of this word
3. **current_usage**: A simpler word or phrase the student might currently use instead
4. **definition**: Clear, student-friendly definition
5. **example_sentence**: An example sentence relevant to the subject and student's level
6. **rationale**: Why this word is appropriate for this student (1-2 sentences)

**Requirements:**
- Only recommend words from the provided available words list
- Ensure recommended words are at least 1 grade level above the student's current level
- Choose words that are appropriate for the subject matter
- Avoid overly difficult or obscure words
- Provide varied recommendations across different word types (nouns, verbs, adjectives)

**Output Format:**
Return ONLY a valid JSON array with this exact structure (no markdown formatting, no code blocks):

[
  {{
    "word": "example",
    "recommended_grade": 7,
    "current_usage": "show",
    "definition": "to explain or demonstrate something clearly",
    "example_sentence": "The scientist used a diagram to exemplify the water cycle.",
    "rationale": "Natural step up from 'show' that's commonly used in academic writing about science topics."
  }}
]
""")
])


# Simplified prompt for testing/debugging
SIMPLE_TEST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that responds concisely."),
    ("human", "Say 'Hello! Connection successful.' if you receive this message.")
])


# Prompt for analyzing vocabulary gaps in student text
VOCABULARY_GAP_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MESSAGE),
    ("human", """Analyze this student's writing to identify vocabulary improvement opportunities.

**Student Profile:**
- Grade Level: {student_grade}
- Current Vocabulary Level: Grade {avg_grade_level}
- Subject: {subject}

**Student's Text Excerpt:**
{text_excerpt}

**Task:**
Identify 5-10 places in the text where the student uses simple or repetitive vocabulary that could be replaced with more sophisticated alternatives.

For each opportunity, provide:
1. **original_phrase**: The exact phrase from the student's text
2. **suggested_replacement**: A more sophisticated word or phrase
3. **grade_level**: Grade level of the suggested replacement
4. **context**: Brief explanation of where this appears in the text
5. **improvement_note**: Why this replacement would improve the writing

**Output Format:**
Return ONLY a valid JSON array (no markdown formatting):

[
  {{
    "original_phrase": "very good",
    "suggested_replacement": "excellent",
    "grade_level": 7,
    "context": "describing the scientist's research",
    "improvement_note": "More precise and academic term for quality"
  }}
]
""")
])


# Prompt for subject-specific vocabulary recommendations
SUBJECT_SPECIFIC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MESSAGE),
    ("human", """Generate subject-specific vocabulary recommendations for this student.

**Student Profile:**
- Grade Level: {student_grade}
- Current Vocabulary Level: Grade {avg_grade_level}
- Subject Focus: {subject}

**Subject-Specific Context:**
{subject_context}

**Available Subject-Specific Words:**
{available_words}

**Task:**
Generate {count} vocabulary recommendations specifically for {subject} that:
- Are essential for understanding {subject} concepts
- Build on the student's current vocabulary level
- Include domain-specific terminology where appropriate
- Help the student express ideas more precisely in {subject}

Use the same output format as the general recommendations, but ensure all words and examples are highly relevant to {subject}.

**Output Format:**
Return ONLY a valid JSON array (no markdown formatting):

[
  {{
    "word": "analyze",
    "recommended_grade": 7,
    "current_usage": "look at",
    "definition": "to examine something carefully and in detail",
    "example_sentence": "Scientists analyze data to find patterns in their experiments.",
    "rationale": "Essential academic vocabulary for scientific inquiry and critical thinking."
  }}
]
""")
])


# Helper function to create custom prompts
def create_custom_recommendation_prompt(
    system_instructions: str,
    user_template: str
) -> ChatPromptTemplate:
    """
    Create a custom recommendation prompt with specific instructions.

    Args:
        system_instructions: Custom system message
        user_template: Custom user message template with variables

    Returns:
        ChatPromptTemplate: Configured prompt template
    """
    return ChatPromptTemplate.from_messages([
        ("system", system_instructions),
        ("human", user_template)
    ])


# Utility function to format word lists
def format_word_list(words: list[dict]) -> str:
    """
    Format a list of words for inclusion in prompts.

    Args:
        words: List of word dictionaries with 'word', 'grade', 'definition', etc.

    Returns:
        str: Formatted string representation of words

    Example:
        >>> words = [{"word": "analyze", "grade": 7, "definition": "examine in detail"}]
        >>> print(format_word_list(words))
        - analyze (Grade 7): examine in detail
    """
    if not words:
        return "No words available"

    formatted = []
    for word_data in words[:100]:  # Limit to avoid token overflow
        word = word_data.get("word", "unknown")
        grade = word_data.get("grade", "?")
        definition = word_data.get("definition", "")

        if definition:
            formatted.append(f"- {word} (Grade {grade}): {definition}")
        else:
            formatted.append(f"- {word} (Grade {grade})")

    return "\n".join(formatted)


def format_challenging_words(words: list[dict]) -> str:
    """
    Format challenging words for prompt inclusion.

    Args:
        words: List of challenging word dictionaries

    Returns:
        str: Formatted string of challenging words with context
    """
    if not words:
        return "No challenging words identified yet"

    formatted = []
    for word_data in words[:20]:  # Limit to most relevant
        word = word_data.get("word", "unknown")
        grade = word_data.get("grade_level", "?")
        usage_count = word_data.get("usage_count", 0)

        formatted.append(f"- {word} (Grade {grade}, used {usage_count} time(s))")

    return "\n".join(formatted)
