# DADS5001 Data Analytics Tools

[![DADS5001](https://img.shields.io/badge/DADS5001-Data%20Analytics%20Tools-blue)](https://github.com/puwadonsri/DADS5001-Final-Project)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)

> รวมโปรเจกต์วิชา DADS5001 Data Analytics Tools  
> ประกอบด้วย 2 โปรเจกต์หลัก ได้แก่ Live Chat Analytics และ Project Data Analysis

---

## โครงสร้างโปรเจกต์

```
DADS5001_Data_Analytics_Tools/
├── Live_Chat_Analytics/        # วิเคราะห์หุ้นไทยจาก YouTube Live Chat แบบ Real-time
│   ├── main.py                 # Dash Web Dashboard (6 หน้า)
│   ├── YoutubeLive.py          # YouTube Live Chat Scraper
│   ├── YoutubeAnalytics.py     # วิเคราะห์การพูดถึงหุ้น SET
│   ├── generate_charts.py      # สร้างภาพกราฟสำหรับ Dashboard
│   ├── requirements.txt
│   ├── images/                 # ภาพตัวอย่างกราฟ
│   └── json_dataset/           # ข้อมูล JSON และ CSV
│
├── Project/                    # วิเคราะห์การกระจุกตัวของอสังหาริมทรัพย์ตามแนวรถไฟฟ้า
│   ├── DADS5001_PMiniProject.ipynb   # Jupyter Notebook
│   ├── README.md
│   └── Dataset/                # ข้อมูลโครงการที่อยู่อาศัยและสถานีรถไฟฟ้า
│
└── README.md                   # ไฟล์นี้
```

---

## โปรเจกต์ย่อย

### 1. Live Chat Analytics 📊

วิเคราะห์กระแสหุ้นไทยจาก YouTube Live Chat แบบ Real-time  
ดึงข้อมูลจากช่อง MONEY HERO เพื่อระบุหุ้น SET ที่ถูกพูดถึงมากที่สุดระหว่างถ่ายทอดสด

- **Dashboard 6 หน้า** — Top 10 Stocks, All Stocks, Viewers by Date, Top Viewers, Word Cloud, Mentions Over Time
- **เทคโนโลยี**: Python, Dash (Plotly), MongoDB, pytchat
- [รายละเอียดเพิ่มเติม →](Live_Chat_Analytics/README.md)

### 2. Project Data Analysis 🏠

วิเคราะห์การกระจุกตัวของการพัฒนาอสังหาริมทรัพย์ตามแนวรถไฟฟ้า  
ใช้ข้อมูลโครงการที่อยู่อาศัย >23,000 โครงการ และข้อมูลสถานีรถไฟฟ้า >300 สถานี

- **คำถามหลัก**: อสังหาฯ กระจุกตัวตามแนวรถไฟฟ้าหรือไม่? ราคาแพงขึ้นตามระยะทางหรือไม่?
- **เทคโนโลยี**: Python, Pandas, Plotly, Matplotlib
- [รายละเอียดเพิ่มเติม →](Project/README.md)

---

## ผู้จัดทำ

1. 6420422026 ภูวดล ศรีธรรม
2. 6420422019 ขนิษฐา ปะอันทัง
