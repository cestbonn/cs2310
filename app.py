from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
db_prefix = 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = db_prefix + os.path.join(app.root_path, 'data.db')
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    age = db.Column(db.Integer)
    birthday = db.Column(db.String)
    address = db.Column(db.String)
    img = db.Column(db.String)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_ids = db.Column(db.String)
    participant_ids = db.Column(db.String)
    toy_ids = db.Column(db.String)
    duration = db.Column(db.Float)
    alert = db.Column(db.Boolean)
    name = db.Column(db.String)


class TP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    type_ = db.Column(db.String) # Toy, Pet
    belong_to = db.Column(db.Integer)


with app.app_context():
    db.drop_all()
    db.create_all()
    user1 = User(username='admin', password='123', age=21, birthday='2001-1-1', address='Sennott Square, Pittsburgh',
                 img='../static/images/admin_img.jpg')
    user2 = User(username='Tom', password='123', age=22, birthday='2000-2-2', address='Sennott Square, Pittsburgh',
                 img='../static/images/Tom_img.jpeg')
    user3 = User(username='Jerry', password='123', age=23, birthday='1999-3-3', address='Sennott Square, Pittsburgh',
                 img='../static/images/Jerry_img.jpeg')

    toy1 = TP(name='toy_test', type_='toy', belong_to=2)
    pet1 = TP(name='pet_test', type_='pet', belong_to=3)

    act1 = Activity(pet_ids='1&', participant_ids='2&3', toy_ids='1&',
                    duration=120, alert=False, name='any customized text else id')

    for d in [user1, user2, user3, toy1, pet1, act1]:
        db.session.add(d)

    db.session.commit()

# jump to login page
@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():  # put application's code here
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user.password == password:
            uid = user.id
            return redirect(url_for('user_center', user_id=uid))
    else:
        return render_template('login.html')


@app.route('/user_center')
def user_center():
    user_id = request.args.get('user_id')
    data = {'user_id': user_id,
            'username': User.query.get(user_id).username,
            'basic_info': basic_info(user_id),
            'activity_info': activity_info(user_id),
            'TP_info': None}
    return render_template('user_center.html', data=data)


@app.route('/registration_activity')
def registration_activity():
    return 'registration_activity'


@app.route('/management')
def management():
    return 'activity management'


def basic_info(user_id):
    info = {'age': User.query.get(user_id).age,
            'birthday': User.query.get(user_id).birthday,
            'address': User.query.get(user_id).address,
            'img': User.query.get(user_id).img
            }
    return info


def activity_info(user_id):
    activity = Activity.query.filter(Activity.participant_ids.contains(f'{user_id}&')).first()
    if not activity:
        return None
    info = {
        'avtivity_id': activity.id,
        'name': activity.name,
        'participants': ', '.join([User.query.get(int(i)).username for i in activity.participant_ids.split('&') if len(i)]),
        'toy': ', '.join([TP.query.get(int(i)).name for i in activity.toy_ids.split('&') if len(i)]),
        'pet': ', '.join([TP.query.get(int(i)).name for i in activity.pet_ids.split('&') if len(i)]),
    }
    return info


if __name__ == '__main__':
    app.run()
