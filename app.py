import html
import re
import time
from datetime import datetime

import streamlit as st
from pypdf import PdfReader

from nlp.answer_evaluation import evaluate_answer
from ai.ai_interview import (
    ai_available,
    generate_question,
    generate_resume_questions,
    generate_adaptive_question,
    generate_adaptive_resume_question,
    generate_ai_feedback,
)
from voice.speech_to_text import (
    speech_to_text_available,
    transcribe_audio_bytes,
    get_supported_audio_types,
)

st.set_page_config(
    page_title="AI Interview Preparation Agent - Version 7",
    page_icon="🎤",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size:42px;font-weight:800;text-align:center;margin-bottom:5px;}
    .subtitle {text-align:center;color:#aaaaaa;font-size:18px;margin-bottom:30px;}
    .question-box {
        background:#dceeff !important;color:#111111 !important;
        border:2px solid #4a90e2 !important;border-radius:12px;
        padding:24px;margin-bottom:20px;font-size:21px;
        font-weight:700;line-height:1.6;
    }
    .question-box * {color:#111111 !important;background:transparent !important;}
    textarea {background:#ffffff !important;color:#111111 !important;border:2px solid #cccccc !important;}
    textarea::placeholder {color:#666666 !important;}
    .section-box {
        background:#f8f9fa !important;color:#111111 !important;
        padding:20px;border-radius:12px;border:1px solid #dddddd;
        margin-top:15px;margin-bottom:20px;
    }
    .section-box * {color:#111111 !important;}
    .score-card {
        background:#f8f9fa !important;color:#111111 !important;
        border:1px solid #dddddd;border-radius:12px;padding:20px;
        text-align:center;margin-bottom:10px;
    }
    .score-card * {color:#111111 !important;}
    .score-number {font-size:30px;font-weight:800;}
    .score-label {color:#666666 !important;font-size:15px;}
    </style>
    """,
    unsafe_allow_html=True,
)

questions = {
    "Python Developer": {
        "Easy": [
            {"question":"What is Python?","expected_answer":"Python is a high-level interpreted programming language known for its simple syntax and readability."},
            {"question":"What are lists in Python?","expected_answer":"A list is a mutable ordered collection in Python that can store multiple values and allows duplicate elements."},
            {"question":"What is a variable in Python?","expected_answer":"A variable is a name used to store or reference a value in Python."},
            {"question":"What is the difference between a list and a tuple?","expected_answer":"A list is mutable while a tuple is immutable. Lists use square brackets and tuples use parentheses."},
            {"question":"What are dictionaries in Python?","expected_answer":"A dictionary is a mutable collection that stores data as key-value pairs."},
        ],
        "Medium": [
            {"question":"Explain object-oriented programming in Python.","expected_answer":"Object-oriented programming is a programming paradigm based on classes and objects. Python supports inheritance, encapsulation, polymorphism and abstraction."},
            {"question":"What are decorators in Python?","expected_answer":"Decorators are functions that modify or extend the behavior of another function without changing its source code."},
            {"question":"Explain exception handling in Python.","expected_answer":"Exception handling in Python uses try, except, else and finally blocks to handle runtime errors."},
            {"question":"What is list comprehension?","expected_answer":"List comprehension is a concise way of creating a list using an expression and an iterable, optionally with a condition."},
            {"question":"What is the difference between shallow copy and deep copy?","expected_answer":"A shallow copy creates a new object but references nested objects, while a deep copy recursively creates copies of nested objects."},
        ],
        "Hard": [
            {"question":"Explain Python memory management.","expected_answer":"Python manages memory using a private heap, memory allocation mechanisms, reference counting and garbage collection."},
            {"question":"What is the Global Interpreter Lock in Python?","expected_answer":"The Global Interpreter Lock is a mechanism in CPython that allows only one thread to execute Python bytecode at a time."},
            {"question":"Explain generators and iterators in Python.","expected_answer":"An iterator is an object that implements the iterator protocol. A generator is a special type of iterator that produces values lazily using the yield keyword."},
            {"question":"How does garbage collection work in Python?","expected_answer":"Python uses reference counting and a cyclic garbage collector to identify and remove objects that are no longer needed."},
            {"question":"Explain multiprocessing and multithreading in Python.","expected_answer":"Multithreading uses multiple threads within a process, while multiprocessing uses multiple processes. Multiprocessing can execute CPU-bound tasks in parallel in CPython."},
        ],
    },
    "Software Developer": {
        "Easy": [
            {"question":"What is software engineering?","expected_answer":"Software engineering is the systematic approach to designing, developing, testing and maintaining software systems."},
            {"question":"What is an algorithm?","expected_answer":"An algorithm is a step-by-step procedure used to solve a problem or perform a computation."},
            {"question":"What is a data structure?","expected_answer":"A data structure is a way of organizing and storing data so that it can be accessed and modified efficiently."},
            {"question":"What is debugging?","expected_answer":"Debugging is the process of identifying, analyzing and fixing errors or bugs in a software program."},
            {"question":"What is version control?","expected_answer":"Version control is a system that tracks changes to files and allows developers to manage different versions of a project."},
        ],
        "Medium": [
            {"question":"Explain object-oriented programming.","expected_answer":"Object-oriented programming is a programming paradigm based on classes and objects and includes concepts such as inheritance, encapsulation, polymorphism and abstraction."},
            {"question":"What is the software development life cycle?","expected_answer":"The software development life cycle is a structured process including planning, analysis, design, development, testing, deployment and maintenance."},
            {"question":"What is the difference between Git and GitHub?","expected_answer":"Git is a distributed version control system, while GitHub is a cloud platform used to host Git repositories and collaborate."},
            {"question":"Explain REST API.","expected_answer":"A REST API is an application programming interface that follows REST principles and commonly uses HTTP methods such as GET, POST, PUT and DELETE."},
            {"question":"What is unit testing?","expected_answer":"Unit testing is the process of testing individual components or functions of a software application independently."},
        ],
        "Hard": [
            {"question":"Explain microservices architecture.","expected_answer":"Microservices architecture divides an application into small, independent services that communicate through APIs."},
            {"question":"What are design patterns?","expected_answer":"Design patterns are reusable solutions to commonly occurring software design problems."},
            {"question":"Explain scalability in software systems.","expected_answer":"Scalability is the ability of a software system to handle increasing workload by adding resources or improving architecture."},
            {"question":"What is system architecture?","expected_answer":"System architecture describes the structure, components, interfaces and interactions of a software system."},
            {"question":"Explain CI/CD.","expected_answer":"CI/CD represents continuous integration and continuous delivery or deployment, which automate software building, testing and release."},
        ],
    },
    "Data Analyst": {
        "Easy": [
            {"question":"What is data analysis?","expected_answer":"Data analysis is the process of inspecting, cleaning, transforming and interpreting data to discover useful information."},
            {"question":"What is a dataset?","expected_answer":"A dataset is a structured collection of related data."},
            {"question":"What is an average?","expected_answer":"Average usually refers to the arithmetic mean, calculated by dividing the sum of values by the number of values."},
            {"question":"What is data visualization?","expected_answer":"Data visualization is the graphical representation of data using charts, graphs and other visual elements."},
            {"question":"What is SQL?","expected_answer":"SQL is a language used to create, access, manage and manipulate data stored in relational databases."},
        ],
        "Medium": [
            {"question":"What is the difference between mean and median?","expected_answer":"Mean is the sum of values divided by the number of values, while median is the middle value when data is arranged in order."},
            {"question":"Explain SQL joins.","expected_answer":"SQL joins combine rows from two or more tables based on a related column. Common joins include inner, left, right and full joins."},
            {"question":"What is data cleaning?","expected_answer":"Data cleaning is the process of detecting and correcting missing, incorrect, duplicate or inconsistent data."},
            {"question":"What is correlation?","expected_answer":"Correlation measures the strength and direction of the relationship between two variables."},
            {"question":"What is an outlier?","expected_answer":"An outlier is a data point that is significantly different from other observations in a dataset."},
        ],
        "Hard": [
            {"question":"Explain hypothesis testing.","expected_answer":"Hypothesis testing is a statistical method used to determine whether there is enough evidence to support a claim about a population."},
            {"question":"What is regression analysis?","expected_answer":"Regression analysis is a statistical technique used to model the relationship between a dependent variable and one or more independent variables."},
            {"question":"Explain feature engineering.","expected_answer":"Feature engineering is the process of creating, transforming or selecting useful features from raw data for machine learning models."},
            {"question":"How would you handle missing data?","expected_answer":"Missing data can be handled by removing records, imputing values using statistical methods, or using algorithms that support missing values."},
            {"question":"Explain statistical significance.","expected_answer":"Statistical significance indicates whether an observed result is unlikely to have occurred by chance under a specified null hypothesis."},
        ],
    },
}

ROLE_SKILLS = {
    "Python Developer":["python","django","flask","fastapi","sql","git","github","rest api","api","pandas","numpy","machine learning","object oriented programming","oops"],
    "Software Developer":["python","java","c++","javascript","html","css","sql","git","github","rest api","api","object oriented programming","data structures","algorithms","testing"],
    "Data Analyst":["python","sql","excel","power bi","tableau","pandas","numpy","statistics","data visualization","machine learning","matplotlib"],
}
DIFFICULTIES = ["Easy","Medium","Hard"]
DIFFICULTY_VALUE = {"Easy":0,"Medium":1,"Hard":2}

defaults = {
    "started":False,"finished":False,"question_index":0,"answers":[],
    "name":"","role":"Python Developer","difficulty":"Easy","questions":[],
    "start_time":None,"end_time":None,"ai_mode":False,"resume_mode":False,
    "resume_text":"","resume_skills":[],"resume_projects":[],
    "resume_reference":"","adaptive_mode":True,"voice_mode":False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def reset_interview():
    for key, value in {
        "started":False,"finished":False,"question_index":0,"answers":[],
        "questions":[],"start_time":None,"end_time":None,"ai_mode":False,
        "resume_mode":False,"voice_mode":False,"resume_reference":""
    }.items():
        st.session_state[key] = value

def extract_resume_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        st.error(f"Could not read the PDF: {exc}")
        return ""

def find_resume_skills(text, role):
    lower = text.lower()
    found = [s for s in ROLE_SKILLS.get(role, []) if s.lower() in lower]
    missing = [s for s in ROLE_SKILLS.get(role, []) if s.lower() not in lower]
    return found, missing

def extract_possible_projects(text):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    keywords = ["project","projects","developed","built","application","system","website","platform"]
    found = []
    for line in lines:
        low = line.lower()
        if any(k in low for k in keywords) and 3 <= len(line.split()) <= 15 and line not in found:
            found.append(line)
    return found[:10]

def average_metric(key):
    if not st.session_state.answers:
        return 0.0
    return round(sum(x["score"].get(key,0) for x in st.session_state.answers)/len(st.session_state.answers),2)

def calculate_communication_score(answer):
    words = re.findall(r"\b[\w+#.-]+\b", answer)
    if not words:
        return 0.0
    word_score = min(len(words)/80,1.0)*55
    sentences = [s for s in re.split(r"[.!?]+",answer) if s.strip()]
    sentence_score = min(len(sentences)/5,1.0)*25
    structure_bonus = 20 if len(words)>=25 and len(sentences)>=2 else 10 if len(words)>=12 else 0
    return round(min(word_score+sentence_score+structure_bonus,100),2)

def topic_label(question):
    q = question.lower()
    if any(x in q for x in ["python","decorator","generator","interpreter","memory","garbage"]):
        return "Python"
    if any(x in q for x in ["sql","data","dataset","regression","correlation","hypothesis","statistics","outlier"]):
        return "Data / SQL / Statistics"
    if any(x in q for x in ["api","git","software","algorithm","architecture","microservices","testing","design pattern","scalability","ci/cd"]):
        return "Software Engineering"
    return "Technical Concept"

def next_difficulty(current, score):
    idx = DIFFICULTY_VALUE[current]
    if score >= 75 and idx < 2:
        return DIFFICULTIES[idx+1],"Increased difficulty because the score was 75 or higher."
    if score < 60 and idx > 0:
        return DIFFICULTIES[idx-1],"Decreased difficulty because the score was below 60."
    if score >= 75:
        return current,"Kept Hard difficulty because it is the highest level."
    if score < 60:
        return current,"Kept Easy difficulty because it is the lowest level."
    return current,"Kept the same difficulty because the score was between 60 and 74."

def built_in_question(role,difficulty,used):
    for item in questions[role][difficulty]:
        if item["question"] not in used:
            item = dict(item)
            item["topic"] = topic_label(item["question"])
            return item
    return None

def make_ai_question(role,difficulty,used,resume=False):
    try:
        if resume:
            result = generate_adaptive_resume_question(
                role,difficulty,st.session_state.resume_text,
                st.session_state.resume_skills,st.session_state.resume_projects,used)
        else:
            result = generate_adaptive_question(role,difficulty,used)
        if result and result.get("question") and result.get("expected_answer"):
            result.setdefault("topic",topic_label(result["question"]))
            return result
    except Exception:
        pass
    return None

def initial_ai_questions(role,difficulty,resume=False):
    generated=[]
    for _ in range(5):
        try:
            if resume:
                result=generate_resume_questions(
                    role,difficulty,st.session_state.resume_text,
                    st.session_state.resume_skills,st.session_state.resume_projects,
                    [x["question"] for x in generated])
            else:
                result=generate_question(role,difficulty,[x["question"] for x in generated])
        except Exception:
            result=None
        if not result:
            return []
        result.setdefault("topic",topic_label(result["question"]))
        generated.append(result)
    return generated

def show_score_card(label,value):
    st.markdown(
        f'<div class="score-card"><div class="score-number">{value:.2f}%</div><div class="score-label">{html.escape(label)}</div></div>',
        unsafe_allow_html=True)

def build_report():
    a=st.session_state.answers
    comm=round(sum(x.get("communication_score",0) for x in a)/len(a),2) if a else 0
    lines=[
        "AI INTERVIEW PREPARATION AGENT - VERSION 7",
        "="*55,f"Candidate: {st.session_state.name}",f"Role: {st.session_state.role}",
        f"Questions answered: {len(a)}",f"Overall Score: {average_metric('final_score')}%",
        f"Keyword Score: {average_metric('keyword_score')}%",
        f"TF-IDF Score: {average_metric('tfidf_score')}%",
        f"Semantic/Relevance Score: {average_metric('semantic_score')}%",
        f"Communication Score: {comm}%","",
        "QUESTION DETAILS","-"*55]
    for i,item in enumerate(a,1):
        lines += [
            f"{i}. {item['question']}",f"Input Mode: {item.get('input_mode','Text')}",
            f"Difficulty: {item.get('difficulty','')}",f"Topic: {item.get('topic','')}",
            f"Final Score: {item['score']['final_score']}%",
            f"Communication: {item.get('communication_score',0)}%",
            f"Answer: {item['answer']}",f"NLP Feedback: {item['score']['feedback']}",""]
    return "\n".join(lines)

# ============================================================
# DASHBOARD
# ============================================================
st.markdown('<div class="main-title">🎤 AI Interview Preparation Agent</div>',unsafe_allow_html=True)
st.markdown('<div class="subtitle">NLP • AI • Resume • Adaptive Interview • Voice • Performance Dashboard</div>',unsafe_allow_html=True)

if st.session_state.finished:
    answers=st.session_state.answers
    st.success("🎉 Interview Completed!")
    st.markdown("## 📊 Version 7 Interview Dashboard")

    overall=average_metric("final_score")
    technical=round(.60*average_metric("semantic_score")+.20*average_metric("keyword_score")+.20*average_metric("tfidf_score"),2)
    relevance=average_metric("semantic_score")
    concept=average_metric("keyword_score")
    communication=round(sum(x.get("communication_score",0) for x in answers)/len(answers),2) if answers else 0

    c1,c2,c3,c4,c5=st.columns(5)
    with c1: show_score_card("Overall",overall)
    with c2: show_score_card("Technical",technical)
    with c3: show_score_card("Communication*",communication)
    with c4: show_score_card("Relevance",relevance)
    with c5: show_score_card("Concept Coverage",concept)
    st.caption("*Communication is a simple text-structure heuristic, not a speech or grammar assessment.")

    st.markdown("### 📈 Performance by Question")
    if answers:
        import pandas as pd
        df=pd.DataFrame([{
            "Question":f"Q{i}","Final Score":x["score"]["final_score"],
            "Semantic":x["score"]["semantic_score"],
            "Communication":x.get("communication_score",0)}
            for i,x in enumerate(answers,1)]).set_index("Question")
        st.line_chart(df)

    st.markdown("### 🎤 Answer Input Modes")
    voice_count=sum(x.get("input_mode")=="Voice" for x in answers)
    text_count=len(answers)-voice_count
    st.write(f"Voice answers: **{voice_count}**  |  Text answers: **{text_count}**")

    st.markdown("### 📚 Difficulty Progression")
    if answers:
        import pandas as pd
        prog=pd.DataFrame([{
            "Question":f"Q{i}",
            "Difficulty Level":DIFFICULTY_VALUE.get(x.get("difficulty","Easy"),0)+1}
            for i,x in enumerate(answers,1)]).set_index("Question")
        st.bar_chart(prog)

    topic_scores={}
    for item in answers:
        topic_scores.setdefault(item.get("topic","Technical Concept"),[]).append(item["score"]["final_score"])

    st.markdown("### 🟢 Strong Areas")
    strong=[(t,sum(v)/len(v)) for t,v in topic_scores.items() if sum(v)/len(v)>=75]
    if strong:
        for t,a in strong: st.write(f"✓ **{t}** — {a:.2f}% average")
    else: st.info("No topic reached the 75% threshold.")

    st.markdown("### 🔴 Weak Areas")
    weak=[(t,sum(v)/len(v)) for t,v in topic_scores.items() if sum(v)/len(v)<60]
    if weak:
        for t,a in weak: st.write(f"• **{t}** — {a:.2f}% average")
    else: st.success("No topic fell below the 60% threshold.")

    st.markdown("### 🎯 Recommended Practice")
    rec=[]
    if concept<75: rec.append("Review core terminology and key concepts.")
    if relevance<75: rec.append("Practice answering the exact question first, then add technical details.")
    if communication<70: rec.append("Practice structured answers with a definition, explanation, example, and conclusion.")
    for t,_ in weak: rec.append(f"Revise {t}.")
    if not rec: rec.append("Continue practicing mixed-difficulty technical questions.")
    for x in rec: st.write("→ "+x)

    st.markdown("### 📝 Question-by-Question Report")
    for i,item in enumerate(answers,1):
        score=item["score"]
        with st.expander(f"Question {i}: {item['question']} — {score['final_score']:.2f}%"):
            st.write(f"**Input Mode:** {item.get('input_mode','Text')}")
            st.write(f"**Difficulty:** {item.get('difficulty','')}")
            st.write(f"**Topic:** {item.get('topic','Technical Concept')}")
            if item.get("resume_reference"): st.info("📄 Resume reference: "+item["resume_reference"])
            st.write("**Your Answer:**"); st.write(item["answer"])
            a,b,c,d=st.columns(4)
            a.metric("Keyword",f"{score['keyword_score']:.2f}%")
            b.metric("TF-IDF",f"{score['tfidf_score']:.2f}%")
            c.metric("Semantic",f"{score['semantic_score']:.2f}%")
            d.metric("Final",f"{score['final_score']:.2f}%")
            st.metric("Communication*",f"{item.get('communication_score',0):.2f}%")
            st.write("**NLP Feedback:** "+score["feedback"])
            if item.get("adaptation_reason"): st.write("**Adaptive Decision:** "+item["adaptation_reason"])
            if item.get("ai_feedback"):
                fb=item["ai_feedback"]
                st.markdown("**🤖 AI Feedback**")
                if fb.get("evaluation"): st.write(fb["evaluation"])
                if fb.get("strengths"): st.write("**Strengths:** "+"; ".join(fb["strengths"]))
                if fb.get("improvements"): st.write("**Improvements:** "+"; ".join(fb["improvements"]))
                if fb.get("ideal_answer"):
                    with st.expander("View AI Ideal Answer"): st.write(fb["ideal_answer"])
            with st.expander("View Expected Answer"): st.write(item["expected_answer"])

    st.download_button("📥 Download Interview Report",build_report(),
        file_name=f"{st.session_state.name or 'candidate'}_interview_report.txt",
        mime="text/plain",use_container_width=True)
    if st.button("🔄 Start New Interview",use_container_width=True):
        reset_interview(); st.rerun()
    st.stop()

# ============================================================
# ACTIVE INTERVIEW
# ============================================================
if st.session_state.started:
    # 🔙 Back to Interview Setup
    if st.button("⬅️ Back to Interview Setup"):
        reset_interview()
        st.rerun()

    idx=st.session_state.question_index
    total=len(st.session_state.questions)
    
    if idx>=total:
        st.session_state.finished=True
        st.session_state.end_time=datetime.now()
        st.rerun()

    q=st.session_state.questions[idx]
    qtext=q.get("question","")
    expected=q.get("expected_answer","")
    topic=q.get("topic",topic_label(qtext))
    resume_reference=q.get("resume_reference","")

    st.markdown(f"## 🎯 {st.session_state.role} Interview")
    st.progress(idx/total if total else 0,text=f"Question {idx+1} of {total}")
    c1,c2,c3=st.columns(3)
    c1.write(f"**Candidate:** {st.session_state.name}")
    c2.write(f"**Difficulty:** {st.session_state.difficulty}")
    c3.write(f"**Input:** {'🎤 Voice' if st.session_state.voice_mode else '⌨️ Text'}")

    if st.session_state.start_time:
        elapsed=int(time.time()-st.session_state.start_time)
        st.info(f"⏱️ Interview Time: {elapsed//60:02d}:{elapsed%60:02d}")

    st.markdown(
        f'<div class="question-box"><div style="color:#111111 !important;font-size:15px;margin-bottom:8px;">Topic: {html.escape(topic)}</div><div style="color:#111111 !important;font-size:21px;font-weight:700;">{html.escape(qtext)}</div></div>',
        unsafe_allow_html=True)
    if resume_reference: st.info("📄 This question is based on: "+resume_reference)

    # Voice mode and text mode are both available. Voice mode uses the browser
    # microphone recorder exposed by Streamlit's audio_input widget.
    if st.session_state.voice_mode:
        st.markdown("### 🎤 Speak Your Answer")
        st.caption("Record your answer using your microphone. After recording, the app converts the audio to text and evaluates that transcript.")
        audio_file=st.audio_input("Record your answer",key=f"audio_{idx}")
        typed_fallback=st.text_area(
            "⌨️ Text fallback (optional)",
            placeholder="If voice transcription is unavailable, you can type your answer here.",
            height=160,key=f"fallback_{idx}")
        submitted=st.button("Submit Voice Answer →",use_container_width=True,type="primary")
        if submitted:
            answer=""
            input_mode="Voice"
            if audio_file is not None:
                audio_bytes=audio_file.getvalue()
                with st.spinner("📝 Converting speech to text..."):
                    answer=transcribe_audio_bytes(audio_bytes)
                if not answer:
                    st.warning("Speech-to-text could not transcribe the recording.")
            if not answer and typed_fallback.strip():
                answer=typed_fallback.strip()
                input_mode="Text Fallback"
            if not answer:
                st.warning("Please record an answer or use the text fallback.")
                st.stop()
        else:
            st.stop()
    else:
        with st.form(key=f"answer_form_{idx}"):
            answer=st.text_area("✍️ Your Answer",placeholder="Type your technical answer here...",height=220,key=f"answer_text_{idx}")
            submitted=st.form_submit_button("Submit Answer →",use_container_width=True)
        input_mode="Text"
        if not submitted:
            st.stop()

    if not answer.strip():
        st.warning("Please provide an answer.")
        st.stop()

    score=evaluate_answer(answer,expected)
    communication_score=calculate_communication_score(answer)
    ai_feedback=None

    if st.session_state.ai_mode and ai_available():
        with st.spinner("🤖 AI is analyzing your answer..."):
            ai_feedback=generate_ai_feedback(
                role=st.session_state.role,question=qtext,
                candidate_answer=answer,expected_answer=expected,
                keyword_score=score["keyword_score"],tfidf_score=score["tfidf_score"],
                semantic_score=score["semantic_score"],final_score=score["final_score"])

    current_difficulty=st.session_state.difficulty
    new_difficulty,reason=next_difficulty(current_difficulty,score["final_score"])

    st.session_state.answers.append({
        "question":qtext,"answer":answer,"expected_answer":expected,
        "score":score,"ai_feedback":ai_feedback,"topic":topic,
        "resume_reference":resume_reference,"difficulty":current_difficulty,
        "communication_score":communication_score,"adaptation_reason":reason,
        "input_mode":input_mode,
    })
    st.session_state.question_index += 1

    if st.session_state.question_index>=5:
        st.session_state.finished=True
        st.session_state.end_time=datetime.now()
    else:
        st.session_state.difficulty=new_difficulty
        used=[x["question"] for x in st.session_state.answers]
        next_q=None
        if st.session_state.ai_mode and ai_available():
            with st.spinner("🤖 Preparing your adaptive next question..."):
                next_q=make_ai_question(st.session_state.role,new_difficulty,used,st.session_state.resume_mode)
        if next_q is None:
            next_q=built_in_question(st.session_state.role,new_difficulty,used)
        if next_q is None:
            for level in DIFFICULTIES:
                next_q=built_in_question(st.session_state.role,level,used)
                if next_q is not None:
                    st.session_state.difficulty=level
                    break
        if next_q is None:
            st.session_state.finished=True
            st.session_state.end_time=datetime.now()
        else:
            st.session_state.questions.append(next_q)
    st.rerun()

# ============================================================
# START PAGE
# ============================================================
tab1,tab2=st.tabs(["🎯 Interview","📄 Resume Analysis"])

with tab1:
    st.markdown("## Start Your Interview")
    name=st.text_input("👤 Candidate Name",placeholder="Enter your name")
    role=st.selectbox("💼 Select Role",list(questions.keys()))
    difficulty=st.selectbox("📈 Starting Difficulty",DIFFICULTIES)
    ai_mode=st.toggle("🤖 Enable AI Question Generator",value=False)
    adaptive_mode=st.toggle("🧠 Enable Adaptive Difficulty",value=True)
    voice_mode=st.toggle("🎤 Enable Voice Interview",value=False)

    if voice_mode:
        if speech_to_text_available():
            st.success("🎤 Voice input is available.")
        else:
            st.warning("Speech-to-text package is not available. Install SpeechRecognition and PyAudio, or use the text fallback.")

    if ai_mode:
        if ai_available(): st.success("🤖 AI is ready.")
        else: st.warning("AI mode requires OPENAI_API_KEY. The built-in question bank will be used if it is unavailable.")

    resume_interview=st.toggle("📄 Enable Resume-Based Interview",value=False)
    if resume_interview:
        if st.session_state.resume_text:
            st.success("Resume is ready for personalized questions.")
            if st.session_state.resume_skills:
                st.write("**Detected skills:** "+", ".join(st.session_state.resume_skills))
        else:
            st.warning("Analyze a resume in the Resume Analysis tab first.")

    if st.button("🚀 Start Interview",use_container_width=True,type="primary"):
        if not name.strip():
            st.warning("Please enter your name.")
        elif resume_interview and not st.session_state.resume_text:
            st.warning("Please analyze your resume before enabling Resume-Based Interview.")
        else:
            st.session_state.name=name.strip()
            st.session_state.role=role
            st.session_state.difficulty=difficulty
            st.session_state.ai_mode=ai_mode
            st.session_state.adaptive_mode=adaptive_mode
            st.session_state.voice_mode=voice_mode
            st.session_state.resume_mode=resume_interview
            st.session_state.question_index=0
            st.session_state.answers=[]
            generated=[]
            if ai_mode and ai_available():
                with st.spinner("🤖 Preparing your interview..."):
                    generated=initial_ai_questions(role,difficulty,resume_interview)
            if len(generated)==5:
                st.session_state.questions=generated
            else:
                first=built_in_question(role,difficulty,[])
                st.session_state.questions=[first] if first else []
                if not st.session_state.questions:
                    st.warning("Could not prepare a question.")
                    st.stop()
            st.session_state.start_time=time.time()
            st.session_state.end_time=None
            st.session_state.started=True
            st.session_state.finished=False
            st.rerun()

with tab2:
    st.markdown("## 📄 Resume Analysis")
    st.write("Upload your resume PDF to extract skills and project references for personalized interview questions.")
    resume_role=st.selectbox("Select Target Role",list(ROLE_SKILLS.keys()),key="resume_role")
    uploaded_resume=st.file_uploader("Upload Resume PDF",type=["pdf"])

    if uploaded_resume and st.button("🔍 Analyze Resume",use_container_width=True):
        resume_text=extract_resume_text(uploaded_resume)
        if resume_text:
            found,missing=find_resume_skills(resume_text,resume_role)
            projects=extract_possible_projects(resume_text)
            st.session_state.resume_text=resume_text
            st.session_state.resume_skills=found
            st.session_state.resume_projects=projects
            st.session_state.resume_reference=resume_role

            c1,c2,c3=st.columns(3)
            c1.metric("Words",len(resume_text.split()))
            c2.metric("Characters",len(resume_text))
            c3.metric("Matched Skills",len(found))
            st.markdown("### 🛠️ Skills Detected")
            st.success(", ".join(s.title() for s in found) if found else "No predefined role skills detected.")
            st.markdown("### 📌 Skills Not Detected")
            st.write(", ".join(s.title() for s in missing) if missing else "All predefined role skills detected.")
            st.markdown("### 📁 Possible Projects / Project References")
            if projects:
                for project in projects: st.write("• "+project)
            else: st.info("No obvious project references were detected.")
            with st.expander("📖 View Extracted Resume Text"):
                st.text_area("Resume Text",resume_text,height=400)
            st.success("Resume analysis completed.")
    elif not uploaded_resume:
        st.info("Upload a PDF resume to begin.")
