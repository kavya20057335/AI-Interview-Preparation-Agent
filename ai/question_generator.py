import os
import json

try:
    import cohere
except ImportError:
    cohere = None


# ============================================================
# FALLBACK QUESTION BANK
# ============================================================

FALLBACK_QUESTIONS = {

    "Python Developer": {

        "Easy": [
            {
                "question": "What is Python?",
                "expected_answer": (
                    "Python is a high-level, interpreted, "
                    "general-purpose programming language."
                )
            },
            {
                "question": "What is the difference between a list and a tuple?",
                "expected_answer": (
                    "A list is mutable, while a tuple is immutable. "
                    "Lists use square brackets and tuples use parentheses."
                )
            },
            {
                "question": "What are Python dictionaries?",
                "expected_answer": (
                    "A dictionary is a mutable collection that stores "
                    "data as key-value pairs."
                )
            },
            {
                "question": "What is a Python function?",
                "expected_answer": (
                    "A function is a reusable block of code that performs "
                    "a specific task and can accept parameters and return values."
                )
            },
            {
                "question": "What is the difference between == and is in Python?",
                "expected_answer": (
                    "The == operator compares values, while the is operator "
                    "checks whether two references point to the same object."
                )
            },
            {
                "question": "What are Python sets?",
                "expected_answer": (
                    "A set is an unordered collection of unique elements."
                )
            },
            {
                "question": "What is indentation in Python?",
                "expected_answer": (
                    "Indentation defines blocks of code in Python, such as "
                    "the body of functions, loops and conditional statements."
                )
            },
            {
                "question": "What is a variable in Python?",
                "expected_answer": (
                    "A variable is a name that refers to an object or value "
                    "stored in memory."
                )
            }
        ],

        "Medium": [
            {
                "question": "Explain mutable and immutable objects in Python with examples.",
                "expected_answer": (
                    "Mutable objects can be changed after creation, such as "
                    "lists and dictionaries. Immutable objects cannot be changed "
                    "after creation, such as tuples, strings and integers."
                )
            },
            {
                "question": "What is the difference between shallow copy and deep copy?",
                "expected_answer": (
                    "A shallow copy creates a new outer object but keeps references "
                    "to nested objects. A deep copy recursively copies nested objects."
                )
            },
            {
                "question": "Explain exception handling in Python.",
                "expected_answer": (
                    "Python handles exceptions using try, except, else and finally. "
                    "This allows programs to handle runtime errors gracefully."
                )
            },
            {
                "question": "What are list comprehensions in Python?",
                "expected_answer": (
                    "List comprehensions provide a concise way to create lists "
                    "using an expression and an optional condition."
                )
            },
            {
                "question": "Explain inheritance in Python.",
                "expected_answer": (
                    "Inheritance allows a class to acquire attributes and methods "
                    "from another class. It supports code reuse and object-oriented programming."
                )
            },
            {
                "question": "What is a lambda function in Python?",
                "expected_answer": (
                    "A lambda function is a small anonymous function defined using "
                    "the lambda keyword. It can take arguments and return an expression."
                )
            },
            {
                "question": "Explain the difference between *args and **kwargs.",
                "expected_answer": (
                    "*args allows a function to accept multiple positional arguments, "
                    "while **kwargs allows multiple keyword arguments."
                )
            },
            {
                "question": "What is a Python decorator?",
                "expected_answer": (
                    "A decorator is a function that modifies or extends the behavior "
                    "of another function without changing its source code."
                )
            }
        ],

        "Hard": [
            {
                "question": "Explain Python memory management and garbage collection.",
                "expected_answer": (
                    "Python manages memory automatically using private heaps, "
                    "reference counting and garbage collection to remove unreachable objects."
                )
            },
            {
                "question": "What is the Global Interpreter Lock in Python?",
                "expected_answer": (
                    "The GIL is a mechanism in CPython that allows only one thread "
                    "to execute Python bytecode at a time, affecting CPU-bound multithreading."
                )
            },
            {
                "question": "Explain generators and the yield keyword in Python.",
                "expected_answer": (
                    "Generators produce values lazily using yield. They maintain their "
                    "state between calls and are useful for memory-efficient iteration."
                )
            },
            {
                "question": "Explain Python context managers and the with statement.",
                "expected_answer": (
                    "Context managers manage resources and ensure cleanup. The with "
                    "statement automatically calls the context manager's enter and exit methods."
                )
            },
            {
                "question": "Explain method resolution order in Python.",
                "expected_answer": (
                    "Method Resolution Order determines the order in which Python "
                    "searches classes for methods, especially in multiple inheritance."
                )
            },
            {
                "question": "How does Python handle multiple inheritance?",
                "expected_answer": (
                    "Python supports multiple inheritance and uses the C3 linearization "
                    "algorithm to determine the method resolution order."
                )
            }
        ]
    },


    "Software Developer": {

        "Easy": [
            {
                "question": "What is object-oriented programming?",
                "expected_answer": (
                    "Object-oriented programming is a programming paradigm based on "
                    "objects, classes, inheritance, encapsulation and polymorphism."
                )
            },
            {
                "question": "What is a class?",
                "expected_answer": (
                    "A class is a blueprint for creating objects and defines their "
                    "attributes and methods."
                )
            },
            {
                "question": "What is an API?",
                "expected_answer": (
                    "An API is an interface that allows different software systems "
                    "to communicate with each other."
                )
            },
            {
                "question": "What is Git?",
                "expected_answer": (
                    "Git is a distributed version control system used to track "
                    "changes in source code."
                )
            },
            {
                "question": "What is a database?",
                "expected_answer": (
                    "A database is an organized collection of data that can be "
                    "stored, managed and retrieved efficiently."
                )
            }
        ],

        "Medium": [
            {
                "question": "Explain the difference between SQL and NoSQL databases.",
                "expected_answer": (
                    "SQL databases use structured tables and predefined schemas, "
                    "while NoSQL databases use flexible data models such as documents, "
                    "key-value pairs or graphs."
                )
            },
            {
                "question": "What is REST API architecture?",
                "expected_answer": (
                    "REST is an architectural style for web services that uses "
                    "HTTP methods and resources to enable communication between systems."
                )
            },
            {
                "question": "Explain the software development life cycle.",
                "expected_answer": (
                    "SDLC includes stages such as planning, requirements analysis, "
                    "design, development, testing, deployment and maintenance."
                )
            },
            {
                "question": "What is unit testing?",
                "expected_answer": (
                    "Unit testing tests individual functions or components of a "
                    "software application independently."
                )
            }
        ],

        "Hard": [
            {
                "question": "Explain microservices architecture.",
                "expected_answer": (
                    "Microservices architecture divides an application into small "
                    "independent services that communicate through APIs."
                )
            },
            {
                "question": "Explain database indexing and its advantages.",
                "expected_answer": (
                    "An index is a data structure that improves the speed of database "
                    "queries by allowing faster lookup of rows."
                )
            },
            {
                "question": "What is a design pattern? Explain the Singleton pattern.",
                "expected_answer": (
                    "A design pattern is a reusable solution to a common software design "
                    "problem. Singleton ensures that only one instance of a class exists."
                )
            }
        ]
    },


    "Data Analyst": {

        "Easy": [
            {
                "question": "What is data analysis?",
                "expected_answer": (
                    "Data analysis is the process of inspecting, cleaning, transforming "
                    "and interpreting data to discover useful information."
                )
            },
            {
                "question": "What is Pandas in Python?",
                "expected_answer": (
                    "Pandas is a Python library used for data manipulation and analysis "
                    "using structures such as Series and DataFrame."
                )
            },
            {
                "question": "What is a DataFrame?",
                "expected_answer": (
                    "A DataFrame is a two-dimensional labeled data structure in Pandas."
                )
            },
            {
                "question": "What is data visualization?",
                "expected_answer": (
                    "Data visualization represents data graphically using charts, "
                    "graphs and plots."
                )
            }
        ],

        "Medium": [
            {
                "question": "What is the difference between mean, median and mode?",
                "expected_answer": (
                    "Mean is the average value, median is the middle value when data "
                    "is ordered, and mode is the most frequently occurring value."
                )
            },
            {
                "question": "What is data cleaning?",
                "expected_answer": (
                    "Data cleaning involves handling missing values, duplicates, "
                    "inconsistent formats and incorrect data."
                )
            },
            {
                "question": "What is correlation?",
                "expected_answer": (
                    "Correlation measures the strength and direction of the relationship "
                    "between two variables."
                )
            },
            {
                "question": "Explain GROUP BY in SQL.",
                "expected_answer": (
                    "GROUP BY groups rows with the same values so aggregate functions "
                    "such as COUNT, SUM and AVG can be applied."
                )
            }
        ],

        "Hard": [
            {
                "question": "Explain normalization in databases.",
                "expected_answer": (
                    "Normalization organizes database tables to reduce redundancy "
                    "and improve data integrity."
                )
            },
            {
                "question": "What is hypothesis testing?",
                "expected_answer": (
                    "Hypothesis testing is a statistical method used to determine "
                    "whether there is enough evidence to reject a null hypothesis."
                )
            },
            {
                "question": "Explain the difference between supervised and unsupervised learning.",
                "expected_answer": (
                    "Supervised learning uses labeled data to learn a mapping from "
                    "inputs to outputs, while unsupervised learning discovers patterns "
                    "in unlabeled data."
                )
            }
        ]
    }
}


# ============================================================
# GET COHERE CLIENT
# ============================================================

def get_cohere_client():

    if cohere is None:
        return None

    api_key = os.getenv(
        "COHERE_API_KEY"
    )

    if not api_key:
        return None

    try:

        return cohere.ClientV2(
            api_key=api_key
        )

    except Exception:

        return None


# ============================================================
# FALLBACK QUESTION
# ============================================================

def get_fallback_question(
    role,
    difficulty,
    previous_questions=None
):

    previous_questions = (
        previous_questions or []
    )


    role_questions = FALLBACK_QUESTIONS.get(
        role,
        FALLBACK_QUESTIONS["Python Developer"]
    )


    questions = role_questions.get(
        difficulty,
        role_questions["Medium"]
    )


    # --------------------------------------------------------
    # FIND UNUSED QUESTION
    # --------------------------------------------------------

    for item in questions:

        question_text = item["question"]

        if question_text not in previous_questions:

            return {
                "question": question_text,
                "expected_answer": item["expected_answer"],
                "difficulty": difficulty
            }


    # --------------------------------------------------------
    # IF ALL QUESTIONS AT THIS LEVEL ARE USED,
    # SEARCH OTHER LEVELS
    # --------------------------------------------------------

    for level in [
        "Easy",
        "Medium",
        "Hard"
    ]:

        for item in role_questions.get(
            level,
            []
        ):

            question_text = item["question"]

            if question_text not in previous_questions:

                return {
                    "question": question_text,
                    "expected_answer": item["expected_answer"],
                    "difficulty": level
                }


    # --------------------------------------------------------
    # LAST RESORT
    # --------------------------------------------------------

    return {
        "question": (
            "Explain an important technical concept "
            "related to your role."
        ),
        "expected_answer": (
            "The candidate should clearly explain "
            "a relevant technical concept."
        ),
        "difficulty": difficulty
    }


