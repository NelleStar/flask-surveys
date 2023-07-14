from flask import Flask, render_template, redirect, request, url_for, jsonify, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

# list to store responses for each survey
survey_responses = []

@app.route('/', methods=['GET', 'POST'])
def survey_home():
    if request.method == "POST":
        session['responses'] = []  # Initialize session with an empty list
        return redirect(url_for('start_survey', survey_id='survey_id', question_id=0))
    return render_template("survey.html", surveys=surveys)


@app.route('/survey/<survey_id>/questions/<int:question_id>', methods=['GET', 'POST'])
def start_survey(survey_id, question_id):
    if survey_id in surveys:
        selected_survey = surveys[survey_id]
        if request.method == "POST":
            answer = request.form['answer']

            responses = session.get('responses', [])  # Retrieve the list from the session
            responses.append(answer)
            session['responses'] = responses  # Store the updated list back into the session

            next_question_id = question_id + 1

            if next_question_id < len(selected_survey.questions):
                next_url = url_for('start_survey', survey_id=survey_id, question_id=next_question_id, _external=True)
                return redirect(next_url)
            else:
                return redirect(url_for('survey_completed', survey_id=survey_id))

        if question_id >= 0 and question_id < len(selected_survey.questions):
            question = selected_survey.questions[question_id]
            return render_template('questions.html', survey=selected_survey, survey_id=survey_id,
                                   question_id=question_id, question=question)

        flash("Invalid question ID. Please provide a valid question ID.", "error")
        return redirect(url_for('survey_home'))

    flash("Survey not found. Please select a valid survey.", "error")
    return redirect(url_for('survey_home'))


@app.route('/survey-completed')
def survey_completed():
    survey_id = request.args.get('survey_id', '')
    responses = session.get('responses', [])

    if survey_id != '' and len(responses) == len(surveys[survey_id].questions):
        flash("Thank you for taking the survey!", "success")
    else:
        flash("Please complete all the questions before submitting the survey.", "error")

    return redirect(url_for('survey_home'))


@app.route('/responses')
def get_responses():
    responses = session.get('responses', [])  # Retrieve the list from the session
    return jsonify(responses)


if __name__ == "__main__":
    app.run()

