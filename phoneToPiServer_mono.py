from flask import *
import dataBase
import subprocess
from threading import Semaphore
import socket


def executeExercise(data):
    # Define the script and arguments
    script_name = "ExerciseRoutineExecuter_V5.py"
    arguments = [data]  # Replace with correct data name

    # Run the script with arguments
    result = subprocess.run(["python", script_name] + arguments, capture_output=True, text=True)

    print(result.stdout)
    msg = (result.stdout).split('\n')
    #dataBase.insertStats("Users.db", result.stdout)
    return msg[-2], msg[-3], msg[-4]#sending stat to phone which will redirect it to the base server

app = Flask(__name__)
MAX_CONNECTIONS = 2  # Rig + phone
connection_limiter = Semaphore(MAX_CONNECTIONS)

@app.before_request
def limit_connections():
    if not connection_limiter.acquire(blocking=False):
        client_ip = request.remote_addr
        print(f"Rejected connection from {client_ip} (max connections reached)")
        return jsonify({"error": "Robot busy"}), 429  # HTTP 429 = Too Many Requests

@app.teardown_request
def release_connection(exception=None):
    connection_limiter.release()


@app.route("/")
def showHomePage():
    # response from the server
    return "This is home page"


@app.route('/api/exercises', methods=['POST','GET'])
def get_stepping_exercises():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        exerciseType = data.get("type")  # Either stepping, tempo, or dance
        exercises = dataBase.getExercisesByType("Exercises.db", exerciseType)

        # 2. Return structured response
        response = jsonify({
            'success': True,
            'data': exercises,
            'message': f"Found {len(exercises)} {exerciseType} exercises"
        })

        #print(response)
        #print(response.data)
        #print(response.get_json())
        return response

    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'data': [],
            'error': str(e)
        }), 404

@app.route('/api/exercises/add-exercise', methods=['GET','POST'])
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

@app.route("/exercise-selection", methods=['GET','POST'])  # When an exercise is selected, this route will execute it.
def exercise_selection():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    selectedExerciseName = data.get("name")
    selectedExercise = dataBase.getSpecificExerciseText("Exercises.db",selectedExerciseName)[0]
    print(selectedExercise)
    msg, tmpArr, dur = executeExercise(selectedExercise)  # executing the exercise
    #return redirect("/exercise-instructions")  # redirecting to the exercise page
    return jsonify({"stat":msg, "interval": json.loads(tmpArr), "duration": dur, "exercise": selectedExerciseName})

@app.route("/exercise-instructions", methods=['GET'])
def exercise_instructions():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    while(True):
        if(data.get("exercise_status") == "complete"):
            return redirect("/")


@app.route("/user/exercise-names", methods=["GET"])
def get_exercise_names():
    try:
        names = dataBase.getAllExerciseNames("Exercises.db") 
        return jsonify({"status": "success", "exercises": names})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


dataBase.createExerciseTable("Exercises.db")
if __name__ == "__main__":
    host_ip = socket.gethostbyname(socket.gethostname())
    app.run(host='192.168.137.110', port=5000, threaded=True)
