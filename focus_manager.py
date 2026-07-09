import cv2
import time
import winsound


class FocusManager:
    def __init__(self):
        self.focus_score = 100
        self.last_score_update = time.time()
        self.study_start_time = time.time()

        self.phone_total_time = 0
        self.eye_closed_total_time = 0
        self.away_count = 0

        self.phone_start_time = None
        self.eye_closed_start_time = None

        self.away_was_detected = False
        self.break_start_time = time.time()
        self.break_warning_shown = False

    def update(self, phone_detected, eyes_closed, long_eye_closed, no_face, bad_posture):
        current_time = time.time()
        study_elapsed = current_time - self.break_start_time

        # Telefon süresi
        if phone_detected:
            if self.phone_start_time is None:
                self.phone_start_time = current_time
        else:
            if self.phone_start_time is not None:
                self.phone_total_time += current_time - self.phone_start_time
                self.phone_start_time = None

        # Uyuklama süresi: sadece 3 saniyeden uzun göz kapanması sayılır
        if eyes_closed:
            if self.eye_closed_start_time is None:
                self.eye_closed_start_time = current_time
        else:
            if self.eye_closed_start_time is not None:
                closed_duration = current_time - self.eye_closed_start_time

                if closed_duration >= 3:
                    self.eye_closed_total_time += closed_duration

                self.eye_closed_start_time = None

        # Masadan uzaklaşma sayacı kalabilir
        if no_face and not self.away_was_detected:
            self.away_count += 1
            self.away_was_detected = True
        elif not no_face:
            self.away_was_detected = False

        # Focus Score daha yavaş düşsün
        if current_time - self.last_score_update >= 1:
            if phone_detected:
                self.focus_score -= 1

            if long_eye_closed:
                self.focus_score -= 1

            if no_face:
                self.focus_score -= 1

            if not phone_detected and not eyes_closed and not no_face and not bad_posture:
                self.focus_score += 1
            if bad_posture:
                self.focus_score -= 1

            self.focus_score = max(0, min(100, self.focus_score))
            self.last_score_update = current_time

        if study_elapsed >= 45 * 60 and not self.break_warning_shown:
            winsound.PlaySound(
                "sounds/rooster.wav",
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )

            self.break_warning_shown = True
            
            self.break_warning_shown = True

    def draw_focus_ui(self, frame):
        if self.focus_score >= 80:
            score_color = (0, 255, 0)
        elif self.focus_score >= 50:
            score_color = (0, 255, 255)
        else:
            score_color = (0, 0, 255)
        if self.break_warning_shown:

            cv2.putText(
                frame,
                "BREAK TIME!",
                (330,120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,165,255),
                3
            )

            cv2.putText(
                frame,
                "Take a 5 minute break",
                (260,160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,255),
                2
            )

        cv2.putText(frame, f"Focus Score: {self.focus_score}%", (380, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, score_color, 2)

        bar_x, bar_y, bar_width, bar_height = 380, 60, 220, 20
        filled_width = int(bar_width * self.focus_score / 100)

        cv2.rectangle(frame, (bar_x, bar_y),
                      (bar_x + bar_width, bar_y + bar_height),
                      (255, 255, 255), 2)

        cv2.rectangle(frame, (bar_x, bar_y),
                      (bar_x + filled_width, bar_y + bar_height),
                      score_color, -1)

        return frame