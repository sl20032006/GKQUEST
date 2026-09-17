import pandas as pd
import gspread
import streamlit as st


CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDIZghhgdV_kg2GYPMEGX-NFatFtmxYpjFzScNAvDqG_8utOoZGxNnvYIshAvUHbkRP6qArfWOO_d1/pub?output=csv"
REPOSITORY_COLUMNS = [
	"ID",
	"Question",
	"Option A",
	"Option B",
	"Option C",
	"Option D",
	"Answer",
	"Question Type",
	"Subject",
	"Topic",
	"Difficulty",
	"Exam",
	"Explanation",
]


def load_questions():
	questions = pd.read_csv(CSV_URL)
	if "Question Type" not in questions.columns and "Quetion type" in questions.columns:
		questions = questions.rename(columns={"Quetion type": "Question Type"})
	return questions


def save_question_to_sheet(question_data):
	try:
		credentials = dict(st.secrets["gcp_service_account"])
		settings = st.secrets["google_sheets"]
		spreadsheet_id = settings["spreadsheet_id"]
		worksheet_name = settings["worksheet_name"]
	except KeyError as error:
		raise RuntimeError(
			"Google Sheets secrets are not configured. Add gcp_service_account "
			"and google_sheets.spreadsheet_id/worksheet_name to Streamlit secrets."
		) from error

	client = gspread.service_account_from_dict(credentials)
	try:
		spreadsheet = client.open_by_key(spreadsheet_id)
		worksheet = spreadsheet.worksheet(worksheet_name)
		row = [question_data.get(column, "") for column in REPOSITORY_COLUMNS]
		worksheet.append_row(row, value_input_option="USER_ENTERED")
	except PermissionError as error:
		raise RuntimeError(
			"The service account cannot access this spreadsheet. Share the spreadsheet "
			"with the client_email from gcp_service_account as an Editor and verify "
			"the spreadsheet_id and worksheet_name."
		) from error
