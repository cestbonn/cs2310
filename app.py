import random
import time

from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
db_prefix = 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = db_prefix + os.path.join(app.root_path, 'data.db')
db = SQLAlchemy(app)
fake_heat_rate = {'4': [[70, 85, 92, 108, 130, 150, 130, 110, 100, 90, 88, 80], 0],
                  '2': [[70, 85, 92, 85, 77, 80, 88, 70, 85, 78, 90, 85], 0],
                  '1': [[100, 110, 120, 115, 117, 127, 120, 110, 115, 120, 112, 109], 0],
                  '3': [[100, 110, 120, 115, 117, 127, 120, 110, 115, 120, 112, 109], 0]
                  }
fake_temperature = {
    '3': 29, '2': 28, '1': 27, '4': 27
}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    age = db.Column(db.Integer)
    birthday = db.Column(db.String)
    address = db.Column(db.String)
    img = db.Column(db.String)
    alert = db.Column(db.Boolean)
    calling = db.Column(db.Boolean)
    answer = db.Column(db.Boolean)
    calling_time = db.Column(db.Integer)
    reject = db.Column(db.Integer)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_ids = db.Column(db.String)
    tp_ids = db.Column(db.String)
    duration = db.Column(db.Float)
    alert = db.Column(db.Boolean)
    name = db.Column(db.String)
    start = db.Column(db.String)
    current = db.Column(db.String)


class TP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    type_ = db.Column(db.String) # Toy, Pet
    belong_to = db.Column(db.Integer)


with app.app_context():
    db.drop_all()
    db.create_all()
    user1 = User(username='admin', password='123')
    user2 = User(username='Tom', password='123', age=22, birthday='2000-2-2', address='Sennott Square, Pittsburgh',
                 img='../static/images/Tom_img.jpeg', alert=False, calling=False, reject=False)
    user3 = User(username='Jerry', password='123', age=23, birthday='1999-3-3', address='Sennott Square, Pittsburgh',
                 img='../static/images/Jerry_img.jpeg', alert=False, calling=False, reject=False)
    user4 = User(username='Spike', password='123', age=24, birthday='1998-4-4', address='Sennott Square, Pittsburgh',
                 img='../static/images/Spike_img.jpeg', alert=False, calling=False, reject=False)

    toy1 = TP(name='Tom\'s Toy', type_='toy', belong_to=2)
    pet1 = TP(name='Jerry\'s Pet', type_='pet', belong_to=3)

    act1 = Activity(tp_ids='1&2&', participant_ids='2&3&', start='12:00', current='12:45',
                    duration=120, alert=False, name='Tom&Jerry chasing game')

    for d in [user1, user2, user3, user4, toy1, pet1, act1]:
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
        if username == 'admin' and user.password == password:
            return redirect(url_for('admin_center'))
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
            'TP_info': TP_info(user_id)}
    return render_template('user_center.html', data=data)


@app.route('/admin_center')
def admin_center():
    data = {
        'users': {i.id: {'name': i.username, 'img': i.img,
                         'activity_id': Activity.query.filter(Activity.participant_ids.contains(f'{i.id}&')).first().id
                         if Activity.query.filter(Activity.participant_ids.contains(f'{i.id}&')).first() else None}
                  for i in User.query.all() if i.username != 'admin'},
        'pt': {i.id: {'name': i.name,
                      'activity_id': Activity.query.filter(Activity.tp_ids.contains(f'{i.id}&')).first().id
                      if Activity.query.filter(Activity.tp_ids.contains(f'{i.id}&')).first() else None,
                      'belong to': i.belong_to}
               for i in TP.query.all()},
        'activity': {i.id: [str(User.query.get(u).id) for u in i.participant_ids.split('&') if len(u)]
                     for i in Activity.query.all()},
    }
    return render_template('admin_center.html', data=data)


@app.route('/registration_activity', methods=['POST', 'GET'])
def registration_activity():
    user_id = request.args.get('user_id')
    if request.method == 'POST':
        interest = request.form.get('interest')
        duration = request.form.get('duration')
        if 'Tom' in interest or 'Jerry' in interest:
            data = {'recommendation': f'we recommend you activity 1 !, {Activity.query.get(1).name}', 'user_id': user_id}
            participants = Activity.query.get(1).participant_ids
            Activity.query.get(1).participant_ids = participants + f'{user_id}&'
            db.session.commit()
        else:
            data = {'recommendation': 'no available activity :(. Register a new one :)', 'user_id': user_id}
            new_act = Activity(tp_ids='', participant_ids=f'{user_id}&', start='12:00', current='12:45',
                               duration=duration, alert=False, name=interest)
            db.session.add(new_act)
            db.session.commit()
        return render_template("register_activity.html", data=data)
    else:
        data = {'recommendation': None, 'user_id': user_id}
        return render_template("register_activity.html", data=data)


@app.route('/end_activity')
def end_activity():
    user_id = request.args.get('user_id')
    activity = Activity.query.filter(Activity.participant_ids.contains(f'{user_id}&')).first()
    participants = activity.participant_ids
    activity.participant_ids = participants.replace(f'{user_id}&', '')
    if activity.participant_ids == '':
        Activity.query.filter(Activity.id == activity.id).delete()
    db.session.commit()
    return "terminate success!"


