import re

from pypdf import PdfReader


# ============================================================
# COMMON TECHNICAL SKILLS
# ============================================================

TECHNICAL_SKILLS = [

    # Programming Languages
    "Python",
    "Java",
    "C",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "SQL",
    "R",

    # Web Technologies
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Node.js",
    "Django",
    "Flask",
    "FastAPI",
    "Streamlit",

    # Databases
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "Oracle",
    "Redis",

    # AI / Machine Learning
    "Artificial Intelligence",
    "AI",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",

    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "OpenCV",

    "YOLO",
    "YOLOv8",

    "Transformers",
    "Sentence Transformers",

    # Generative AI
    "Generative AI",
    "GenAI",
    "LangChain",
    "Cohere",
    "Hugging Face",

    # Data Analysis
    "Power BI",
    "Tableau",
    "Excel",
    "Matplotlib",
    "Seaborn",
    "Plotly",

    # DevOps / Cloud
    "Git",
    "GitHub",
    "Docker",
    "Jenkins",
    "Linux",

    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",

    # APIs / Software
    "REST API",
    "REST",
    "API",

    "Spring",
    "Spring Boot",

    # Other Tools
    "VS Code",
    "Jupyter",
    "Postman"
]


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_resume_text(uploaded_file):
    """
    Extract text from an uploaded PDF resume.

    Args:
        uploaded_file:
            Streamlit UploadedFile object.

    Returns:
        Extracted resume text as a string.
    """

    try:

        reader = PdfReader(uploaded_file)

        text = ""

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:

                page_text = page.extract_text()

                if page_text:

                    text += page_text
                    text += "\n"

            except Exception as page_error:

                print(
                    f"Error reading page {page_number}:",
                    page_error
                )

        # Remove excessive blank lines
        text = re.sub(
            r"\n\s*\n+",
            "\n\n",
            text
        )

        return text.strip()

    except Exception as error:

        print(
            "Resume parsing error:",
            error
        )

        return ""


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize resume text for easier processing.
    """

    if not text:

        return ""

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT TECHNICAL SKILLS
# ============================================================

def extract_skills(resume_text):
    """
    Detect technical skills mentioned in the resume.

    Returns:
        List of detected skills.
    """

    if not resume_text:

        return []

    normalized_text = normalize_text(
        resume_text
    )

    resume_lower = normalized_text.lower()

    found_skills = []

    for skill in TECHNICAL_SKILLS:

        skill_lower = skill.lower()

        # Special handling for short skills
        # such as C, R and AI.
        if skill_lower in [
            "c",
            "r",
            "ai"
        ]:

            pattern = (
                r"\b"
                + re.escape(skill_lower)
                + r"\b"
            )

            if re.search(
                pattern,
                resume_lower
            ):

                found_skills.append(
                    skill
                )

        else:

            if skill_lower in resume_lower:

                found_skills.append(
                    skill
                )

    return found_skills


# ============================================================
# FIND RESUME SECTION
# ============================================================

def extract_section(
    resume_text,
    section_names
):
    """
    Extract a particular section from a resume.

    Example:
        Projects
        Education
        Experience
    """

    if not resume_text:

        return ""

    text = normalize_text(
        resume_text
    )

    lines = text.splitlines()

    start_index = None
    end_index = None


    # --------------------------------------------------------
    # FIND SECTION START
    # --------------------------------------------------------

    for index, line in enumerate(lines):

        cleaned_line = (
            line
            .strip()
            .lower()
        )

        # Remove common punctuation
        cleaned_line = re.sub(
            r"[:\-]+$",
            "",
            cleaned_line
        ).strip()

        for section_name in section_names:

            if cleaned_line == section_name.lower():

                start_index = index

                break

        if start_index is not None:

            break


    if start_index is None:

        return ""


    # --------------------------------------------------------
    # POSSIBLE NEXT SECTIONS
    # --------------------------------------------------------

    next_sections = [

        "summary",
        "profile",
        "objective",

        "skills",
        "technical skills",
        "key skills",

        "projects",
        "project",
        "academic projects",
        "projects undertaken",

        "education",
        "educational qualification",
        "academic qualification",
        "academic background",

        "experience",
        "work experience",
        "professional experience",

        "internship",
        "internships",

        "certifications",
        "certification",
        "certificates",

        "achievements",
        "accomplishments",

        "publications",

        "contact",
        "contact details",

        "personal details",

        "references"
    ]


    # --------------------------------------------------------
    # FIND SECTION END
    # --------------------------------------------------------

    for index in range(
        start_index + 1,
        len(lines)
    ):

        cleaned_line = (
            lines[index]
            .strip()
            .lower()
        )

        cleaned_line = re.sub(
            r"[:\-]+$",
            "",
            cleaned_line
        ).strip()

        if cleaned_line in next_sections:

            end_index = index

            break


    if end_index is None:

        end_index = len(lines)


    # --------------------------------------------------------
    # BUILD SECTION TEXT
    # --------------------------------------------------------

    section_lines = lines[
        start_index + 1:end_index
    ]

    section_text = "\n".join(
        section_lines
    ).strip()

    return section_text


# ============================================================
# EXTRACT PROJECTS
# ============================================================

def extract_projects(resume_text):
    """
    Extract the Projects section.
    """

    return extract_section(
        resume_text,
        [
            "projects",
            "project",
            "academic projects",
            "projects undertaken"
        ]
    )


# ============================================================
# EXTRACT EDUCATION
# ============================================================

def extract_education(resume_text):
    """
    Extract the Education section.
    """

    return extract_section(
        resume_text,
        [
            "education",
            "educational qualification",
            "academic qualification",
            "academic background"
        ]
    )


# ============================================================
# EXTRACT EXPERIENCE
# ============================================================

def extract_experience(resume_text):
    """
    Extract work experience and internships.
    """

    experience = extract_section(
        resume_text,
        [
            "experience",
            "work experience",
            "professional experience"
        ]
    )

    internship = extract_section(
        resume_text,
        [
            "internship",
            "internships"
        ]
    )

    if experience and internship:

        return (
            "WORK EXPERIENCE\n"
            + experience
            + "\n\n"
            + "INTERNSHIPS\n"
            + internship
        )

    if experience:

        return experience

    if internship:

        return internship

    return ""


# ============================================================
# EXTRACT CERTIFICATIONS
# ============================================================

def extract_certifications(resume_text):
    """
    Extract certification information.
    """

    return extract_section(
        resume_text,
        [
            "certifications",
            "certification",
            "certificates"
        ]
    )


# ============================================================
# EXTRACT ACHIEVEMENTS
# ============================================================

def extract_achievements(resume_text):
    """
    Extract achievements section.
    """

    return extract_section(
        resume_text,
        [
            "achievements",
            "accomplishments"
        ]
    )


# ============================================================
# RESUME PREVIEW
# ============================================================

def get_resume_preview(
    resume_text,
    max_characters=2000
):
    """
    Return a shortened preview of resume text.
    """

    if not resume_text:

        return "No resume text found."


    if len(resume_text) <= max_characters:

        return resume_text


    return (
        resume_text[:max_characters]
        + "\n\n"
        + "...[Resume text truncated]..."
    )


# ============================================================
# RESUME STATISTICS
# ============================================================

def get_resume_length(resume_text):
    """
    Calculate basic resume statistics.

    Returns:
        Dictionary containing:
        - characters
        - words
        - lines
    """

    if not resume_text:

        return {
            "characters": 0,
            "words": 0,
            "lines": 0
        }


    words = resume_text.split()

    lines = [
        line
        for line in resume_text.splitlines()
        if line.strip()
    ]


    return {
        "characters": len(resume_text),
        "words": len(words),
        "lines": len(lines)
    }


# ============================================================
# COMPLETE RESUME ANALYSIS
# ============================================================

def analyze_resume(resume_text):
    """
    Perform complete resume analysis.

    Returns:
        Structured resume information.
    """

    if not resume_text:

        return {
            "skills": [],
            "projects": "",
            "education": "",
            "experience": "",
            "certifications": "",
            "achievements": "",
            "statistics": {
                "characters": 0,
                "words": 0,
                "lines": 0
            }
        }


    # --------------------------------------------------------
    # NORMALIZE TEXT
    # --------------------------------------------------------

    resume_text = normalize_text(
        resume_text
    )


    # --------------------------------------------------------
    # EXTRACT INFORMATION
    # --------------------------------------------------------

    skills = extract_skills(
        resume_text
    )

    projects = extract_projects(
        resume_text
    )

    education = extract_education(
        resume_text
    )

    experience = extract_experience(
        resume_text
    )

    certifications = extract_certifications(
        resume_text
    )

    achievements = extract_achievements(
        resume_text
    )

    statistics = get_resume_length(
        resume_text
    )


    # --------------------------------------------------------
    # RETURN STRUCTURED DATA
    # --------------------------------------------------------

    return {
        "skills": skills,
        "projects": projects,
        "education": education,
        "experience": experience,
        "certifications": certifications,
        "achievements": achievements,
        "statistics": statistics
    }


# ============================================================
# SIMPLE TEST FUNCTION
# ============================================================

def test_resume_parser():
    """
    Simple import test.
    """

    print(
        "Resume parser is working correctly."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_resume_parser()
