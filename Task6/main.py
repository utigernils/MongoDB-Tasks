from room import Room
from dao_room import Dao_room

import os
from dotenv import load_dotenv

load_dotenv()

env_connection_string = os.getenv('connection_string')

dao_room = Dao_room(env_connection_string)

room_create = Room("Pilatus", 12, True)
dao_room.create(room_create)

room_read = dao_room.read()

print(room_read)