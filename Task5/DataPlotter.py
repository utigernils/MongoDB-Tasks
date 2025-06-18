from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

env_connection_string = os.getenv('connection_string')


def fetch_data():
    client = MongoClient(env_connection_string)
    db = client['powerlog']
    collection = db['logs']
    logs = list(collection.find().sort("timestamp", 1))

    timestamps = [log["timestamp"] for log in logs]
    cpu = [log["cpu"] for log in logs]
    ram_used = [log["ram_used"] / (1024 ** 3) for log in logs]  # GB
    ram_total = [log["ram_total"] / (1024 ** 3) for log in logs]  # GB

    return timestamps, cpu, ram_used, ram_total


def plot_data():
    timestamps, cpu, ram_used, ram_total = fetch_data()

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(timestamps, cpu, label='CPU (%)', color='red')
    plt.ylabel("CPU Usage (%)")
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(timestamps, ram_used, label='RAM Used (GB)', color='blue')
    plt.plot(timestamps, ram_total, label='RAM Total (GB)', color='green', linestyle='--')
    plt.ylabel("RAM (GB)")
    plt.xlabel("Timestamp")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_data()
