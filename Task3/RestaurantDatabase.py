from pymongo import MongoClient
from pymongo import GEOSPHERE
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

env_connection_string = os.getenv('connection_string')

client = MongoClient(env_connection_string)
db = client['restaurants']
collection = db['restaurants']

def display_unique_boroughs():
    boroughs = collection.distinct("borough")
    print("\nEinzigartige Stadtbezirke:")
    for borough in boroughs:
        print(f"- {borough}")


def display_top_3_restaurants_by_avg_score():
    pipeline = [
        {"$unwind": "$grades"},
        {"$group": {
            "_id": "$_id",
            "name": {"$first": "$name"},
            "avg_score": {"$avg": "$grades.score"}
        }},
        {"$sort": {"avg_score": -1}},
        {"$limit": 3}
    ]

    results = list(collection.aggregate(pipeline))

    print("\nTop 3 Restaurants nach durchschnittlichem Rating:")
    for i, restaurant in enumerate(results, 1):
        print(f"{i}. {restaurant['name']} - Durchschnittsrating: {restaurant['avg_score']:.2f}")


def find_nearest_restaurant_to_le_perigord():
    if "coord_2dsphere" not in collection.index_information():
        collection.create_index([("address.coord", GEOSPHERE)])

    le_perigord = collection.find_one({"name": "Le Perigord"})
    if not le_perigord:
        print("\nRestaurant 'Le Perigord' nicht gefunden.")
        return

    coordinates = le_perigord["address"]["coord"]

    nearest = collection.aggregate([
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": coordinates
                },
                "distanceField": "distance",
                "spherical": True,
                "query": {"name": {"$ne": "Le Perigord"}}
            }
        },
        {"$limit": 1}
    ])

    nearest_restaurant = list(nearest)[0]
    distance = nearest_restaurant["distance"]

    print(f"\nDas Restaurant '{nearest_restaurant['name']}' ist am nächsten zu 'Le Perigord'")
    print(f"Entfernung: {distance:.2f} Meter")


def search_restaurants():
    print("\nRestaurant-Suche")
    name = input("Name des Restaurants (leer lassen um zu ignorieren): ").strip()
    cuisine = input("Küche (leer lassen um zu ignorieren): ").strip()

    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}

    results = list(collection.find(query))

    if not results:
        print("Keine Restaurants gefunden.")
        return None

    print("\nSuchergebnisse:")
    for i, restaurant in enumerate(results, 1):
        print(f"{i}. {restaurant['name']} - {restaurant.get('cuisine', 'N/A')}")

    return results


def add_rating_to_restaurant():
    results = search_restaurants()
    if not results:
        return

    if len(results) > 1:
        choice = input(f"\nWählen Sie ein Restaurant (1-{len(results)}): ")
        try:
            choice = int(choice) - 1
            if choice < 0 or choice >= len(results):
                print("Ungültige Auswahl.")
                return
            restaurant = results[choice]
        except ValueError:
            print("Ungültige Eingabe.")
            return
    else:
        restaurant = results[0]

    try:
        score = int(input("Bewertung (0-100): "))
        if score < 0 or score > 100:
            print("Bewertung muss zwischen 0 und 100 liegen.")
            return
    except ValueError:
        print("Ungültige Bewertung.")
        return

    grade = "A"
    if score < 50:
        grade = "C"
    elif score < 75:
        grade = "B"

    new_rating = {
        "date": datetime.now(),
        "grade": grade,
        "score": score
    }

    collection.update_one(
        {"_id": restaurant["_id"]},
        {"$push": {"grades": new_rating}}
    )

    print(f"\nBewertung für {restaurant['name']} erfolgreich hinzugefügt.")


def main_menu():
    while True:
        print("\n--- Restaurant-Datenbank ---")
        print("1. Alle Stadtbezirke anzeigen")
        print("2. Top 3 Restaurants nach Rating anzeigen")
        print("3. Nächstgelegenes Restaurant zu 'Le Perigord' finden")
        print("4. Restaurants suchen")
        print("5. Restaurant bewerten")
        print("6. Beenden")

        choice = input("Auswahl: ")

        if choice == "1":
            display_unique_boroughs()
        elif choice == "2":
            display_top_3_restaurants_by_avg_score()
        elif choice == "3":
            find_nearest_restaurant_to_le_perigord()
        elif choice == "4":
            search_restaurants()
        elif choice == "5":
            add_rating_to_restaurant()
        elif choice == "6":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")


if __name__ == "__main__":
    main_menu()