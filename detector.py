import cv2
import mediapipe as mp
import math
import time
import winsound
from pathlib import Path
from ultralytics import YOLO
import os


def distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def eye_aspect_ratio(landmarks, eye_points, w, h):
    p1 = landmarks[eye_points[0]]
    p2 = landmarks[eye_points[1]]
    p3 = landmarks[eye_points[2]]
    p4 = landmarks[eye_points[3]]
    p5 = landmarks[eye_points[4]]
    p6 = landmarks[eye_points[5]]

    vertical1 = distance(p2, p6, w, h)
    vertical2 = distance(p3, p5, w, h)
    horizontal = distance(p1, p4, w, h)

    if horizontal == 0:
        return 0

    return (vertical1 + vertical2) / (2.0 * horizontal)


class VisionDetector:
    def __init__(
        self,
        phone_model_path="yolov8n.pt",
        drowsy_alarm_path="sounds/rooster.wav",
        phone_alarm_path="sounds/alarm.wav"
    ):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.phone_model = YOLO(phone_model_path)

        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.left_eye = [33, 160, 158, 133, 153, 144]
        self.right_eye = [362, 385, 387, 263, 373, 380]

        self.ear_threshold = 0.22
        self.eye_closed_start = None
        self.long_eye_close_counted = False
        self.last_drowsy_alarm_time = None
        self.phone_alarm_playing = False
        self.base_dir = Path(__file__).resolve().parent
        self.drowsy_alarm_path = self._resolve_sound_path(drowsy_alarm_path)
        self.phone_alarm_path = self._resolve_sound_path(phone_alarm_path)

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_results = self.face_detection.process(rgb_frame)
        mesh_results = self.face_mesh.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)

        result = {
            "face_results": face_results,
            "mesh_results": mesh_results,
            "hand_results": hand_results,
            "phone_boxes": [],
            "phone_detected": False,
            "eyes_closed": False,
            "long_eye_closed": False,
            "no_face": False,
            "ear": None,
            "hand_up": False,
            "bad_posture": False,
            "thumbs_up": False
        }

        if not face_results.detections:
            result["no_face"] = True

        # Telefon algÄ±lama
        small_frame = cv2.resize(frame, (320, 240))
        phone_results = self.phone_model(small_frame, imgsz=320, verbose=False)

        for phone_result in phone_results:
            for box in phone_result.boxes:
                class_id = int(box.cls[0])
                class_name = self.phone_model.names[class_id]
                confidence = float(box.conf[0])

                if class_name == "cell phone" and confidence > 0.45:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    scale_x = w / 320
                    scale_y = h / 240

                    x1 = int(x1 * scale_x)
                    x2 = int(x2 * scale_x)
                    y1 = int(y1 * scale_y)
                    y2 = int(y2 * scale_y)

                    result["phone_detected"] = True
                    result["phone_boxes"].append((x1, y1, x2, y2, confidence))

        if result["phone_detected"]:
            if not self.phone_alarm_playing and not self.long_eye_close_counted:
                self.play_alarm(self.phone_alarm_path)
                self.phone_alarm_playing = True
        else:
            self.phone_alarm_playing = False

        # GÃ¶z algÄ±lama
        if mesh_results.multi_face_landmarks:
            landmarks = mesh_results.multi_face_landmarks[0].landmark

            left_ear = eye_aspect_ratio(landmarks, self.left_eye, w, h)
            right_ear = eye_aspect_ratio(landmarks, self.right_eye, w, h)
            avg_ear = (left_ear + right_ear) / 2

            result["ear"] = avg_ear

            if avg_ear < self.ear_threshold:
                result["eyes_closed"] = True

                if self.eye_closed_start is None:
                    self.eye_closed_start = time.time()

                elapsed = time.time() - self.eye_closed_start
                result["eye_closed_elapsed"] = elapsed

                if elapsed >= 3:
                    result["long_eye_closed"] = True

                    current_time = time.time()

                    if self.last_drowsy_alarm_time is None:
                        self.play_alarm(self.drowsy_alarm_path)
                        self.last_drowsy_alarm_time = current_time

                    elif current_time - self.last_drowsy_alarm_time >= 5:
                        self.play_alarm(self.drowsy_alarm_path)
                        self.last_drowsy_alarm_time = current_time
            else:
                self.eye_closed_start = None
                self.long_eye_close_counted = False
                self.last_drowsy_alarm_time = None

                if not result["phone_detected"]:
                    winsound.PlaySound(None, winsound.SND_PURGE)

        # El yukarÄ± algÄ±lama
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                wrist = hand_landmarks.landmark[0]
                index_tip = hand_landmarks.landmark[8]

                if index_tip.y < wrist.y:
                    result["hand_up"] = True
