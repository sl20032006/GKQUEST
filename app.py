import streamlit as st

from google_sheets import load_questions
from question_manager import show_add_question
from quiz_engine import show_quiz


st.title("Quiz Ecosystem")
st.write("A personal quiz platform for UPSC, NDA and GK.")

page = st.radio("Go to", ["Quiz", "Add Question"], horizontal=True)

try:
	questions = load_questions()
	expected_columns = {
		"Question",
		"Option A",
		"Option B",
		"Option C",
		"Option D",
		"Answer",
		"Question Type",
		"Explanation",
	}
	if questions.empty:
		st.error("The quiz sheet is empty.")
	elif not expected_columns.issubset(questions.columns):
		st.error("The quiz sheet does not have the expected columns.")
	elif page == "Add Question":
		show_add_question(questions)
	else:
		show_quiz(questions)
except Exception as error:
	st.error(f"Could not load the quiz sheet: {error}")
