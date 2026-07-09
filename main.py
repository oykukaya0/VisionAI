import cv2
import time

from detector import VisionDetector
from focus_manager import FocusManager
from report import create_report, save_json_report
from ui import show_report_window


def main():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        print("Kamera açılamadı!")
        return

    detector = VisionDetector(
        phone_model_path="yolov8n.pt",
        drowsy_alarm_path="sounds/alarm.wav",
        phone_alarm_path="sounds/rooster.wav"
    )

    focus = FocusManager()
    thumbs_up_start = None
    while True:
        ret, frame = camera.read()

        if not ret:
            print("Kamera görüntüsü alınamadı!")
            break

        frame = cv2.flip(frame, 1)

        result = detector.process_frame(frame)

        frame = detector.draw_results(frame, result)
        if result["thumbs_up"]:
            if thumbs_up_start is None:
                thumbs_up_start = time.time()

            thumbs_elapsed = time.time() - thumbs_up_start

            cv2.putText(
                frame,
                f"Hold 👍 to open report: {thumbs_elapsed:.1f}/2.0s",
                (40, 450),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            if thumbs_elapsed >= 2:
                break
        else:
            thumbs_up_start = None

        focus.update(
            phone_detected=result["phone_detected"],
            eyes_closed=result["eyes_closed"],
            long_eye_closed=result["long_eye_closed"],
            no_face=result["no_face"],
            bad_posture=result["bad_posture"]
        )


        frame = focus.draw_focus_ui(frame)

        cv2.imshow("VisionAI", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    now = time.time()

# Telefon hâlâ eldeyse süreyi tamamla
    if focus.phone_start_time is not None:
        focus.phone_total_time += now - focus.phone_start_time
        focus.phone_start_time = None

    if focus.eye_closed_start_time is not None:
        closed_duration = now - focus.eye_closed_start_time

        if closed_duration >= 3:
            focus.eye_closed_total_time += closed_duration

        focus.eye_closed_start_time = None

    report = create_report(
        study_start_time=focus.study_start_time,
        focus_score=focus.focus_score,
        phone_total_time=focus.phone_total_time,
        eye_closed_total_time=focus.eye_closed_total_time,
        away_count=focus.away_count
    )

    save_json_report(report)
    show_report_window(report)


if __name__ == "__main__":
    main()
