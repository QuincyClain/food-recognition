import os
import argparse

from flask import Flask
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
from flask_sqlalchemy import SQLAlchemy  # Импорт SQLAlchemy

from backend.routes import set_routes
from backend.constants import UPLOAD_FOLDER, CSV_FOLDER, DETECTION_FOLDER, SEGMENTATION_FOLDER, METADATA_FOLDER

parser = argparse.ArgumentParser('Online Food Recognition')
parser.add_argument('--ngrok', action='store_true',
                    default=False, help="Run on local or ngrok")
parser.add_argument('--host',  type=str,
                    default='localhost:8000', help="Local IP")
parser.add_argument('--debug', action='store_true',
                    default=False, help="Run app in debug mode")


app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/api/*": {"origins": "*"}})


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Vladgoogle123@8.tcp.eu.ngrok.io:23380/Food_User_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Инициализация базы данных

try:
    with app.app_context():
        connection = db.engine.connect()
        connection.execute(text('SELECT 1'))
        connection.close()
    print("Successfully connected to the database.")
except Exception as e:
    print("Failed to connect to the database.")
    print(e)

# Определение модели пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER
app.config['DETECTION_FOLDER'] = DETECTION_FOLDER
app.config['SEGMENTATION_FOLDER'] = SEGMENTATION_FOLDER

set_routes(app)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    if not os.path.exists(DETECTION_FOLDER):
        os.makedirs(DETECTION_FOLDER, exist_ok=True)
    if not os.path.exists(SEGMENTATION_FOLDER):
        os.makedirs(SEGMENTATION_FOLDER, exist_ok=True)
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER, exist_ok=True)
    if not os.path.exists(METADATA_FOLDER):
        os.makedirs(METADATA_FOLDER, exist_ok=True)

    args = parser.parse_args()

    if args.ngrok:
        run_with_ngrok(app)
        app.run()
    else:
        hostname = str.split(args.host, ':')
        if len(hostname) == 1:
            port = 4000
        else:
            port = hostname[1]
        host = hostname[0]

        # Создание всех таблиц в базе данных
        with app.app_context():
            db.create_all()
            # Добавление тестового пользователя
            user = User(username='testuser', email='testuser@example.com')
            db.session.add(user)
            db.session.commit()

            # Чтение данных из таблицы
            user = User.query.first()
            print(user)  # Должно вывести <User testuser>

        app.run(host=host, port=port, debug=args.debug, use_reloader=False,
                ssl_context='adhoc')