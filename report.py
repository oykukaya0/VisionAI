import json
import time
from datetime import datetime


def format_duration(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    sec = seconds % 60

    if minutes > 0:
        return f"{minutes} dk {sec} sn"
    return f"{sec} sn"


def create_report(study_start_time, focus_score, phone_total_time, eye_closed_total_time, away_count):
    study_end_time = time.time()
    study_duration = int(study_end_time - study_start_time)

    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "study_time": format_duration(study_duration),
        "final_focus_score": focus_score,
        "phone_usage_time": format_duration(phone_total_time),
        "sleepy_time": format_duration(eye_closed_total_time),
        "away_from_desk_count": away_count
    }


def save_json_report(report):
    with open("focus_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n========== TODAY'S REPORT ==========")
    print(f"Study Time          : {report['study_time']}")
    print(f"Focus Score         : {report['final_focus_score']}%")
    print(f"Phone Usage Time    : {report['phone_usage_time']}")
    print(f"Sleepy Time         : {report['sleepy_time']}")
    print(f"Away From Desk      : {report['away_from_desk_count']}")
    print("====================================")