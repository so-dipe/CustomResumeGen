from app import app
from config.config import Config

config = Config()

env = config.FLASK_ENV

if __name__ == "__main__":
    if env == "PROD":
        app.run(host="0.0.0.0", debug=False)
    elif env == "DEV":
        app.run(debug=True)
