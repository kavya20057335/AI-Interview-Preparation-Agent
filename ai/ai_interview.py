import json
import os
from openai import OpenAI

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def ai_available():
    return bool(os.getenv("OPENAI_API_KEY"))

def clean_json_response(output):
    output=(output or "").strip()
    if output.startswith("```json"): output=output[7:]
    elif output.startswith("```"): output=output[3:]
    if output.endswith("```"): output=output[:-3]
    return output.strip()

def call_ai(prompt):
    client=get_client()
    if client is None:
        return None
    try:
        response=client.responses.create(model=DEFAULT_MODEL,input=prompt)
        return json.loads(clean_json_response(response.output_text))
    except Exception as exc:
        print(f"AI request error: {exc}")
        return None

def _question_prompt(role,difficulty,previous_questions):
    previous="\n".join(f"- {q}" for q in previous_questions[-10:])
    return f"""
Generate one technical interview question for a {role} candidate.
Difficulty: {difficulty}.
Avoid repeating:
{previous or "- none"}

Return ONLY valid JSON:
{{
  "question": "...",
  "expected_answer": "...",
  "topic": "..."
}}
"""

def generate_question(role,difficulty,previous_questions=None):
    return call_ai(_question_prompt(role,difficulty,previous_questions or []))

def _resume_prompt(role,difficulty,resume_text,skills,projects,previous_questions):
    previous="\n".join(f"- {q}" for q in previous_questions[-10:])
    return f"""
Generate one personalized technical interview question for a {role} candidate.
Difficulty: {difficulty}.

Detected resume skills:
{", ".join(skills) if skills else "None"}

Possible project references:
{", ".join(projects) if projects else "None"}

Resume:
{resume_text[:12000]}

Avoid repeating:
{previous or "- none"}

Return ONLY valid JSON:
{{
  "question": "...",
  "expected_answer": "...",
  "topic": "...",
  "resume_reference": "..."
}}
"""

def generate_resume_questions(role,difficulty,resume_text,skills,projects,previous_questions=None):
    return call_ai(_resume_prompt(role,difficulty,resume_text,skills,projects,previous_questions or []))

def generate_adaptive_question(role,difficulty,previous_questions=None):
    return call_ai(_question_prompt(role,difficulty,previous_questions or []))

def generate_adaptive_resume_question(role,difficulty,resume_text,skills,projects,previous_questions=None):
    return call_ai(_resume_prompt(role,difficulty,resume_text,skills,projects,previous_questions or []))

def generate_ai_feedback(role,question,candidate_answer,expected_answer,
                         keyword_score,tfidf_score,semantic_score,final_score):
    prompt=f"""
Evaluate this technical interview answer.

Role: {role}
Question: {question}
Candidate answer: {candidate_answer}
Expected answer: {expected_answer}

NLP scores:
Keyword: {keyword_score}
TF-IDF: {tfidf_score}
Semantic: {semantic_score}
Final: {final_score}

Return ONLY valid JSON:
{{
  "evaluation": "short factual evaluation",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "ideal_answer": "concise model answer"
}}
"""
    return call_ai(prompt)
