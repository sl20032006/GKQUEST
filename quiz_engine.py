import streamlit as st


QUIZ_LENGTH = 10
SUPPORTED_QUESTION_TYPES = {"Single Correct", "Multiple Correct", "Integer"}


def get_available_subjects(questions):
	if "Subject" not in questions.columns:
		return []

	values = {
		str(value).strip()
		for value in questions["Subject"].dropna()
		if str(value).strip()
	}
	return sorted(values)


def filter_questions_by_subjects(questions, subjects):
	if "Subject" not in questions.columns or not subjects:
		return questions.iloc[0:0].copy()

	selected_subjects = {str(subject).strip() for subject in subjects}
	filtered = questions[
		questions["Subject"].fillna("").astype(str).str.strip().isin(selected_subjects)
	]
	if "Question Type" in filtered.columns:
		filtered = filtered[
			filtered["Question Type"].fillna("").astype(str).str.strip().isin(
				SUPPORTED_QUESTION_TYPES
			)
		]
	return filtered


def check_single_correct(selected_letter, answer):
	return selected_letter == str(answer).strip().upper()


def check_multiple_correct(selected_letters, answer):
	correct_letters = {
		letter.strip().upper()
		for letter in str(answer).split(",")
		if letter.strip()
	}
	return set(selected_letters) == correct_letters


def check_integer(selected_number, answer):
	try:
		return int(selected_number) == int(str(answer).strip())
	except (TypeError, ValueError):
		return False


def reset_quiz(questions, requested_count=None):
	if requested_count is None:
		requested_count = QUIZ_LENGTH
	question_count = min(requested_count, QUIZ_LENGTH, len(questions))
	for key in list(st.session_state):
		if key.startswith(("single_answer_", "option_", "integer_answer_")):
			del st.session_state[key]
	st.session_state.quiz_questions = questions.sample(n=question_count).reset_index(drop=True)
	st.session_state.current_question = 0
	st.session_state.score = 0
	st.session_state.submitted = False
	st.session_state.quiz_finished = False
	st.session_state.last_answer_correct = False


def clear_quiz_state():
	for key in [
		"quiz_questions",
		"quiz_filter_subjects",
		"quiz_active",
		"current_question",
		"score",
		"submitted",
		"quiz_finished",
		"last_answer_correct",
		"quiz_subject_options",
		"quiz_question_count",
	]:
		st.session_state.pop(key, None)


def show_correct_answer(question):
	question_type = str(question["Question Type"]).strip()
	answer = str(question["Answer"]).strip().upper()

	if question_type == "Single Correct":
		option_text = question.get(f"Option {answer}", "")
		return f"{answer} ({option_text})"
	if question_type == "Multiple Correct":
		return answer
	return str(question["Answer"]).strip()


def show_quiz(questions):
	available_subjects = get_available_subjects(questions)
	if not st.session_state.get("quiz_active", False):
		if not available_subjects:
			st.warning("No non-empty subjects are available, so the quiz cannot be filtered yet.")
			return

		subject_labels = {
			subject: f"{subject} ({(questions['Subject'].fillna('').astype(str).str.strip() == subject).sum()})"
			for subject in available_subjects
		}
		selected_labels = st.multiselect(
			"Select subjects",
			[subject_labels[subject] for subject in available_subjects],
			key="quiz_subject_options",
		)
		selected_subjects = [
			subject for subject in available_subjects if subject_labels[subject] in selected_labels
		]
		filtered_questions = filter_questions_by_subjects(questions, selected_subjects)
		max_question_count = min(QUIZ_LENGTH, len(filtered_questions))
		question_count_options = list(range(1, max_question_count + 1)) or [1]
		requested_count = st.selectbox(
			"Number of questions",
			question_count_options,
			index=len(question_count_options) - 1,
			key="quiz_question_count",
			disabled=not selected_subjects,
		)
		if st.button("Start Quiz", key="start_quiz"):
			if not selected_subjects:
				st.error("Select at least one subject before starting the quiz.")
				return
			if filtered_questions.empty:
				st.error("The selected subjects have no valid questions to quiz.")
				return
			st.session_state.quiz_filter_subjects = selected_subjects
			st.session_state.quiz_question_count = min(requested_count, len(filtered_questions))
			reset_quiz(filtered_questions, st.session_state.quiz_question_count)
			st.session_state.quiz_active = True
			st.rerun()
		return

	quiz_questions = st.session_state.quiz_questions
	if len(quiz_questions) < QUIZ_LENGTH:
		st.info(f"Using all {len(quiz_questions)} available questions for this selection.")

	if st.session_state.quiz_finished:
		question_count = len(st.session_state.quiz_questions)
		st.subheader("Quiz complete!")
		st.write(f"Score: {st.session_state.score} out of {question_count}")
		accuracy = st.session_state.score / question_count * 100 if question_count else 0
		st.write(f"Accuracy: {accuracy:.0f}%")
		if st.button("Restart Quiz"):
			filtered_questions = filter_questions_by_subjects(
				questions, st.session_state.get("quiz_filter_subjects", [])
			)
			if filtered_questions.empty:
				st.error("The selected subjects no longer have valid questions.")
				return
			reset_quiz(
				filtered_questions,
				st.session_state.get("quiz_question_count", QUIZ_LENGTH),
			)
			st.rerun()
		return

	question_number = st.session_state.current_question + 1
	question = st.session_state.quiz_questions.iloc[st.session_state.current_question]
	question_type = str(question["Question Type"]).strip()

	st.write(f"Question {question_number} of {len(st.session_state.quiz_questions)}")
	st.write(f"Type: {question_type}")
	st.subheader(str(question["Question"]))

	option_letters = ["A", "B", "C", "D"]
	options = {
		letter: str(question[f"Option {letter}"])
		for letter in option_letters
	}

	if question_type == "Single Correct":
		selected_text = st.radio(
			"Choose an answer:",
			list(options.values()),
			key=f"single_answer_{question_number}",
		)
		selected_letters = [
			letter for letter, text in options.items() if text == selected_text
		]
	elif question_type == "Multiple Correct":
		selected_letters = [
			letter
			for letter, text in options.items()
			if st.checkbox(text, key=f"option_{letter}_{question_number}")
		]
	elif question_type == "Integer":
		selected_number = st.number_input(
			"Enter your answer:",
			step=1,
			key=f"integer_answer_{question_number}",
		)
	else:
		st.error(f"Question type '{question_type}' is not supported yet.")

	if not st.session_state.submitted:
		if st.button("Submit Answer"):
			if question_type == "Single Correct":
				is_correct = check_single_correct(selected_letters[0], question["Answer"])
			elif question_type == "Multiple Correct":
				is_correct = check_multiple_correct(selected_letters, question["Answer"])
			elif question_type == "Integer":
				is_correct = check_integer(selected_number, question["Answer"])
			else:
				is_correct = False

			st.session_state.submitted = True
			st.session_state.last_answer_correct = is_correct
			if is_correct:
				st.session_state.score += 1
			st.rerun()

	if st.session_state.submitted:
		if st.session_state.last_answer_correct:
			st.success("Correct!")
		else:
			st.error("Incorrect.")
		st.write(f"Correct answer: {show_correct_answer(question)}")
		st.write(f"Explanation: {question['Explanation']}")

		if question_number < len(st.session_state.quiz_questions):
			if st.button("Next Question"):
				st.session_state.current_question += 1
				st.session_state.submitted = False
				st.rerun()
		else:
			if st.button("Finish Quiz"):
				st.session_state.quiz_finished = True
				st.rerun()
