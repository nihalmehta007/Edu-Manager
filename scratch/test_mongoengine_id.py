import mongoengine as db
import pymongo
import mongomock

db.connect(db='test_db', host='localhost', mongo_client_class=mongomock.MongoClient)

class User(db.Document):
    name = db.StringField()

u = User(name="test").save()
print("Saved ID:", u.id, type(u.id))

str_id = str(u.id)
u_fetched = User.objects(id=str_id).first()
print("Fetched by string:", u_fetched)
