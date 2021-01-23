from flask import Flask, send_from_directory, request
import os

app = Flask(__name__)


@app.route("/")
def main():
    return "ok"


@app.route("/download")
def download():
    filename = request.json['filename']

    try:
        return send_from_directory(directory='static', filename=filename, as_attachment=True)
    except Exception as e:
        print(e)
        return "bad"
    return "ok"


@app.route("/upload")
def upload():
    filename = request.args['filename']
    data = request.data


    files = [f for _, _, f in os.walk(os.getcwd() + "/static")][0]
    for file in files:
        if file == filename:
            return {"nameIsTaken": True}
    with open("static/" + filename, "wb+") as file:
        file.write(request.data)
    return {"ok": True}


app.run(debug=True)
