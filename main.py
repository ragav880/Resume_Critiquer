import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv
ATS_KEYWORDS = [
    "python", "java", "sql", "react", "machine learning",
    "data analysis", "api", "git", "docker", "cloud"
]


load_dotenv()
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")
st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

uploaded_file = st.file_uploader("Upload your resume(PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're taregtting (optional)")

analyze= st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")
   

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("The uploaded file is empty or could not be read.")
            st.stop()
        prompt = f"""
        Analyze the following resume and provide feedback.

        First, give an overall Resume Score out of 100.

        Then provide structured feedback under these sections:

        1. Resume Score (0–100) be strict if the role does not match the resume give low score
        2. Strengths
        3. Weaknesses
        4. Skills Improvement Suggestions
        5. Experience Bullet Improvements
        6. ATS Optimization Tips
        7. Specific suggestions for {job_role if job_role else 'general job roles'}

        Resume Content:
        {file_content}

        Be clear, concise, and practical.
        """
        client = Groq(api_key=GROQ_API_KEY)
        with st.spinner("Analyzing your resume with AI... ⏳"):
            response = client.chat.completions.create(
            
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000
            )
        
        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)
        resume_lower = file_content.lower()
        matched = [kw for kw in ATS_KEYWORDS if kw in resume_lower]
        missing = [kw for kw in ATS_KEYWORDS if kw not in resume_lower]

        st.markdown("### 📌 ATS Keyword Check")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ Found Keywords")
            if matched:
                for kw in matched:
                    st.markdown(f"- {kw.title()}")
            else:
                st.write("None")

        with col2:
            st.markdown("#### ❌ Missing Keywords")
            if missing:
                for kw in missing:
                    st.markdown(f"- {kw.title()}")
            else:
                st.write("None")
 

    
    except Exception as e:
        st.error(f"An error occured: {str(e)}")

        



