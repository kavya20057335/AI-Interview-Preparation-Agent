import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# Load semantic model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def clean_text(text):
    """
    Basic text preprocessing.
    Converts text to lowercase and removes unnecessary characters.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def keyword_score(answer, expected_answer):
    """
    Calculates how many important words from the expected answer
    are present in the candidate answer.
    """

    answer_words = set(clean_text(answer).split())
    expected_words = set(clean_text(expected_answer).split())

    if not expected_words:
        return 0.0

    common_words = answer_words.intersection(expected_words)

    score = (len(common_words) / len(expected_words)) * 100

    return round(min(score, 100), 2)


def tfidf_score(answer, expected_answer):
    """
    Calculates TF-IDF cosine similarity between the candidate answer
    and the expected answer.
    """

    answer = clean_text(answer)
    expected_answer = clean_text(expected_answer)

    if not answer or not expected_answer:
        return 0.0

    vectorizer = TfidfVectorizer()

    try:
        vectors = vectorizer.fit_transform(
            [answer, expected_answer]
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(similarity * 100, 2)

    except ValueError:
        return 0.0


def semantic_score(answer, expected_answer):
    """
    Uses Sentence Transformers to calculate semantic similarity.
    """

    answer = clean_text(answer)
    expected_answer = clean_text(expected_answer)

    if not answer or not expected_answer:
        return 0.0

    embeddings = model.encode(
        [answer, expected_answer],
        convert_to_tensor=True
    )

    similarity = cosine_similarity(
        [embeddings[0].cpu().numpy()],
        [embeddings[1].cpu().numpy()]
    )[0][0]

    score = similarity * 100

    return round(max(0, min(score, 100)), 2)


def generate_feedback(final_score):
    """
    Generates feedback based on the final score.
    """

    if final_score >= 90:
        return (
            "Excellent answer! Your response is highly relevant, "
            "well structured, and semantically similar to the expected answer."
        )

    elif final_score >= 75:
        return (
            "Very good answer! Your response demonstrates good "
            "understanding of the concept with relevant information."
        )

    elif final_score >= 60:
        return (
            "Good answer! Your response contains the main concept, "
            "but adding more explanation and technical detail would improve it."
        )

    elif final_score >= 40:
        return (
            "Fair answer. Your response contains some relevant information, "
            "but it needs more explanation and detail."
        )

    else:
        return (
            "Needs improvement. Review the concept and try to provide "
            "a more complete and technically relevant answer."
        )


def evaluate_answer(answer, expected_answer):
    """
    Complete NLP evaluation.

    Weighting:
        Keyword      = 20%
        TF-IDF       = 20%
        Semantic     = 60%
    """

    keyword = keyword_score(
        answer,
        expected_answer
    )

    tfidf = tfidf_score(
        answer,
        expected_answer
    )

    semantic = semantic_score(
        answer,
        expected_answer
    )

    final_score = (
        keyword * 0.20
        + tfidf * 0.20
        + semantic * 0.60
    )

    final_score = round(final_score, 2)

    feedback = generate_feedback(
        final_score
    )

    return {
        "keyword_score": keyword,
        "tfidf_score": tfidf,
        "semantic_score": semantic,

        # Kept for compatibility with earlier code
        "similarity_score": semantic,

        "final_score": final_score,
        "feedback": feedback
    }
