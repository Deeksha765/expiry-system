# 🛡️ ExpiryGuard — Product & Medicine Expiry Analysis System

A web-based system to scan product barcodes and analyze 
expiry dates using Python Flask, MySQL, and Chart.js.

## 🚀 Features
- User Login (Admin & User roles)
- Barcode/QR Scanner using browser camera
- Manual product search
- Expiry classification (Safe / Near-Expiry / Expired)
- Analytics dashboard with charts
- Product CRUD operations
- Color-coded expiry status indicators

## 💻 Technology Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Backend:** Python Flask
- **Database:** MySQL
- **Analysis:** Pandas
- **Charts:** Chart.js
- **Scanner:** ZXing / QuaggaJS

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/expiry-system.git
cd expiry-system
```

### 2. Install Python packages
```bash
pip install flask mysql-connector-python pandas werkzeug
```

### 3. Setup MySQL Database
- Create database: `expiry_system`
- Run the SQL from `database/schema.sql`

### 4. Configure database
Edit `config.py` and set your MySQL password:
```python
DB_PASSWORD = 'your_password'
```

### 5. Run the application
```bash
python app.py
```

### 6. Open in browser
```
http://127.0.0.1:5000
```

## 🔑 Demo Login
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| User | john | user123 |

## 📸 Screenshots
Dashboard with analytics charts and expiry status overview.

## 👨‍🎓 Project Info
- BCA Final Year Project 2024-2025
```
```
3. Press Ctrl+S to save
```

---

## ✅ Step 7 — Create Database SQL File
```
1. In VS Code create folder: database
2. Inside that folder create: schema.sql
3. Paste all your SQL code 
   (CREATE TABLE + INSERT statements)
   from Phase 3 of the project
4. Press Ctrl+S
