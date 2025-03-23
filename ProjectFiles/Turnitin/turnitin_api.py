import os
import threading
import requests
import json
import subprocess
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Path to the Reports folder
REPORTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../Reports")

# Ensure the Reports folder exists
os.makedirs(REPORTS_FOLDER, exist_ok=True)

def process_file(data, task_id):
    """
    Process the file by downloading it and running the Turnitin script.
    """
    try:
        # Download the file
        file_url = data["file_url"]
        file_path = os.path.join(REPORTS_FOLDER, f"{task_id}.file")
        response = requests.get(file_url)
        with open(file_path, "wb") as f:
            f.write(response.content)

        # Run the Turnitin script with the provided options
        subprocess.run([
            "python3",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "turnitin.py")
        ], input=json.dumps(data), text=True)

    except Exception as e:
        # Save the error to the JSON file
        error_report = {"Error": str(e)}
        with open(os.path.join(REPORTS_FOLDER, f"{task_id}.json"), "w") as f:
            json.dump(error_report, f, indent=4)

@app.route("/submit", methods=["POST"])
def submit():
    """
    Handle the /submit endpoint to process a file.
    """
    data = request.get_json()
    if not data or "file_url" not in data:
        return jsonify({"Error": "Invalid request. 'file_url' is required."}), 400

    # Generate a unique task_id
    task_id = f"task_{int(time.time())}"

    # Start a new thread to process the file
    thread = threading.Thread(target=process_file, args=(data, task_id))
    thread.start()

    return jsonify({"task_id": task_id}), 200

@app.route("/receive/<task_id>", methods=["GET"])
def receive(task_id):
    """
    Handle the /receive endpoint to check the status of a task.
    """
    report_path = os.path.join(REPORTS_FOLDER, f"{task_id}.json")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report_data = json.load(f)
        return jsonify(report_data), 200
    else:
        return jsonify({"status": "processing"}), 200

if __name__ == "__main__":
    app.run(debug=True)
