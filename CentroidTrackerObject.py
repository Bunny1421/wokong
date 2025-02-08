import time
from scipy.spatial import distance as dist
import numpy as np


class CentroidTrackerObject:
    def __init__(self, max_disappeared=1):
        self.next_object_id = 1  # เริ่มต้นให้หมายเลข ID กับวัตถุ
        self.objects = {}  # เก็บตำแหน่งของวัตถุที่กำลังติดตาม
        self.disappeared = {}  # นับจำนวนเฟรมที่วัตถุหายไป
        self.max_disappeared = max_disappeared  # กำหนดขีดจำกัดของการหายไป

    def register(self, centroid):
        centroid_data = {
            "position": centroid,  # เก็บ centroid เป็น ndarray
            "start_time": time.time(),
            "start_centroid": centroid,
            "speed": 0.0  # เริ่มต้นด้วยความเร็วเป็น 0
        }
        self.objects[self.next_object_id] = centroid_data
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1  # ให้หมายเลข ID ใหม่กับวัตถุที่พบใหม่

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")

        for i, (x, y, w, h) in enumerate(rects):
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            input_centroids[i] = (cx, cy)

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = [obj["position"] for obj in self.objects.values()]

            D = dist.cdist(np.array(object_centroids), input_centroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)

            used_rows = set()
            used_cols = set()

            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[row]
                new_position = input_centroids[col]
                self.objects[object_id]["position"] = new_position
                self.disappeared[object_id] = 0
                # คำนวณ speed
                start_position = self.objects[object_id]["start_centroid"]
                start_time = self.objects[object_id]["start_time"]
                distance = np.linalg.norm(np.array(new_position) - np.array(start_position))
                time_elapsed = time.time() - start_time
                self.objects[object_id]["speed"] = distance / time_elapsed if time_elapsed > 0 else 0.0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(D.shape[0])) - used_rows
            unused_cols = set(range(D.shape[1])) - used_cols

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects