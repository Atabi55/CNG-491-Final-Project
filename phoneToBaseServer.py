from flask import *
import dataBase

username = ""

app = Flask(__name__)
app.secret_key = "123"


@app.route("/")
@app.route("/index")
def showHomePage():
    # response from the server
    return jsonify({"message":"This is home page"})


@app.route('/user/user-data', methods=['GET'])
def get_user_data():
    try:
        userdata = dataBase.readUser("Users.db", username)

        return jsonify({"status": "success", 'data': userdata})

    except Exception as e:
        return jsonify({
            "status": "error",
            'data': [],
            'error': str(e)
        }), 500



@app.route('/user/user-stats', methods=['GET', 'POST'])
def get_user_stats():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    if request.method == 'POST':
        sDate = data.get("statDate")# YYYY-mm-DD HH:MM:SS format e.g. 2025-05-04 13:25:31
        score = data.get("score")# two decimal point float
        values = [username, score, sDate]#username comes from the token
        dataBase.insertStats("Users.db", values)
        return jsonify({"status": "success", "message": "stat score added successfully"})
    elif request.method == 'GET':

        dateFrom = data.get("dateFrom")
        dateUntil = data.get("dateUntil")

        # 1. Get exercises from DB
        if(dateFrom == None or dateUntil == None):
            userdata = dataBase.getUserStats("Users.db", username)
        else:
            userdata = dataBase.getUserStats("Users.db", username, dateUntil, dateFrom)
        print(userdata, " ", username)
        return jsonify({"status": "success", "message": userdata})

    
@app.route('/user/edit-user', methods=['GET', 'POST'])
def user_edit():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    attribute = data.get("userAttr")
    newVal = data.get("attrVal")

    if(attribute == "weight"):
        dataBase.updateUserWeight("Users.db", username, newVal)
    elif(attribute == "Height"):
        dataBase.updateUserHeight("Users.db", username, newVal)
    elif(attribute == "age"):
        dataBase.updateUserAge("Users.db", username, newVal)
    else:
        return jsonify({"status": "failure"})
    return redirect(url_for("get_user_data"))

@app.route("/login", methods=['GET', 'POST'])
def login():
    global username
    if request.method == "POST":

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        userName = data.get('userName')
        password = data.get('password')

        user = dataBase.validateUser("Users.db", userName, password)

        if user:
            # Successful login, redirect to menu
            session['userName'] = userName
            username = userName
            message = "User: ", userName, " has successfully logged in"
            return jsonify({"status": "success", "message": message})

        else:
            # message = "Invalid username or password. Please try again."
            return jsonify({"status": "error", "message": "username and password don not match!"}), 400


@app.route("/logout")
def logout():
    global logVar
    session.pop("userName", None)
    logVar = 0
    return redirect(url_for("showHomePage"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

            # Extract fields
        userName = data.get('userName')
        password = data.get('password')
        fullName = data.get('fullName')
        email = data.get('email')
        age = data.get('age')
        gender = data.get('gender')
        weight = data.get('weight')
        height = data.get('height')

        # Validation
        if not all([userName, password, fullName, email, age, gender, weight, height]):
            print("Validation failed - missing fields")
            return jsonify({"status": "error", "message": "All fields are required"}), 400

        # Insert to database
        values = [userName, password, fullName, email, age, gender, weight, height]
        message = dataBase.insertUser("Users.db", values)

        return jsonify({"status": "success", "message": message})


dataBase.createDataBase("Users.db")
if __name__ == "__main__":
    app.run(host="0.0.0.0")
