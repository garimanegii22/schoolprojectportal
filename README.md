# 🏆 School House Championship Management System

A complete, responsive, web-based Inter-House Competition Management System built for schools. It replaces manual scorekeeping and paper records with a robust Python Flask and MySQL relational database backend, paired with a modern dark-mode Tailwind CSS interface derived from your original dashboard design[cite: 1].

---

## 🚀 Key Features

* **Public Read-Only Dashboard:** Live house standings, leaderboard rankings, active competition schedules, history logs, universal search, and a Chart.js points distribution chart[cite: 1].
* **Secure Administrator Panel:** Password-protected teacher login (using Werkzeug password hashing and Flask-Login) allowing authorized staff to manage students, create events, register participants, and record podium results.
* **Automatic Standings Calculation:** House points and 1st place wins are calculated dynamically from actual MySQL database records (never hardcoded).
* **CSV Export:** Instantly export house standings and scores to a CSV spreadsheet[cite: 1].
* **Fully Responsive:** Optimized for mobile phones, tablets, laptops, and desktop displays.

---

## 🛠️ Technology Stack

* **Backend Language:** Python 3.10+
* **Web Framework:** Flask
* **Database & ORM:** MySQL & SQLAlchemy
* **Authentication:** Flask-Login & Werkzeug Security
* **Frontend:** HTML5, Tailwind CSS, JavaScript, Jinja2 Templates, Chart.js, FontAwesome

---

## ⚙️ Local Setup Guide

1. **Clone or Download the Project Folder** onto your computer.
2. **Install Python** (version 3.10 or higher).
3. **Open your terminal / VS Code terminal** inside the project root folder (`school_house_portal/`).
4. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate