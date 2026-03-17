from flask import Flask, render_template, request, Response
import random

# AI functions
from detection_ai import start_ai_detection, get_bus_data, get_frame

app = Flask(__name__)

# Bus Data (UPDATED SEAT CAPACITY)
buses = {
    1: {
        "name": "KSRTC City Express",
        "route": "Calicut → Kozhikode Beach",
        "total_seats": 18,
        "passengers": 0
    },
    2: {
        "name": "Metro Fast Passenger",
        "route": "Calicut → Medical College",
        "total_seats": 20,
        "passengers": 0
    },
    3: {
        "name": "Town Circular",
        "route": "Calicut → Mavoor Road",
        "total_seats": 16,
        "passengers": 0
    }
}

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Search Results + Recommendation
@app.route("/search", methods=["POST"])
def search():

    source = request.form.get("source")
    destination = request.form.get("destination")

    bus_list = []

    best_bus = None
    best_score = -999

    for bus_id, bus in buses.items():

        arrival_time = random.randint(1, 10)

        # Get AI passenger data
        ai_data = get_bus_data(bus_id)

        available = ai_data["available"]

        # Recommendation score
        score = available - arrival_time

        if score > best_score:
            best_score = score
            best_bus = bus_id

        bus_list.append({
            "id": bus_id,
            "name": bus["name"],
            "route": bus["route"],
            "arrival": f"Arriving in {arrival_time} mins",
            "available": available
        })

    return render_template(
        "bus_list.html",
        source=source,
        destination=destination,
        buses=bus_list,
        best_bus=best_bus
    )


# Bus Detail Page
@app.route("/bus/<int:bus_id>")
def bus_detail(bus_id):

    bus = buses.get(bus_id)

    if not bus:
        return "Bus Not Found", 404

    return render_template(
        "bus_detail.html",
        bus_id=bus_id,
        bus=bus
    )


# Real-time Bus API
@app.route("/api/bus/<int:bus_id>")
def bus_api(bus_id):

    try:
        data = get_bus_data(bus_id)
        return data
    except:
        return {"error": "Bus not found"}, 404


# Video Feed for AI Monitoring
@app.route('/video/<int:bus_id>')
def video_feed(bus_id):

    def generate():

        while True:

            frame = get_frame(bus_id)

            if frame is None:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   frame + b'\r\n')

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# AI Monitor Page
@app.route("/ai-monitor")
def ai_monitor():
    return render_template("ai_monitor.html")


# Start AI detection
if __name__ == "__main__":

    start_ai_detection()

    app.run(debug=True)