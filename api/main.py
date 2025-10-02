from flask import Flask, request, jsonify
import hashids

app = Flask(__name__)

@app.route('/api')
def index():
    return jsonify("Pong!")

if __name__ == "__main__":
    app.run(debug = True)
