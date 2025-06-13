from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional, List
from bson import ObjectId
import sys
import os
from dotenv import load_dotenv

load_dotenv()

env_connection_string = os.getenv('connection_string')

class MongoDBExplorer:
    def __init__(self, connection_string: str = env_connection_string):
        self.client: MongoClient = MongoClient(connection_string)
        self.current_db: Optional[Database] = None
        self.current_collection: Optional[Collection] = None

    def show_databases(self) -> None:
        db_names = self.client.list_database_names()

        print("\nDatabases")
        if not db_names:
            print("No Databases")
            return

        for db in db_names:
            print(f" - {db}")

    def select_database(self) -> bool:
        db_name = input("\nSelect Database: ").strip()

        if db_name not in self.client.list_database_names():
            print(f"Database '{db_name}' not found. Please try again.")
            return False

        self.current_db = self.client[db_name]
        return True

    def show_collections(self) -> None:
        if self.current_db is None:
            return

        col_names = self.current_db.list_collection_names()

        print(f"\n{self.current_db.name}")
        print("\nCollections")

        if not col_names:
            print("No Collections")
            return

        for col in col_names:
            print(f" - {col}")

    def select_collection(self) -> bool:
        if self.current_db is None:
            return False

        col_name = input("\nSelect Collection: ").strip()

        if col_name not in self.current_db.list_collection_names():
            print(f"Collection '{col_name}' not found. Please try again.")
            return False

        self.current_collection = self.current_db[col_name]
        return True

    def show_documents(self) -> None:
        if self.current_collection is None:
            return

        print(f"\n{self.current_db.name}.{self.current_collection.name}")
        print("\nDocuments")

        documents = list(self.current_collection.find({}, {"_id": 1}))

        if not documents:
            print("No Documents")
            return

        for doc in documents:
            print(f" - {doc['_id']}")

    def select_document(self) -> None:
        if self.current_collection is None:
            return

        doc_id = input("\nSelect Document: ").strip()

        try:
            document = self.current_collection.find_one({"_id": ObjectId(doc_id)})

            if document is None:
                print(f"Document with ID '{doc_id}' not found.")
                input("\nPress any key to return")
                return

            print(f"\n{self.current_db.name}.{self.current_collection.name}.{doc_id}\n")

            for key, value in document.items():
                if key != "_id":
                    print(f"{key}: {value}")

        except Exception as e:
            print(f"Error retrieving document: {str(e)}")

        input("\nPress any key to return")

    def run(self) -> None:
        while True:
            try:
                self.current_db = None
                self.current_collection = None

                while True:
                    self.show_databases()
                    if self.select_database():
                        break

                while True:
                    self.show_collections()
                    if self.select_collection():
                        break

                while True:
                    self.show_documents()
                    self.select_document()
                    break

            except KeyboardInterrupt:
                print("\nExiting...")
                self.client.close()
                sys.exit(0)

            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                input("Press any key to restart")

if __name__ == "__main__":
    explorer = MongoDBExplorer()
    explorer.run()
