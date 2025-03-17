import subprocess

# Define the script and arguments
script_name = "ExerciseRoutineExecuter.py"
arguments = ["data.txt"]  # Replace with correct data name

# Run the script with arguments
result = subprocess.run(["python", script_name] + arguments, capture_output=True, text=True)

print(result.stdout)
