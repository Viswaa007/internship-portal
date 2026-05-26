# =============================================================
# File: backend/ai/resume_analyzer.py
# =============================================================

import re
import os

# ---------------------------------------------------------------
# PDF Reader
# ---------------------------------------------------------------
try:
    import PyPDF2
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

# ---------------------------------------------------------------
# DOCX Reader
# ---------------------------------------------------------------
try:
    import docx
    DOCX_AVAILABLE = True
except:
    DOCX_AVAILABLE = False

# ---------------------------------------------------------------
# SKLEARN
# ---------------------------------------------------------------
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except:
    SKLEARN_AVAILABLE = False

# ---------------------------------------------------------------
# Skills Database
# ---------------------------------------------------------------
TECH_SKILLS = [
    "python", "java", "javascript", "html", "css",
    "react", "nodejs", "flask", "django",
    "mysql", "mongodb", "sql",
    "machine learning", "deep learning",
    "tensorflow", "pytorch",
    "data analysis", "pandas", "numpy",
    "git", "github", "docker",
    "aws", "azure",
    "communication", "leadership",
    "teamwork", "problem solving"
]


class ResumeAnalyzer:

    # =========================================================
    # Extract text from PDF
    # =========================================================
    def extract_text_from_pdf(self, file_path):

        if not PDF_AVAILABLE:
            return ""

        text = ""

        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                for page in reader.pages:
                    extracted = page.extract_text()

                    if extracted:
                        text += extracted + "\n"

        except Exception as e:
            print("PDF Error:", e)

        return text

    # =========================================================
    # Extract text from DOCX
    # =========================================================
    def extract_text_from_docx(self, file_path):

        if not DOCX_AVAILABLE:
            return ""

        text = ""

        try:
            document = docx.Document(file_path)

            for para in document.paragraphs:
                text += para.text + "\n"

        except Exception as e:
            print("DOCX Error:", e)

        return text

    # =========================================================
    # Extract Text
    # =========================================================
    def extract_text(self, file_path):

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)

        elif ext == ".docx":
            return self.extract_text_from_docx(file_path)

        return ""

    # =========================================================
    # Clean Text
    # =========================================================
    def clean_text(self, text):

        text = text.lower()

        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    # =========================================================
    # Extract Skills
    # =========================================================
    def extract_skills(self, text):

        text = text.lower()

        found_skills = []

        for skill in TECH_SKILLS:
            if skill.lower() in text:
                found_skills.append(skill)

        return list(set(found_skills))

    # =========================================================
    # Match Score
    # =========================================================
    def calculate_match_score(self, resume_text, required_skills):

        if not required_skills:
            return 50

        resume_text = resume_text.lower()

        matched = 0

        for skill in required_skills:

            if skill.lower() in resume_text:
                matched += 1

        score = (matched / len(required_skills)) * 100

        return round(score, 2)

    # =========================================================
    # TFIDF Score
    # =========================================================
    def calculate_similarity(self, resume_text, skills_text):

        if not SKLEARN_AVAILABLE:
            return 0

        try:
            vectorizer = TfidfVectorizer()

            vectors = vectorizer.fit_transform([
                resume_text,
                skills_text
            ])

            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

            return round(similarity * 100, 2)

        except:
            return 0

    # =========================================================
    # Main Analyze Function
    # =========================================================
    def analyze(self, file_path, required_skills_str=""):

        # -----------------------------------------------------
        # Extract text
        # -----------------------------------------------------
        resume_text = self.extract_text(file_path)

        if not resume_text or len(resume_text) < 20:

            return {
                "match_score": 0,
                "recommendation": "Resume content not readable",
                "grade": "D",
                "extracted_skills": [],
                "matched_skills": [],
                "missing_skills": []
            }

        cleaned_text = self.clean_text(resume_text)

        # -----------------------------------------------------
        # Extract Skills
        # -----------------------------------------------------
        extracted_skills = self.extract_skills(cleaned_text)

        # -----------------------------------------------------
        # Required Skills
        # -----------------------------------------------------
        required_skills = []

        if required_skills_str:

            required_skills = [
                s.strip().lower()
                for s in required_skills_str.split(",")
                if s.strip()
            ]

        # -----------------------------------------------------
        # Match Skills
        # -----------------------------------------------------
        matched_skills = []

        for skill in required_skills:
            if skill in extracted_skills:
                matched_skills.append(skill)

        missing_skills = [
            s for s in required_skills
            if s not in matched_skills
        ]

        # -----------------------------------------------------
        # Scores
        # -----------------------------------------------------
        skill_score = self.calculate_match_score(
            cleaned_text,
            required_skills
        )

        similarity_score = self.calculate_similarity(
            cleaned_text,
            " ".join(required_skills)
        )

        final_score = round(
            (skill_score * 0.7) +
            (similarity_score * 0.3),
            2
        )

        # -----------------------------------------------------
        # Recommendation
        # -----------------------------------------------------
        if final_score >= 80:
            recommendation = "Strongly Recommended"
            grade = "A"

        elif final_score >= 60:
            recommendation = "Recommended"
            grade = "B"

        elif final_score >= 40:
            recommendation = "Average Match"
            grade = "C"

        else:
            recommendation = "Not Recommended"
            grade = "D"

        # -----------------------------------------------------
        # Return Result
        # -----------------------------------------------------
        return {

            "match_score": final_score,

            "grade": grade,

            "recommendation": recommendation,

            "extracted_skills": extracted_skills,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "resume_length": len(resume_text),

            "total_skills_found": len(extracted_skills)
        }


# ---------------------------------------------------------------
# Test the module directly
# ---------------------------------------------------------------
if __name__ == '__main__':
    print("Resume Analyzer Test")
    print("=" * 50)
    analyzer = ResumeAnalyzer()

    # Test with a dummy text (no actual PDF needed)
    test_text = """
    John Doe | john@example.com | +91 9876543210
    Skills: Python, Machine Learning, TensorFlow, Flask, MySQL, Git, Pandas, NumPy
    Education: B.Tech Computer Science, Anna University, CGPA: 8.5
    Projects: Movie Recommendation System using collaborative filtering
    Experience: Python Intern at ABC Corp for 3 months
    """

    # Simulate PDF extraction
    analyzer.extract_text_from_pdf = lambda x: test_text  # Mock for testing

    result = analyzer.analyze('dummy.pdf', 'Python, Machine Learning, Flask, SQL')
    print(f"Match Score: {result['match_score']}%")
    print(f"Extracted Skills: {result['extracted_skills']}")
    print(f"Matched Skills: {result['matched_skills']}")
    print(f"Missing Skills: {result['missing_skills']}")
    print(f"Recommendation: {result['recommendation']}")
