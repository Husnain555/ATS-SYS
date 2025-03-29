import base64
import io
import os

from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GENAI_API_KEY"))


def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([input_text, pdf_content, prompt])
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        image_byte_arr = io.BytesIO()
        first_page.save(image_byte_arr, format='JPEG')
        image_byte_arr = image_byte_arr.getvalue()

        pdf_part = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(image_byte_arr).decode(),
        }
        return pdf_part
    else:
        raise FileNotFoundError("No file uploaded")

# ---------------------------
# Streamlit UI Starts Here
# ---------------------------

st.set_page_config(page_title="ATS Resume Analyzer")
st.header("ATS Resume Evaluation & Suggestions")

input_text = st.text_area("Job Description:", key="input")
job_field = st.text_input("Job Field (e.g., Marketing, Engineering, Medical):")
uploaded_file = st.file_uploader("Upload Resume (PDF Only):", type=["pdf"])

if uploaded_file:
    st.success("Resume uploaded successfully.")
else:
    st.warning("Upload your resume to continue.")

if not job_field:
    st.warning("Specify the job field for accurate analysis.")

# ----------- Optimized Prompts -----------

prompts = {
    "Analyze": f"""
        You are an expert HR and ATS specialist with deep knowledge of {job_field}.
        Evaluate the resume based on the provided job description.
        Your response must include:
        - A detailed assessment of resume strengths and weaknesses.
        - Critical gaps and missing elements.
        - Direct and actionable improvement recommendations.
        Format all suggestions as clear bullet points.
    """,

    "Recommend": f"""
        You are a professional career coach and resume reviewer specialized in {job_field}.
        Review the resume against the job description.
        Provide:
        - Concrete skill improvement recommendations.
        - Career development suggestions.
        - Steps to enhance the resume's chances of shortlisting.
        Keep the suggestions professional and ATS-focused.
    """,

    "Missing": f"""
        As an ATS and recruitment expert in {job_field}, your task is:
        - Identify essential keywords and skills present in the job description but missing from the resume.
        - Present the missing items as a bullet point list.
        Only include highly relevant and impactful keywords for ATS scoring.
    """,

    "Match": f"""
        Act as a strict ATS evaluator for {job_field}.
        Your task:
        - Compare the resume to the job description.
        - Calculate a realistic match percentage based on ATS standards.
        - Briefly justify the percentage.
        Be unbiased and professional.
    """
}

# ----------- Buttons -----------

if st.button("Analyze Resume"):
    if uploaded_file and job_field:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, prompts["Analyze"])
        st.subheader("Resume Analysis Report")
        st.write(response)
    else:
        st.error("Please upload a resume and specify the job field.")

if st.button("Recommend Improvements"):
    if uploaded_file and job_field:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, prompts["Recommend"])
        st.subheader("Skill Improvement Suggestions")
        st.write(response)
    else:
        st.error("Please upload a resume and specify the job field.")

if st.button("Find Missing Keywords"):
    if uploaded_file and job_field:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, prompts["Missing"])
        st.subheader("Missing Keywords")
        st.write(response)
    else:
        st.error("Please upload a resume and specify the job field.")

if st.button("Calculate ATS Match %"):
    if uploaded_file and job_field:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, prompts["Match"])
        st.subheader("ATS Match Percentage Report")
        st.write(response)
    else:
        st.error("Please upload a resume and specify the job field.")
