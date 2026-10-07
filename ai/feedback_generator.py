import os
import json
import cohere


# ============================================================
# COHERE CLIENT
# ============================================================

def get_cohere_client():
    """
    Create and return a Cohere client.

    Returns:
        Cohere client if API key exists.
        None if API key is not configured.
    """

    api_key = os.getenv("COHERE_API_KEY")

    if not api_key:
        return None

    return cohere.ClientV2(
        api_key=api_key
    )


# ============================================================
# FALLBACK FEEDBACK
# ============================================================

def generate_fallback_feedback(
    final_score,
    keyword_score,
    tfidf_score,
    semantic_score
):
    """
    Generate feedback without using the AI API.

    This is used when:
    - API key is missing
    - Internet is unavailable
    - Cohere API gives an error
    """

    strengths = []
    missing_concepts = []
    improvements = []

    # --------------------------------------------------------
    # STRENGTHS
    # --------------------------------------------------------

    if keyword_score >= 70:
        strengths.append(
            "You included important technical keywords related to the topic."
        )

    if tfidf_score >= 70:
        strengths.append(
            "Your answer has good textual similarity with the expected answer."
        )

    if semantic_score >= 70:
        strengths.append(
            "Your answer is semantically relevant to the question."
        )

    if final_score >= 80:
        strengths.append(
            "Your answer demonstrates a strong understanding of the concept."
        )

    if not strengths:
        strengths.append(
            "You made an attempt to answer the interview question."
        )

    # --------------------------------------------------------
    # MISSING CONCEPTS
    # --------------------------------------------------------

    if keyword_score < 70:
        missing_concepts.append(
            "Some important technical keywords are missing."
        )

    if tfidf_score < 70:
        missing_concepts.append(
            "The answer could include more relevant details from the expected concept."
        )

    if semantic_score < 70:
        missing_concepts.append(
            "The explanation could be more closely focused on the question."
        )

    if not missing_concepts:
        missing_concepts.append(
            "No major missing concepts were detected."
        )

    # --------------------------------------------------------
    # IMPROVEMENTS
    # --------------------------------------------------------

    if keyword_score < 70:
        improvements.append(
            "Include important technical terms and concepts in your answer."
        )

    if tfidf_score < 70:
        improvements.append(
            "Structure your answer clearly and include the main points."
        )

    if semantic_score < 70:
        improvements.append(
            "Explain the concept more clearly and directly."
        )

    if final_score >= 80:
        improvements.append(
            "Add a practical example to make your answer even stronger."
        )

    if not improvements:
        improvements.append(
            "Continue practicing technical interview questions."
        )

    # --------------------------------------------------------
    # OVERALL FEEDBACK
    # --------------------------------------------------------

    if final_score >= 80:

        overall_feedback = (
            "Excellent answer. You demonstrated a strong "
            "understanding of the concept."
        )

    elif final_score >= 60:

        overall_feedback = (
            "Good answer. You covered the main idea, "
            "but adding more technical details would improve your response."
        )

    elif final_score >= 40:

        overall_feedback = (
            "Partially correct answer. You have some understanding "
            "of the topic, but you should include more important concepts."
        )

    else:

        overall_feedback = (
            "The answer needs improvement. Review the concept "
            "and practice explaining it in your own words."
        )

    return {
        "strengths": strengths,
        "missing_concepts": missing_concepts,
        "improvement": improvements,
        "overall_feedback": overall_feedback
    }


# ============================================================
# AI FEEDBACK GENERATOR
# ============================================================

def generate_ai_feedback(
    question,
    expected_answer,
    candidate_answer,
    keyword_score,
    tfidf_score,
    semantic_score,
    final_score
):
    """
    Generate detailed feedback using Cohere AI.
    """

    client = get_cohere_client()

    # No API key
    if client is None:
        return None

    prompt = f"""
You are an experienced technical interviewer.

Analyze the candidate's answer.

INTERVIEW QUESTION:
{question}

EXPECTED ANSWER:
{expected_answer}

CANDIDATE ANSWER:
{candidate_answer}

NLP EVALUATION SCORES:

Keyword Score: {keyword_score}%
TF-IDF Score: {tfidf_score}%
Semantic Similarity Score: {semantic_score}%
Final Score: {final_score}%

Provide constructive interview feedback.

You must analyze:

1. What the candidate did well.
2. Which important concepts are missing or weak.
3. How the candidate can improve the answer.
4. A short overall evaluation.

Rules:

- Be constructive and educational.
- Do not insult or discourage the candidate.
- Do not invent skills or experience.
- Focus only on the given question and answer.
- Keep the feedback technically accurate.
- Keep each point concise.
- Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "missing_concepts": [
        "missing concept 1",
        "missing concept 2"
    ],
    "improvement": [
        "improvement 1",
        "improvement 2"
    ],
    "overall_feedback": "overall feedback"
}}

The fields strengths, missing_concepts and improvement
must be arrays of strings.

The field overall_feedback must be a string.
"""

    response_format = {
        "type": "json_object",
        "schema": {
            "type": "object",

            "properties": {

                "strengths": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "missing_concepts": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "improvement": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "overall_feedback": {
                    "type": "string"
                }
            },

            "required": [
                "strengths",
                "missing_concepts",
                "improvement",
                "overall_feedback"
            ]
        }
    }

    try:

        response = client.chat(

            model="command-a-plus-05-2026",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional technical "
                        "interviewer who provides accurate, "
                        "constructive and educational feedback."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            response_format=response_format,

            temperature=0
        )

        # ----------------------------------------------------
        # Extract AI response
        # ----------------------------------------------------

        response_text = (
            response
            .message
            .content[0]
            .text
        )

        # ----------------------------------------------------
        # Convert JSON text to Python dictionary
        # ----------------------------------------------------

        feedback = json.loads(
            response_text
        )

        # ----------------------------------------------------
        # Validate required fields
        # ----------------------------------------------------

        required_fields = [
            "strengths",
            "missing_concepts",
            "improvement",
            "overall_feedback"
        ]

        for field in required_fields:

            if field not in feedback:
                return None

        return feedback

    except Exception as error:

        print(
            "Cohere feedback error:",
            error
        )

        return None


# ============================================================
# MAIN FEEDBACK FUNCTION
# ============================================================

def generate_feedback(
    question,
    expected_answer,
    candidate_answer,
    keyword_score,
    tfidf_score,
    semantic_score,
    final_score
):
    """
    Generate AI feedback.

    First attempts to use Cohere.
    If Cohere is unavailable, uses fallback feedback.
    """

    ai_feedback = generate_ai_feedback(

        question,
        expected_answer,
        candidate_answer,

        keyword_score,
        tfidf_score,
        semantic_score,

        final_score
    )

    # --------------------------------------------------------
    # AI feedback available
    # --------------------------------------------------------

    if ai_feedback is not None:
        return ai_feedback

    # --------------------------------------------------------
    # Fallback feedback
    # --------------------------------------------------------

    return generate_fallback_feedback(

        final_score,

        keyword_score,

        tfidf_score,

        semantic_score
    )