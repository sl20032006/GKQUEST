import streamlit as st

from google_sheets import load_questions
from question_manager import show_add_question
from quiz_engine import clear_quiz_state, show_quiz


def go_to_main_menu():
	clear_quiz_state()
	st.session_state.page = "Main Menu"


if "page" not in st.session_state:
	st.session_state.page = "Main Menu"


st.title("Quiz Ecosystem")
st.write("A personal quiz platform2 for UPSC, NDA and GK.")

if st.session_state.page == "Main Menu":
	st.header("Main Menu")
	st.write("Choose what you would like to do2:")
	quiz_clicked = st.button("GK Quest", use_container_width=True, key="main_menu_quiz")
	add_clicked = st.button("Add a Question", use_container_width=True, key="main_menu_add")
	if quiz_clicked:
		clear_quiz_state()
		st.session_state.page = "GK Quest"
		st.rerun()
	if add_clicked:
		st.session_state.page = "Add Question"
		st.rerun()

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
	if not expected_columns.issubset(questions.columns):
		st.error("The quiz sheet does not have the expected columns.")
	elif st.session_state.page == "Add Question":
		show_add_question(questions)
		if st.button("Back to Main Menu", key="back_from_add"):
			go_to_main_menu()
			st.rerun()
	elif st.session_state.page == "GK Quest":
		if questions.empty:
			st.error("The quiz sheet is empty. Add questions before starting a quiz.")
		else:
			show_quiz(questions)
		if st.button("Back to Main Menu", key="back_from_quiz"):
			go_to_main_menu()
			st.rerun()
	else:
		if questions.empty:
			st.info("The quiz sheet is empty. You can still add a question.")
		else:
			st.info("Choose an option from the main menu to continue.")
except Exception as error:
	st.error(f"Could not load the quiz sheet: {error}")
