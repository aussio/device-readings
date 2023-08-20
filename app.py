from flask import Flask
from device_reading.urls import device_reading_api

app = Flask(__name__)

app.register_blueprint(device_reading_api)


@app.route("/")
def hello():
    return "👋🏻 Hello brightwheel! 🌟🎡\n"


if __name__ == "__main__":
    app.run()
