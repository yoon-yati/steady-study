 📚 Steady Study - Smart Study Planner

> AI-powered study planning to help you stay organized, focused, and achieve more every day.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://steady-study-jaaxku33eqwygkxorzx6cs.streamlit.app)

---

## 📖 About The Project

**Steady Study** is an all-in-one study management platform designed to help students plan, track, and improve their learning journey. From personalized study plans to interactive quizzes, everything you need is in one place.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📋 **Smart Planner** | Create and manage personalized study plans with goals and notes |
| ⏰ **Timetable Generator** | AI-powered schedule generation based on your subjects and availability |
| 🎓 **Learning Dashboard** | Track progress across multiple subjects with video roadmaps |
| 🧩 **Interactive Quiz** | Generate quizzes from topics or uploaded files (PDF, DOCX, PPTX, TXT) |
| 👤 **User Profiles** | Secure login/signup with profile picture and preferences |
| 📊 **Progress Tracking** | Monitor tasks, streaks, and overall learning progress |
| 📱 **Mobile Responsive** | Fully optimized for phone, tablet, and desktop |

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python)
- **Authentication**: Custom session-based login
- **Database**: JSON file storage (users.json, plans.json)
- **AI Integration**: Groq API for smart quiz generation
- **Styling**: Font Awesome Icons + Glassmorphism UI

---

## 🚀 Live Demo

🔗 **URL:** [https://steady-study-jaaxku33eqwygkxorzx6cs.streamlit.app](https://steady-study-jaaxku33eqwygkxorzx6cs.streamlit.app)

📱 **Scan QR Code to open on phone:**

![QR Code](steady_study_qr.png)

---

## 📂 Project Structure

```

Steady Study/
├── app.py                 # Main application entry point
├── auth.py                # Login/Signup authentication
├── dashboard.py           # Dashboard page
├── planner.py             # Study planner page
├── timetable.py           # Timetable generator page
├── learning.py            # Learning dashboard page
├── quiz.py                # Quiz page
├── settings.py            # User settings page
├── data_manager.py        # JSON data management
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
└── users.json             # User database (auto-generated)

```

---

## 🚦 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yoon-yati/steady-study.git
   cd steady-study
```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application
   ```bash
   streamlit run app.py
   ```
4. Open in browser
   · Local: http://localhost:8501
   · Network: http://YOUR_IP:8501 (for mobile testing)

---

📱 Mobile Setup

To test on your phone:

```bash
# Run with network access
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Find your IP address
ipconfig  # Windows
ifconfig  # Mac/Linux

# Open on phone:
http://YOUR_IP:8501
```

---

📦 Dependencies

```
streamlit>=1.28.0
Pillow>=9.0.0
PyPDF2>=3.0.0
python-docx>=0.8.11
python-pptx>=0.6.21
reportlab>=4.0.0
qrcode>=7.4.0
```

---

🔐 Environment Variables (Optional)

For AI quiz generation, create .streamlit/secrets.toml:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
```

---

🌟 Features in Detail

📋 Smart Planner

· Create study plans with subjects and deadlines
· Set goals with progress tracking
· Quick notes for ideas and reminders

⏰ Timetable Generator

· AI-generated schedules based on your subjects
· Customizable study hours and start times
· PDF download support

🎓 Learning Dashboard

· Subject roadmaps with video tutorials
· Track completed lessons
· Progress visualization

🧩 Interactive Quiz

· Generate quizzes from topics or uploaded files
· Multiple question types: MCQ, True/False, Fill Blank
· Time limits and automatic submission
· PDF export for questions and results

---

🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

---

📄 License

This project is for educational purposes. All rights reserved.

---

👩‍💻 Author

Yoon Yati Pyae

· GitHub: @yoon-yati
· Email: yoonyatipyae@gmail.com

---

🙏 Acknowledgments

· Streamlit - Amazing framework for data apps
· Font Awesome - Beautiful icons
· Unsplash - Background images
📞 Contact

For any questions or support, please reach out via:

· GitHub Issues
· Email: yoonyatipyae@gmail.com

---

⭐ If you like this project, please give it a star on GitHub!

Made with ❤️ by Yoon Yati Pyae and 2 members
