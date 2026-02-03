from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector, json
from datetime import datetime

app = Flask(__name__)
CORS(app)

db = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "database": "emergency_db"
}

def analyze_patient(data):
    try:
        name = data["name"].strip()
        age = int(data["age"])
        gender = data["gender"].lower()
        hr = int(data["heart_rate"])
        oxygen = int(data["oxygen"])
        bp = data["blood_pressure"]
        symptoms = data.get("symptoms", "").lower()
    except:
        return {"error": "Invalid input"}

    actions = []
    status = "NORMAL"

    elderly_age = 60 if gender == "male" else 55
    high_hr = 120 if gender == "male" else 115
    warn_oxygen = 95 if gender == "male" else 94

    if oxygen < 90:
        actions.append("Provide oxygen support immediately")

    if hr > high_hr:
        actions.append("Urgent cardiac evaluation required")

    if "chest pain" in symptoms:
        if gender == "female":
            actions.append("Check for atypical heart attack symptoms")
        actions.append("Prepare ECG and cardiac enzymes test")

    if "unconscious" in symptoms:
        actions.append("Initiate CPR protocol if required")

    if age >= elderly_age and oxygen < warn_oxygen:
        actions.append("High-risk elderly patient — close monitoring")

    if oxygen < 90 or hr > high_hr or "unconscious" in symptoms:
        status = "EMERGENCY"
    elif oxygen < warn_oxygen or hr > 100:
        status = "WARNING"
    else:
        actions.append("Patient stable — routine monitoring")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    case = {
        "patient_name": name,
        "age": age,
        "gender": gender,
        "heart_rate": hr,
        "oxygen": oxygen,
        "blood_pressure": bp,
        "status": status,
        "actions": actions,
        "timestamp": timestamp
    }

    conn = mysql.connector.connect(**db)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patient_cases
        (patient_name, age, gender, heart_rate, oxygen, blood_pressure, status, actions, timestamp)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        case["patient_name"], case["age"], case["gender"],
        case["heart_rate"], case["oxygen"], case["blood_pressure"],
        case["status"], json.dumps(case["actions"]), case["timestamp"]
    ))
    conn.commit()
    cur.close()
    conn.close()

    return case

@app.route("/analyze", methods=["POST"])
def analyze():
    return jsonify(analyze_patient(request.json))

if __name__ == "__main__":
    app.run(debug=True)