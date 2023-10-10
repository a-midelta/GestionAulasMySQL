from pymongo import MongoClient, errors
from bson import ObjectId

class MongoDBHandler:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["aulas"]
        self.collection = self.db["disponibilidad"]

    def insert_data(self, day, time, name, subject, classroom):
        data = {"day": day, "time": time, "name": name, "subject": subject, "classroom": classroom}
        self.collection.insert_one(data)

    def check_duplicate(self, day, time, classroom):
        count = self.collection.count_documents({"day": day, "time": time, "classroom": classroom})
        return count > 0

    def get_all_data(self):
        cursor = self.collection.find({}, {"_id": 0})
        data = list(cursor)
        return data

    def delete_data(self, day, time):
        self.collection.delete_one({"day": day, "time": time})
        