# ============================================================
# COHERE AI QUESTION
# ============================================================

def generate_ai_question(
    role,
    difficulty,
    previous_score=None,
    previous_questions=None
):

    previous_questions = (
        previous_questions or []
    )


    client = get_cohere_client()


    if client is None:

        return None


    previous_text = "\n".join(
        f"- {question}"
        for question in previous_questions[-10:]
    )


    prompt = f"""
You are an AI technical interviewer.

Role:
{role}

Difficulty:
{difficulty}

Previous score:
{previous_score}

Previously asked questions:
{previous_text}

Generate ONE new technical interview question.

IMPORTANT:
- Do NOT repeat any previous question.
- The question must be different in wording and concept.
- The question must be relevant to the role.
- Match the requested difficulty.
- Provide a concise expected answer.
- Return ONLY valid JSON.

JSON format:

{{
    "question": "your question",
    "expected_answer": "your expected answer"
}}
"""


    try:

        response = client.chat(

            model="command-a-plus-05-2026",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            response_format={
                "type": "json_object"
            }
        )


        content = (
            response
            .message
            .content[0]
            .text
        )


        result = json.loads(
            content
        )


        question = result.get(
            "question",
            ""
        ).strip()


        expected_answer = result.get(
            "expected_answer",
            ""
        ).strip()


        if not question:

            return None


        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        question_lower = question.lower()


        for old_question in previous_questions:

            if question_lower == old_question.lower():

                return None


        return {
            "question": question,
            "expected_answer": expected_answer,
            "difficulty": difficulty
        }


    except Exception as error:

        print(
            "Cohere question generation error:",
            error
        )

        return None


