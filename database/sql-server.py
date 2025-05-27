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
    data = request.json
    email = data.get('email')
    user_question = data.get('user_question')

    if email is None or user_question is None:
        return jsonify({"response": "Missing input values"}), 400

    result = askDbQuestion(email, user_question)
    return jsonify({"response": result})

if __name__ == '__main__':
    app.run(debug=True, port=8000)