# ğŸ‘ Thumbs Up algÄ±lama - sÄ±kÄ± kontrol
                thumb_tip = hand_landmarks.landmark[4]
                thumb_ip = hand_landmarks.landmark[3]
                thumb_mcp = hand_landmarks.landmark[2]

                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                ring_tip = hand_landmarks.landmark[16]
                pinky_tip = hand_landmarks.landmark[20]

                index_pip = hand_landmarks.landmark[6]
                middle_pip = hand_landmarks.landmark[10]
                ring_pip = hand_landmarks.landmark[14]
                pinky_pip = hand_landmarks.landmark[18]

                wrist = hand_landmarks.landmark[0]

                # El kamerada bÃ¼yÃ¼k mÃ¼?
                xs = [lm.x for lm in hand_landmarks.landmark]
                ys = [lm.y for lm in hand_landmarks.landmark]

                hand_width = max(xs) - min(xs)
                hand_height = max(ys) - min(ys)
                hand_area = hand_width * hand_height

                hand_is_big = hand_area > 0.06

                # BaÅŸparmak gerÃ§ekten yukarÄ±da mÄ±?
                thumb_is_up = (
                    thumb_tip.y < thumb_ip.y and
                    thumb_ip.y < thumb_mcp.y and
                    thumb_tip.y < wrist.y
                )

                # DiÄŸer parmaklar kapalÄ± mÄ±?
                other_fingers_closed = (
                    index_tip.y > index_pip.y and
                    middle_tip.y > middle_pip.y and
                    ring_tip.y > ring_pip.y and
                    pinky_tip.y > pinky_pip.y
                )

                if hand_is_big and thumb_is_up and other_fingers_closed:
                    result["thumbs_up"] = True

        return result

    def _resolve_sound_path(self, sound_path):
        path = Path(sound_path)

        if not path.is_absolute():
            path = self.base_dir / path

        return str(path)

    def play_alarm(self, alarm_path):
        try:
            winsound.PlaySound(
                alarm_path,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except Exception:
            winsound.Beep(1000, 700)

    def draw_results(self, frame, result):
        if result["face_results"].detections:
            for detection in result["face_results"].detections:
                bbox = detection.location_data.relative_bounding_box

                if bbox.width > 0.42 or bbox.height > 0.55:
                    result["bad_posture"] = True

        if result["ear"] is not None:
            cv2.putText(frame, f"EAR: {result['ear']:.2f}", (50, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        if result["eyes_closed"]:
            elapsed = result.get("eye_closed_elapsed", 0)
            cv2.putText(frame, f"Eyes Closed: {elapsed:.1f}s", (50, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if result["long_eye_closed"]:
            cv2.putText(frame, "WAKE UP!", (50, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)

        if result["hand_results"].multi_hand_landmarks:
            for hand_landmarks in result["hand_results"].multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

        if result["hand_up"]:
            cv2.putText(frame, "HAND UP", (50, 230),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)

        for x1, y1, x2, y2, confidence in result["phone_boxes"]:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, f"PHONE {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if result["phone_detected"]:
            cv2.putText(frame, "DON'T LOOK PHONE. FOCUS!", (50, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        if result["bad_posture"]:
            cv2.putText(frame, "SIT STRAIGHT!", (50, 410),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)

        if result["thumbs_up"]:
            cv2.putText(frame, "THUMBS UP", (50, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        return frame

