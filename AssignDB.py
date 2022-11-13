from app import User, Activity, TP
from app import db


# db.create_all()
# generate fake data
user1 = User(username='admin', password='123')
user2 = User(username='Tom', password='123')
user3 = User(username='Jerry', password='123')
toy1 = TP(name='toy_test', type_='toy')
pet1 = TP(name='pet_test', type_='pet')

act1 = Activity(pet_ids='0', participant_ids='1/2', toy_ids='0',
                duration=120, alert=False)

db.session.add(user1)
db.session.add(user2)
db.session.add(user3)
db.session.add(toy1)
db.session.add(pet1)
db.session.add(act1)
db.session.commit()