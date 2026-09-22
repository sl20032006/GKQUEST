import re

import pandas as pd
import streamlit as st

from google_sheets import save_question_to_sheet


def get_next_id(questions):
	if "ID" not in questions.columns:
		return "Q00001"

	highest_number = 0
	for value in questions["ID"].dropna():
		match = re.fullmatch(r"Q(\d+)", str(value).strip(), flags=re.IGNORECASE)
		if match:
			highest_number = max(highest_number, int(match.group(1)))

	return f"Q{highest_number + 1:05d}"


def get_existing_values(questions, column):
	if column not in questions.columns:
		return []

	values = {
		str(value).strip()
		for value in questions[column].dropna()
		if str(value).strip()
	}
	return sorted(values)


def show_add_question(questions):
	st.header("Add Question")
	st.write("Preview a question before adding it to the repository.")

	question_type = st.selectbox(
		"Question Type",
		["Single Correct", "Multiple Correct", "Integer"],
		key="new_question_type",
	)

	subject_options = ["+ Add New Subject"] + get_existing_values(questions, "Subject")
	selected_subject = st.selectbox("Subject", subject_options, key="new_subject_choice")
	if selected_subject == "+ Add New Subject":
		subject = st.text_input("New Subject", key="new_subject_value")
	else:
		subject = selected_subject

	exam_options = ["+ Add New Exam"] + get_existing_values(questions, "Exam")
	selected_exam = st.selectbox("Exam", exam_options, key="new_exam_choice")
	if selected_exam == "+ Add New Exam":
		exam = st.text_input("New Exam", key="new_exam_value")
	else:
		exam = selected_exam

	with st.form("add_question_form"):
		question_text = st.text_area("Question")

		if question_type in ["Single Correct", "Multiple Correct"]:
			option_a = st.text_input("Option A")
			option_b = st.text_input("Option B")
			option_c = st.text_input("Option C")
			option_d = st.text_input("Option D")
		else:
			option_a = option_b = option_c = option_d = ""
			st.info("Options are not needed for Integer questions.")

		if question_type == "Single Correct":
			answer_value = st.selectbox("Answer", ["A", "B", "C", "D"])
		elif question_type == "Multiple Correct":
			answer_letters = st.multiselect("Answer", ["A", "B", "C", "D"])
			answer_value = ",".join(answer_letters)
		else:
			answer_value = st.number_input("Answer", step=1, format="%d")

		topic = st.text_input("Topic")
		difficulty = st.text_input("Difficulty")
		explanation = st.text_area("Explanation")
		preview_clicked = st.form_submit_button("Preview Question")

	if preview_clicked:
		errors = []
		if not question_text.strip():
			errors.append("Question cannot be empty.")
		if question_type not in ["Single Correct", "Multiple Correct", "Integer"]:
			errors.append("Question Type is invalid.")
		if question_type in ["Single Correct", "Multiple Correct"]:
			missing_options = [
				letter for letter, value in {
					"A": option_a,
					"B": option_b,
					"C": option_c,
					"D": option_d,
				}.items() if not value.strip()
			]
			if missing_options:
				errors.append(f"Option {', '.join(missing_options)} cannot be empty.")
		if question_type == "Single Correct" and not answer_value:
			errors.append("Single Correct must have exactly one correct option.")
		if question_type == "Multiple Correct" and not answer_value:
			errors.append("Multiple Correct must have at least one correct option.")
		if question_type == "Integer":
			try:
				int(answer_value)
			except (TypeError, ValueError):
				errors.append("Integer answer must be a valid integer.")
		if not subject.strip():
			errors.append("Subject cannot be empty.")
		if not exam.strip():
			errors.append("Exam cannot be empty.")
		if not explanation.strip():
			errors.append("Explanation cannot be empty.")

		if errors:
			for error in errors:
				st.error(error)
		else:
			preview = {
				"ID": get_next_id(questions),
				"Question": question_text,
				"Option A": option_a,
				"Option B": option_b,
				"Option C": option_c,
				"Option D": option_d,
				"Answer": answer_value,
				"Question Type": question_type,
				"Subject": subject.strip(),
				"Topic": topic,
				"Difficulty": difficulty,
				"Exam": exam.strip(),
				"Explanation": explanation,
			}
			st.session_state.question_preview = preview

	if "question_preview" in st.session_state:
		st.subheader("Question Preview")
		st.table(pd.DataFrame([st.session_state.question_preview]).T.rename(columns={0: "Value"}))
		if st.button("Save Question"):
			try:
				save_question_to_sheet(st.session_state.question_preview)
				st.success("Question saved successfully.")
				del st.session_state.question_preview
			except Exception as error:
				error_details = str(error) or repr(error)
				st.error(f"Could not save question ({type(error).__name__}): {error_details}")