# ============================================================
# RESUME-BASED QUESTION
# ============================================================

def generate_resume_question(
    role,
    difficulty,
    resume_text,
    previous_questions=None
):

    previous_questions = (
        previous_questions or []
    )


    if not resume_text.strip():

        return None


    client = get_cohere_client()


    if client is None:

        return None


    previous_text = "\n".join(
        f"- {question}"
        for question in previous_questions[-10:]
    )


    resume_text = resume_text[:12000]


    prompt = f"""
You are an AI technical interviewer.

Candidate role:
{role}

Difficulty:
{difficulty}

Resume:
{resume_text}

Previously asked questions:
{previous_text}

Generate ONE technical interview question based on
the candidate's resume.

The question can be based on:
- skills
- projects
- technologies
- internships
- experience

IMPORTANT:
- Do NOT repeat previous questions.
- Ask a different question.
- Make the question relevant to the resume.
- Match the requested difficulty.
- Return ONLY valid JSON.

JSON format:

{{
    "question": "your question",
    "expected_answer": "your expected answer"
}}
"""


    try:

        response = client.chat(

            model="command-a-plus-05-2026",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            response_format={
                "type": "json_object"
            }
        )


        content = (
            response
            .message
            .content[0]
            .text
        )


        result = json.loads(
            content
        )


        question = result.get(
            "question",
            ""
        ).strip()


        expected_answer = result.get(
            "expected_answer",
            ""
        ).strip()


        if not question:

            return None


        for old_question in previous_questions:

            if question.lower() == old_question.lower():

                return None


        return {
            "question": question,
            "expected_answer": expected_answer,
            "difficulty": difficulty
        }


    except Exception as error:

        print(
            "Resume question generation error:",
            error
        )

        return None


# ============================================================
# MAIN QUESTION GENERATOR
# ============================================================

def generate_question(
    role,
    difficulty,
    previous_score=None,
    resume_text=None,
    previous_questions=None
):

    previous_questions = (
        previous_questions or []
    )


    # --------------------------------------------------------
    # ADAPT DIFFICULTY
    # --------------------------------------------------------

    actual_difficulty = difficulty


    if previous_score is not None:

        if previous_score >= 80:

            if difficulty == "Easy":

                actual_difficulty = "Medium"

            elif difficulty == "Medium":

                actual_difficulty = "Hard"

            else:

                actual_difficulty = "Hard"


        elif previous_score < 60:

            if difficulty == "Hard":

                actual_difficulty = "Medium"

            elif difficulty == "Medium":

                actual_difficulty = "Easy"

            else:

                actual_difficulty = "Easy"


    # --------------------------------------------------------
    # TRY RESUME-BASED QUESTION
    # --------------------------------------------------------

    if resume_text:

        result = generate_resume_question(

            role=role,

            difficulty=actual_difficulty,

            resume_text=resume_text,

            previous_questions=previous_questions
        )


        if result:

            return result


    # --------------------------------------------------------
    # TRY COHERE GENERIC QUESTION
    # --------------------------------------------------------

    result = generate_ai_question(

        role=role,

        difficulty=actual_difficulty,

        previous_score=previous_score,

        previous_questions=previous_questions
    )


    if result:

        return result


    # --------------------------------------------------------
    # FALLBACK QUESTION
    # --------------------------------------------------------

    return get_fallback_question(

        role=role,

        difficulty=actual_difficulty,

        previous_questions=previous_questions
    )