@app.route('/registration_TP', methods=['POST', 'GET'])
def registration_TP():
    user_id = request.args.get('user_id')
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        new_tp = TP(name=name, type_=type, belong_to=user_id)
        db.session.add(new_tp)
        db.session.commit()
        data = {'flag': 'register success', 'user_id': user_id}
        return render_template("register_TP.html", data=data)
    else:
        data = {'flag': False, 'user_id': user_id}
        return render_template("register_TP.html", data=data)


@app.route('/activity')
def activity():
    act_id = request.args.get('act_id')
    user_id = request.args.get('user_id')
    data = {
        'display': {'act_id': act_id},
        'arguments': {},
        'device_data': {},
        'user_id': user_id,
    }
    return render_template('activity.html', data=data)


@app.route('/read_data')
def read_data():
    user_id = request.args.get('user_id')
    heart_rate = fake_heat_rate[user_id][0]
    temperature = fake_temperature[user_id]
    alert = User.query.get(user_id).alert
    calling = User.query.get(user_id).calling
    reject = User.query.get(user_id).reject
    if calling:
        answer = User.query.get(user_id).answer
    else:
        answer = False
    return {'heartrate': heart_rate[-1], 'temperature': temperature, 'alert': alert,
            'heartrate_seq': heart_rate,
            'X': [str(i) for i in list(range(len(fake_heat_rate[user_id][0])))],
            'calling': calling,
            'answer': answer,
            'reject': reject}


@app.route('/send_alert')
def send_alert():
    user_id = request.args.get('user_id')
    User.query.get(user_id).alert = True
    db.session.commit()
    return 'Alert sent!'


@app.route('/call')
def call():
    user_id = request.args.get('user_id')
    User.query.get(user_id).calling = True
    User.query.get(user_id).reject = False
    db.session.commit()
    return render_template('waiting_room.html', user_id=user_id)


@app.route('/cancell_call')
def cancel_call():
    user_id = request.args.get('user_id')
    User.query.get(user_id).calling = False
    db.session.commit()
    ad_center = admin_center()
    return ad_center


@app.route('/answer')
def answer():
    user_id = request.args.get('user_id')
    User.query.get(user_id).answer = True
    db.session.commit()
    return 'answering...'


@app.route('/reject')
def reject():
    user_id = request.args.get('user_id')
    User.query.get(user_id).answer = False
    User.query.get(user_id).calling = False
    User.query.get(user_id).reject = True
    db.session.commit()
    return 'reject!'


@app.route('/end_call')
def end_call():
    user_id = request.args.get('user_id')
    User.query.get(user_id).calling = False
    User.query.get(user_id).answer = False
    db.session.commit()
    return 'end call'


@app.route('/generate_data')
def generate_data():
    return render_template("generate_data.html")


@app.route('/generate')
def generate():
    for k, v in fake_heat_rate.items():
        heart_rate = v[0]
        heart_rate.append(heart_rate.pop(0))
        fake_heat_rate[k][0] = heart_rate

        user = User.query.get(k)
        if heart_rate[-1] >= 150 or fake_temperature[k] >= 30:
            user.alert = True
            v[1] = 0
        else:
            if v[1] <= 5:
                pass
            else:
                v[1] = 0
                user.alert = False
        v[1] += 1
    db.session.commit()
    return fake_heat_rate


@app.route('/video')
def video():
    user_id = request.args.get('user_id')
    data = {'user_id': user_id}
    User.query.get(user_id).answer = True
    db.session.commit()
    return render_template('video.html', data=data)


def basic_info(user_id):
    info = {'display': {'age': User.query.get(user_id).age,
                        'birthday': User.query.get(user_id).birthday,
                        'address': User.query.get(user_id).address,},
            'arguments': {'img': User.query.get(user_id).img,}
            }
    return info


def activity_info(user_id):
    activity = Activity.query.filter(Activity.participant_ids.contains(f'{user_id}&')).first()
    if not activity:
        return None
    info = {
        'display': {'activity_id': activity.id,
                    'name': activity.name,
                    'participants': ', '.join([User.query.get(int(i)).username for i in activity.participant_ids.split('&') if len(i)]),
                    'toy': ', '.join([TP.query.get(i).name for i in activity.tp_ids.split('&') if len(i) and TP.query.get(i).type_=='toy']),
                    'pet': ', '.join([TP.query.get(i).name for i in activity.tp_ids.split('&') if len(i) and TP.query.get(i).type_=='pet']),
                    'start': activity.start,
                    'duration': str(int(activity.duration)) + 'min'},
        'arguments': {'alert_statue': False}
    }
    return info


def TP_info(user_id):
    tps = TP.query.filter_by(belong_to=user_id).all()
    info = []
    for tp in tps:
        tp_id = tp.id
        temp = {
            'name': TP.query.get(tp_id).name,
            'activity': ', '.join([str(a.id) for a in Activity.query.filter(Activity.tp_ids.contains(f'{tp_id}&')).all()]),
        }
        info.append(temp)
    return info


if __name__ == '__main__':
    app.run()
