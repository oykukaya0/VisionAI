import tkinter as tk
from tkinter import ttk
import asyncio
import edge_tts
from playsound import playsound
import os


def duration_to_seconds(text):
    total = 0

    if "dk" in text:
        minute_part = text.split("dk")[0].strip()
        total += int(minute_part) * 60

        rest = text.split("dk")[1].strip()
        if "sn" in rest:
            second_part = rest.split("sn")[0].strip()
            if second_part:
                total += int(second_part)

    elif "sn" in text:
        second_part = text.split("sn")[0].strip()
        total += int(second_part)

    return total


def create_coach_message(report):
    study_seconds = duration_to_seconds(report["study_time"])
    phone_seconds = duration_to_seconds(report["phone_usage_time"])
    sleepy_seconds = duration_to_seconds(report["sleepy_time"])

    phone_ratio = phone_seconds / study_seconds if study_seconds > 0 else 0
    sleepy_ratio = sleepy_seconds / study_seconds if study_seconds > 0 else 0

    if phone_ratio >= 0.5 and sleepy_ratio >= 0.5:
        return (
            "Bugünlük bence bu kadar çalışma yeter. "
            "Yarın daha iyi bir performans bekliyorum. "
            "Uyu ve odağını toparla, lütfen."
        )

    elif phone_ratio >= 0.25 and sleepy_ratio >= 0.25:
        return (
            "Bugün hem telefon dikkatini dağıtmış, hem de biraz yorgun görünüyorsun."
            "Kısa bir mola vermen iyi olabilir."
            "Odağını toparlayıp sonra devam edebilirsin."
        )

    elif phone_ratio < 0.25 and sleepy_ratio < 0.25:
        return (
            "Güzel bir çalışma oldu."
            "Odaklanabildin ve telefona çok az baktın."
            "Harika gidiyorsun."
        )

    elif sleepy_ratio >= 0.5:
        return (
            "Biraz yorgun görünüyorsun."
            "Dinlensen iyi olur."
            "Uyuyup daha dinç şekilde devam edebilirsin."
        )

    elif phone_ratio >= 0.25:
        return (
            "Telefon dikkatini biraz fazla dağıtmış gibi görünüyor."
            "Bir sonraki çalışmada telefonu biraz daha uzak tutmanı öneririm."
        )

    else:
        return (
            "Çalışma tamamlandı. "
            "Bugünkü performansın fena değil. "
            "Biraz dinlenip sonra devam edebilirsin."
        )


async def speak_with_edge_tts(text):
    communicate = edge_tts.Communicate(
        text=text,
        voice="tr-TR-EmelNeural"
    )
    await communicate.save("coach_voice.mp3")


def speak_report(report):
    text = create_coach_message(report)

    try:
        if os.path.exists("coach_voice.mp3"):
            os.remove("coach_voice.mp3")

        asyncio.run(speak_with_edge_tts(text))
        playsound("coach_voice.mp3")

    except Exception as e:
        print("Sesli asistan çalışmadı:", e)


def show_report_window(report):
    root = tk.Tk()
    root.title("VisionAI Focus Report")
    root.geometry("420x520")
    root.configure(bg="#111827")

    title = tk.Label(
        root,
        text="VisionAI Focus Report",
        font=("Arial", 20, "bold"),
        fg="white",
        bg="#111827"
    )
    title.pack(pady=20)

    score = report["final_focus_score"]

    score_label = tk.Label(
        root,
        text=f"{score}%",
        font=("Arial", 48, "bold"),
        fg="#22c55e" if score >= 80 else "#facc15" if score >= 50 else "#ef4444",
        bg="#111827"
    )
    score_label.pack()

    tk.Label(
        root,
        text="Final Focus Score",
        font=("Arial", 12),
        fg="#d1d5db",
        bg="#111827"
    ).pack(pady=5)

    progress = ttk.Progressbar(
        root,
        length=280,
        mode="determinate",
        maximum=100,
        value=score
    )
    progress.pack(pady=20)

    card = tk.Frame(root, bg="#1f2937")
    card.pack(padx=30, pady=10, fill="both")

    def add_stat(label, value):
        row = tk.Frame(card, bg="#1f2937")
        row.pack(fill="x", padx=20, pady=12)

        tk.Label(
            row,
            text=label,
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1f2937"
        ).pack(side="left")

        tk.Label(
            row,
            text=str(value),
            font=("Arial", 12),
            fg="#93c5fd",
            bg="#1f2937"
        ).pack(side="right")

    add_stat("Study Time", report["study_time"])
    add_stat("Phone Usage Time", report["phone_usage_time"])
    add_stat("Sleept Time", report["sleepy_time"])
    add_stat("Away From Desk", report["away_from_desk_count"])

    tk.Label(
        root,
        text=report["date"],
        font=("Arial", 10),
        fg="#9ca3af",
        bg="#111827"
    ).pack(pady=15)

    close_btn = tk.Button(
        root,
        text="Close",
        command=root.destroy,
        font=("Arial", 12, "bold"),
        bg="#2563eb",
        fg="white",
        padx=30,
        pady=8
    )
    close_btn.pack(pady=10)

    root.after(800, lambda: speak_report(report))
    root.mainloop()