

https://github.com/user-attachments/assets/eb93c8ab-7804-4f10-bd59-fe8b37133d0a

# 🤖 VisionAI - AI Powered Study Focus Assistant

VisionAI is an AI-powered desktop application that helps students improve their study habits using Computer Vision.

Using a webcam, the system monitors the user's focus level in real time by analyzing facial features, eye movements, posture, hand gestures, and mobile phone usage. At the end of each study session, VisionAI generates a detailed focus report and provides personalized voice feedback.

---

# 📸 Features

## 👤 Face Detection

VisionAI continuously detects the user's face using MediaPipe Face Detection.

If no face is detected, the system assumes that the user has left the desk and records this event.

---

## 👀 Eye Tracking & Drowsiness Detection

VisionAI calculates the Eye Aspect Ratio (EAR) using MediaPipe Face Mesh.

Features:

- Blink detection is ignored.
- Eyes must remain closed for at least **3 seconds** before being considered drowsiness.
- Alarm sounds after 3 seconds.
- If eyes remain closed, the alarm repeats every 5 seconds.
- Total drowsiness duration is stored in the report.

---

## 📱 Mobile Phone Detection

A YOLOv8 object detection model continuously searches for the **cell phone** class.

If a phone is detected:

- Red warning appears on screen.
- Alarm plays.
- Total phone usage time is recorded.
- Focus score decreases.

---

## 🪑 Posture Analysis

VisionAI estimates whether the user is sitting too close or leaning forward.

When poor posture is detected:

```
SIT STRAIGHT!
```

appears on screen.

---

## 👍 Hand Gesture Recognition

MediaPipe Hands tracks 21 hand landmarks.

VisionAI recognizes:

- Hand Up
- 👍 Thumbs Up

The report only opens if:

- A clear thumbs-up gesture is detected.
- The hand is large enough in the camera.
- The gesture is held continuously for **2 seconds**.

This prevents accidental report generation.

---

## ☕ Break Reminder

After **45 minutes** of continuous study:

```
BREAK TIME!
Take a 5 minute break.
```

is displayed.

A notification sound is also played.

---

## 📊 Focus Score

VisionAI calculates a dynamic focus score between **0 and 100**.

Focus decreases when:

- Phone detected
- Long eye closure
- No face detected
- Bad posture

Focus slowly increases while studying correctly.

---

## 📈 Study Report

At the end of each session VisionAI generates a report containing:

- Study Time
- Final Focus Score
- Phone Usage Time
- Drowsiness Time
- Away From Desk Count

---

## 🔊 AI Voice Coach

After the report opens, VisionAI generates a personalized Turkish voice response using Microsoft Edge TTS.

Example feedback:

> Güzel bir çalışma oldu. Telefona oldukça az baktın. Harika gidiyorsun.

or

> Bugün biraz yorgun görünüyorsun. Dinlenmeni öneriyorum.

or

> Bugün hem telefona fazla baktın hem de oldukça yorgundun. Bugünlük bu kadar çalışma yeter.

The feedback changes depending on user performance.

---

# 🛠 Technologies

- Python
- OpenCV
- MediaPipe
- YOLOv8
- Ultralytics
- Tkinter
- Edge TTS
- NumPy
- Winsound

---

# 📂 Project Structure

```
VisionAI/
│
├── detector.py
├── focus_manager.py
├── report.py
├── ui.py
├── main.py
├── requirements.txt
├── README.md
│
├── sounds/
│   ├── alarm.wav
│   └── rooster.wav
│
└── assets/
```

---

# ⚙ Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/VisionAI.git
```

Enter project directory.

```bash
cd VisionAI
```

Create virtual environment.

```bash
py -3.12 -m venv venv
```

Activate environment.

Windows

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Run

```bash
python main.py
```

---

# 📖 How VisionAI Works

Every camera frame follows this pipeline.

```
Camera

↓

Face Detection

↓

Face Mesh

↓

Eye Aspect Ratio

↓

Phone Detection (YOLOv8)

↓

Hand Detection

↓

Focus Score Update

↓

UI Rendering

↓

Report Generation

↓

AI Voice Feedback
```

---

# 🧠 Eye Aspect Ratio (EAR)

VisionAI uses the Eye Aspect Ratio to determine whether the user's eyes are closed.

```
EAR =
(vertical distance 1 + vertical distance 2)
--------------------------------------------
       2 × horizontal distance
```

If

```
EAR < 0.22
```

the eye is considered closed.

---

# 📱 Phone Detection

YOLOv8 detects objects belonging to

```
cell phone
```

Only detections above

```
confidence > 0.45
```

are accepted.

---

# 📊 Focus Score Logic

Initial score:

```
100
```

Every second:

| Event | Score |
|--------|------:|
| Phone detected | -1 |
| Eyes closed (3s+) | -1 |
| Away from desk | -1 |
| Bad posture | -1 |
| Good focus | +1 |

Score always remains between

```
0 - 100
```

---

# 🚀 Future Improvements

- Robot avatar replacing user's face
- Face animation
- Weekly statistics
- SQLite database
- PDF reports
- User accounts
- Cloud synchronization
- AI productivity recommendations
- Study history dashboard
- Mobile application

---

# 🎯 Purpose

VisionAI aims to improve study efficiency by providing real-time AI-based feedback through computer vision technologies.

Instead of simply detecting faces or eyes, VisionAI evaluates overall study behavior and transforms it into meaningful productivity insights.

---

# 👨‍💻 Developers

Computer Engineering & Software Engineering Students

AI • Computer Vision • Deep Learning • Python
