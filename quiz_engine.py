import streamlit as st


QUIZ_LENGTH = 10


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


def reset_quiz(questions):
	question_count = min(QUIZ_LENGTH, len(questions))
	st.session_state.quiz_questions = questions.sample(n=question_count).reset_index(drop=True)
	st.session_state.current_question = 0
	st.session_state.score = 0
	st.session_state.submitted = False
	st.session_state.quiz_finished = False


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
	if "quiz_questions" not in st.session_state:
		reset_quiz(questions)

	if len(questions) < QUIZ_LENGTH:
		st.info(f"The sheet has fewer than {QUIZ_LENGTH} questions. Using all {len(questions)} questions.")

	if st.session_state.quiz_finished:
		question_count = len(st.session_state.quiz_questions)
		st.subheader("Quiz complete!")
		st.write(f"Score: {st.session_state.score} out of {question_count}")
		accuracy = st.session_state.score / question_count * 100 if question_count else 0
		st.write(f"Accuracy: {accuracy:.0f}%")
		if st.button("Restart Quiz"):
			reset_quiz(questions)
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
