from flask import Flask, request, render_template, redirect, url_for
import os
import pickle

app = Flask(__name__, template_folder="../templates")

# File paths (Vercel allows writes only to /tmp)
INFO_PATH = "/tmp/info.pkl"
COSTS_PATH = "/tmp/costs.pkl"
NUM_ROOMS = 40
DEFAULT_COST = 100.0

def load_pickle(path, default):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except:
        return default

def save_pickle(path, data):
    with open(path, "wb") as f:
        pickle.dump(data, f)

def get_data():
    info = load_pickle(INFO_PATH, {
        "customers": [],
        "clean_rooms": [],
        "dirty_rooms": [],
        "customer_to_room": {},
        "occupied_rooms": []
    })
    costs = load_pickle(COSTS_PATH, [DEFAULT_COST] * NUM_ROOMS)
    return info, costs

@app.route("/", methods=["GET", "POST"])
def index():
    info, costs = get_data()

    message = ""
    if request.method == "POST":
        action = request.form.get("action")

        if action == "check_in":
            name = request.form["name"]
            room = int(request.form["room"]) - 1
            if room in info["occupied_rooms"]:
                message = "Room already occupied."
            else:
                info["customers"].append(name)
                info["occupied_rooms"].append(room)
                info["customer_to_room"][name] = room
                message = f"{name} checked into room {room + 1} (${costs[room]:.2f})"

        elif action == "check_out":
            name = request.form["name"]
            room = info["customer_to_room"].pop(name, None)
            if room is not None:
                info["customers"].remove(name)
                info["occupied_rooms"].remove(room)
                info["dirty_rooms"].append(room)
                message = f"{name} checked out of room {room + 1}."
            else:
                message = "Customer not found."

        elif action == "clean_room":
            room = int(request.form["room"]) - 1
            if room in info["dirty_rooms"]:
                info["dirty_rooms"].remove(room)
                info["clean_rooms"].append(room)
                message = f"Room {room + 1} marked clean."
            else:
                message = "Room was not marked dirty."

        elif action == "change_cost":
            room = int(request.form["room"]) - 1
            cost = float(request.form["cost"])
            costs[room] = cost
            message = f"Room {room + 1} cost set to ${cost:.2f}"

        save_pickle(INFO_PATH, info)
        save_pickle(COSTS_PATH, costs)

    return render_template("index.html", info=info, costs=costs, message=message)

# Required by Vercel
app.run()
