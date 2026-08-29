import mongoengine as db
import pymongo
import mongomock
print("pymongo version:", pymongo.__version__)
print("mongoengine version:", db.__version__)

db.connect(db='test_db', host='localhost', mongo_client_class=mongomock.MongoClient)

class TestDoc(db.Document):
    name = db.StringField()

qs = TestDoc.objects()
print("bool(qs):", bool(qs))

TestDoc(name="test").save()
print("bool(qs):", bool(qs))
