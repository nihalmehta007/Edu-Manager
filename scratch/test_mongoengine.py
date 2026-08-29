import mongoengine as db
import pymongo
import mongomock
print("pymongo version:", pymongo.__version__)
print("mongoengine version:", db.__version__)

db.connect(db='test_db', host='localhost', mongo_client_class=mongomock.MongoClient)

class TestDoc(db.Document):
    name = db.StringField()

TestDoc(name="test").save()
print("Count:", TestDoc.objects.count())
