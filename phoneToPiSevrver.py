from flask import *
import dataBase
import subprocess


def executeExercise(data):
    # Define the script and arguments
    script_name = "ExerciseRoutineExecuter.py"
    arguments = [data]  # Replace with correct data name

    # Run the script with arguments
    result = subprocess.run(["python", script_name] + arguments, capture_output=True, text=True)

    print(result.stdout)
    dataBase.insertStats("users.db", result.stdout)


app = Flask(__name__)


@app.route("/")
def showHomePage():
    # response from the server
    return "This is home page"


@app.route('/api/exercises', methods=['POST'])
def get_stepping_exercises():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        exerciseType = data.get("type")  # Either stepping, tempo, or dance
        exercises = dataBase.getExercisesByType("Exercises.db", exerciseType)

        # 2. Return structured response
        return jsonify({
            'success': True,
            'data': exercises,
            'message': f"Found {len(exercises)} {exerciseType} exercises"
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'data': [],
            'error': str(e)
        }), 404

@app.route('/api/exercises/add-exercise', methods=['GET'])
def exercise_adding():
    if request.method == 'GET':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        name = data.get('name')
        exerciseType = data.get('type')
        text = data.get('text')
        dataBase.insertExercise("Exercises.db", [name, exerciseType, text])
        return jsonify({"status":"success","message": "exercise successfully added to the database"})

@app.route("/exercise-selection", methods=['GET'])  # When an exercise is selected, this route will execute it.
def exercise_selection():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    selectedExercise = data.get("text")
    print(selectedExercise)
    executeExercise(selectedExercise)  # executing the exercise
    return redirect("/exercise-instructions")  # redirecting to the exercise page


@app.route("/exercise-instructions", methods=['GET'])
def exercise_instructions():
    return jsonify({'data': 'x.jpg'})#dinamik bir şekilde resim adını değiştirmemiz gerek.

dataBase.createExerciseTable("Exercises.db")
if __name__ == "__main__":
    app.run(host="0.0.0.0")#ayrı ip nasıl yapılır bak, tek seferde kaç kişinin bağlancağını nasıl limitlerim bak
