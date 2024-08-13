from flask import Flask, request
import os


app = Flask(__name__)


@app.route("/", methods=["POST"])
def webhook():
    if request.method == "POST":
        os.system("git -C /home/ian/repos/passivesonar pull")
        os.system(
            "docker-compose -f /home/ian/repos/passivesonar/docker/"
            "local-single/services/docker-compose.yml up --build -d"
        )
        return "Success", 200
    else:
        return "Invalid request", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
