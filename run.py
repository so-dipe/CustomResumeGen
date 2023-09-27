from app import app
from config.config import Config

config = Config()

env = config.FLASK_ENV

if __name__ == "__main__":
    if env == "PROD":
        app.run()
    elif env == "DEV":
        app.run(debug=True)
