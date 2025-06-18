from pymongo import MongoClient
from room import Room

class Dao_room:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.col = MongoClient(connection_string)["buildings"]["rooms"]

    def create(self, room):
        self.col.insert_one(room.__dict__)

    def read(self):
        room = Room(**self.col.find_one())
        return room

    def update(self, room_id, updated_fields):
        self.col.update_one({"_id": room_id}, {"$set": updated_fields})

    def delete(self, room_id):
        self.col.delete_one({"_id": room_id})
