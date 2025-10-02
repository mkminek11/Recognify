from flask import Flask, request, jsonify
import hashids
from db import *

hid = hashids.Hashids(min_length = 8, salt = "ref4a9wzs7")

@app.route('/api')
def index():
    return jsonify("Pong!")

@app.route('/api/sets', methods=['GET'])
def get_sets():
    return jsonify([{ "id": hid.encode(set.id), "name": set.name } for set in Set.all()])

if __name__ == "__main__":
    app.run(debug = True)
