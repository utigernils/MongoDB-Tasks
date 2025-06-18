import psutil
from datetime import datetime
from pymongo import MongoClient, ASCENDING

class Power:
    def __init__(self, cpu=None, ram_total=None, ram_used=None, timestamp=None):
        if cpu is None or ram_total is None or ram_used is None or timestamp is None:
            self.cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            self.ram_total = ram.total
            self.ram_used = ram.used
            self.timestamp = datetime.utcnow()
        else:
            self.cpu = cpu
            self.ram_total = ram_total
            self.ram_used = ram_used
            self.timestamp = timestamp

    def to_dict(self):
        return {
            "cpu": self.cpu,
            "ram_total": self.ram_total,
            "ram_used": self.ram_used,
            "timestamp": self.timestamp
        }

class PowerLogger:
    def __init__(self, db_name='powerlog', collection_name='logs', limit=10000, connection_string='mongodb://localhost:27017/'):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.limit = limit
        self.collection.create_index([("timestamp", ASCENDING)])

    def log(self):
        power = Power()
        self.collection.insert_one(power.to_dict())
        self._trim_logs()

    def _trim_logs(self):
        count = self.collection.estimated_document_count()
        if count > self.limit:
            to_delete = count - self.limit
            old_docs = self.collection.find().sort("timestamp", ASCENDING).limit(to_delete)
            ids_to_delete = [doc['_id'] for doc in old_docs]
            self.collection.delete_many({"_id": {"$in": ids_to_delete}})

if __name__ == "__main__":
    import time

    import os
    from dotenv import load_dotenv

    load_dotenv()

    env_connection_string = os.getenv('connection_string')

    logger = PowerLogger(connection_string=env_connection_string)

    print("Logging started. Press Ctrl+C to stop.")
    try:
        while True:
            logger.log()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLogging stopped.")
