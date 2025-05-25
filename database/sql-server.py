from flask import Flask, request, jsonify
from sql import checkEmail, askDbQuestion
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.environ['BACKEND_URL']}})

@app.route('/checkemail', methods=['GET'])
def checkemail():
    email = request.args.get('email', 'Guest')
    print("email ", email)
    isPresent = checkEmail(email)

    if isPresent:
        return jsonify({"response": "Success"})

    return jsonify({"response": "User not found"})


@app.route('/askdb', methods=['POST'])
def askdb():
    data = request.json  # Expecting JSON: {"a": 5, "b": 3}
    a = data.get('email')
    b = data.get('user_question')

    if a is None or b is None:
        return jsonify({"error": "Missing input values"}), 400

    result = askDbQuestion(a, b)
    return jsonify({"response": result})

if __name__ == '__main__':
    app.run(debug=True, port=8000)