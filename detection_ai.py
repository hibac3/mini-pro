import cv2
import threading
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Seat capacity for each bus (15–20 range)
BUS_SEATS = {
    1: 18,
    2: 20,
    3: 16
}

VIDEO_PATHS = {
    1: "videos/bus1.mp4",
    2: "videos/bus2.mp4",
    3: "videos/bus3.mp4"
}

bus_data = {
    1: {"passengers": 0, "available": 18, "crowd": "Low"},
    2: {"passengers": 0, "available": 20, "crowd": "Low"},
    3: {"passengers": 0, "available": 16, "crowd": "Low"}
}

latest_frames = {
    1: None,
    2: None,
    3: None
}


def process_video(bus_id):

    cap = cv2.VideoCapture(VIDEO_PATHS[bus_id])

    if not cap.isOpened():
        print(f"❌ Could not open video for Bus {bus_id}")
        return

    print(f"✅ AI started for Bus {bus_id}")

    while True:

        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results = model(frame)

        passengers = 0

        for r in results:
            for box in r.boxes:

                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf > 0.6:

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(frame,
                                  (x1, y1),
                                  (x2, y2),
                                  (0, 255, 0),
                                  2)

                    passengers += 1

        capacity = BUS_SEATS[bus_id]

        available = capacity - passengers

        if available < 0:
            available = 0

        occupancy = passengers / capacity

        if occupancy < 0.4:
            crowd = "Low"
        elif occupancy < 0.75:
            crowd = "Medium"
        else:
            crowd = "High"

        bus_data[bus_id] = {
            "passengers": passengers,
            "available": available,
            "crowd": crowd
        }

        latest_frames[bus_id] = frame


def start_ai_detection():

    for bus_id in VIDEO_PATHS:

        thread = threading.Thread(
            target=process_video,
            args=(bus_id,)
        )

        thread.daemon = True
        thread.start()


def get_bus_data(bus_id):

    return bus_data.get(bus_id, {
        "passengers": 0,
        "available": BUS_SEATS.get(bus_id, 15),
        "crowd": "Low"
    })


def get_frame(bus_id):

    frame = latest_frames.get(bus_id)

    if frame is None:
        return None

    ret, buffer = cv2.imencode('.jpg', frame)

    if not ret:
        return None

    return buffer.tobytes()