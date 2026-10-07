from nlp.answer_evaluation import evaluate_answer


expected_answer = """
Python is a high-level interpreted programming language.
It is easy to learn and supports object-oriented programming.
"""


candidate_answer = """
Python is a high-level programming language.
It is interpreted, easy to learn and supports
object-oriented programming.
"""


result = evaluate_answer(
    expected_answer,
    candidate_answer
)


print("NLP Answer Evaluation")
print("----------------------")

print("Keyword Score:", result["keyword_score"])

print("TF-IDF Score:", result["tfidf_score"])

print("Semantic Score:", result["semantic_score"])

print("Final Score:", result["final_score"])

print("Feedback:", result["feedback"])