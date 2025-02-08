import numpy as np
import cv2
from CentroidTrackerObject import CentroidTrackerObject
from ConnectNamedPipe import ConnectNamedPipe
import time
import mss
from collections import deque
import os
import datetime

pipeService = ConnectNamedPipe()
pipe = pipeService.create_pipe()
pipeService.connect_named_pipe(pipe)

threshold_lines = {
    'tl': 390, 'cl': 390, 'bl': 390, 'tr': 30, 'cr': 30, 'br': 30
}

capture_regions = {
    'tl': {"top": 591, "left": 448, "width": 440, "height": 60},
    'cl': {"top": 650, "left": 448, "width": 440, "height": 60},
    'bl': {"top": 717, "left": 448, "width": 440, "height": 60},
    'tr': {"top": 591, "left": 1035, "width": 440, "height": 60},
    'cr': {"top": 650, "left": 1035, "width": 440, "height": 60},
    'br': {"top": 717, "left": 1035, "width": 440, "height": 60}
}
capture_region_check = {
    'tl': {"top": 593, "left": 448, "width": 420, "height": 5},
    'cl': {"top": 652, "left": 448, "width": 420, "height": 5},
    'bl': {"top": 774, "left": 448, "width": 420, "height": 5},
    'tr': {"top": 593, "left": 1065, "width": 420, "height": 5},
    'cr': {"top": 652, "left": 1065, "width": 420, "height": 5},
    'br': {"top": 774, "left": 1065, "width": 420, "height": 5}
}
trackers = {
    'tl': CentroidTrackerObject(max_disappeared=1),
    'cl': CentroidTrackerObject(max_disappeared=1),
    'bl': CentroidTrackerObject(max_disappeared=1),
    'tr': CentroidTrackerObject(max_disappeared=1),
    'cr': CentroidTrackerObject(max_disappeared=1),
    'br': CentroidTrackerObject(max_disappeared=1)
}
disappeared_counts = {'tl': 0, 'bl': 0, 'tr': 0, 'br': 0}
prev_objects = {'tl': {}, 'bl': {}, 'tr': {}, 'br': {}}
directory_name = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
parent_dir = f"img/{directory_name}"
os.makedirs(parent_dir, exist_ok=True)

os.mkdir(f"{parent_dir}/1")
os.mkdir(f"{parent_dir}/3")
os.mkdir(f"{parent_dir}/7")
os.mkdir(f"{parent_dir}/9")

lower_green = np.array([40, 150, 100])
upper_green = np.array([85, 255, 255])


def get_contour_object(imgCheck, type_name):
    hsv = cv2.cvtColor(imgCheck, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.erode(mask, np.ones((1, 1), np.uint8), iterations=1)
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def put_text_obj(img, object, disappeared_count, type_name, is_reverse):
    # cv2.putText(img, f"count: {disappeared_count}", (20, 20),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    for object_id, centroid in object.items():
        position = centroid["position"]
        speed = centroid["speed"]
        if is_reverse:
            cv2.putText(img, f"{object_id}", (position[0], position[1] + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            # cv2.putText(img, f"{round(speed)}", (position[0], position[1]),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            cv2.circle(img, (position[0], position[1] + 15), 4, (0, 0, 255), -1)
        else:
            cv2.putText(img, f"{object_id}", (position[0] + 40, position[1] + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            # cv2.putText(img, f"{round(speed)}", (position[0], position[1]),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            cv2.circle(img, (position[0] + 40, position[1] + 15), 4, (0, 0, 255), -1)


def process_region(type_name, num, is_reverse=False):
    img = np.array(sct.grab(capture_regions[type_name]))
    imgCheck = np.array(sct.grab(capture_region_check[type_name]))
    contours = get_contour_object(imgCheck, type_name)

    rects = [(x, y, w, h) for contour in contours if cv2.contourArea(contour) > 50
             for x, y, w, h in [cv2.boundingRect(contour)]]

    objects = trackers[type_name].update(rects)
    put_text_obj(img, objects, disappeared_counts[type_name], type_name, is_reverse)
    for obj_id, centroid in objects.items():
        position = centroid["position"]
        if is_reverse:
            if position[0] > threshold_lines[type_name]:
                pipeService.send_data(pipe, num)
                disappeared_counts[type_name] += 1
                cv2.imwrite(f'{parent_dir}/{num}/{obj_id}.jpg', img)
        else:
            if position[0] < threshold_lines[type_name]:
                pipeService.send_data(pipe, num)
                disappeared_counts[type_name] += 1
                cv2.imwrite(f'{parent_dir}/{num}/{obj_id}.jpg', img)

    cv2.line(img, (threshold_lines[type_name], 0), (threshold_lines[type_name], 60), (255, 0, 0), 3)
    cv2.imshow(f"img_{type_name}", img)


with mss.mss() as sct:
    frame_count = 0
    start_time = time.time()
    while True:
        frame_count += 1
        elapsed_time = time.time() - start_time
        process_region("tl", "7", is_reverse=True)
        process_region("bl", "1", is_reverse=True)
        process_region("tr", "9", )
        process_region("br", "3", )

        if elapsed_time > 1:  # Update FPS every second
            fps = frame_count / elapsed_time
            print(f"FPS: {fps:.2f}")
            frame_count = 0
            start_time = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
