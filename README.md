# Color Sonic Pro

โปรเจกต์นี้ใช้สำหรับอ่านค่าสีบนหน้าจอแล้วกดปุ่ม (เปิดเอฟเฟคเสียง หรือสั่งงานอื่นๆ)

---

### Python 3.12

## Windows (PowerShell)

### 1. สร้าง Virtual Environment
```bash
python -m venv venv
```

### 2. เข้า Virtual Environment
```bash
.\venv\Scripts\activate
```

### 3. ติดตั้ง dependencies
```bash
pip install -r requirements.txt
```

### 4. รันโปรแกรม
```bash
python main.py
```

## macOS / Linux

### 1. สร้าง Virtual Environment
```bash
python3 -m venv venv
```

### 2. เข้า Virtual Environment
```bash
source venv/bin/activate
```

### 3. ติดตั้ง dependencies
```bash
pip install -r requirements.txt
```

### 4. รันโปรแกรม
```bash
python main.py  
```

## ทำเป็นไฟล์ exe

### 1. ติดตั้ง PyInstaller
```bash
pip install pyinstaller
```

### ตรวจสอบว่า install สำเร็จ
```bash
pyinstaller --version
```

### 2. สร้าง .exe (เข้าไปโฟลเดอร์โปรเจกต์)
```bash
pyinstaller --onefile --windowed --name "Color Sonic Pro 1.0" --icon="C:\path\to\icon.ico" main.py
```
- `--onefile` → รวมทุกอย่างเป็นไฟล์เดียว
- `--windowed` → ไม่เปิด console (เหมาะกับ GUI)
- `--name` → ชื่อไฟล์
- `--icon` → Icon

## Download .exe file for windows
*   [ดาวน์โหลด TikTokAutoPlayGame_1.0.exe](https://github.com/Jakkawal23/tiktok_live_play_context_game/blob/main/Color_Sonic_Pro_1.1.exe)

## Example web

![Example](images/20250923_01.png)
![Example](images/20250923_02.png)
![Example](images/20250923_03.png)
![Example](images/20250923_04.png)
![Example](images/20250923_05.png)
![Example](images/20250923_06.png)
![Example](images/20250923_07.png)