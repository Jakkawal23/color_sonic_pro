import mss
from PIL import Image
from pynput import mouse, keyboard
import time

# Mapping สี → ความหมาย
color_map = {
    (107, 203, 119): "ถูกต้อง (เขียว)",
    (181, 226, 220): "ใกล้เคียง (ฟ้า)",
    (244, 218, 146): "บริบท (ส้ม)",
    (247, 192, 181): "ไม่ใกล้เคียง (แดง)",
    (244, 237, 226): "ยังไม่รู้ (เทา)",
    (255, 251, 245): "พื้นหลัง (ขาว)"
}

selected_pos = None
confirmed = False

def get_color(x, y):
    with mss.mss() as sct:
        screenshot = sct.grab({"top": y, "left": x, "width": 1, "height": 1})
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img.getpixel((0, 0))

def check_answer(pixel):
    for key, meaning in color_map.items():
        if all(abs(pixel[i] - key[i]) < 40 for i in range(3)):  # ยอมคลาดเคลื่อนได้
            return meaning
    return "ไม่รู้จักสี"

# Mouse listener
def on_click(x, y, button, pressed):
    global selected_pos
    if pressed:
        selected_pos = (x, y)
        print(f"คุณเลือกตำแหน่ง X={x}, Y={y}")
        print("กด y เพื่อยืนยัน หรือ n เพื่อเลือกใหม่...")
        return False  # หยุด listener รอบนี้

# Keyboard listener
def on_press(key):
    global selected_pos, confirmed
    if selected_pos is None:
        return
    try:
        if key.char == 'y':
            confirmed = True
            return False
        elif key.char == 'n':
            selected_pos = None
            print("โอเค เลือกใหม่อีกครั้ง...")
            return False
    except AttributeError:
        pass

if __name__ == "__main__":
    print("โปรแกรมเริ่ม → คลิกเมาส์ซ้ายตรงจุดที่ต้องการ")

    # เลือกตำแหน่ง
    while not confirmed:
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
        with keyboard.Listener(on_press=on_press) as k_listener:
            k_listener.join()

    print("เริ่มตรวจจับสีที่ตำแหน่ง:", selected_pos)

    last_status = None
    try:
        while True:
            pixel = get_color(*selected_pos)
            status = check_answer(pixel)
            if status != last_status:
                print(f"Pixel: {pixel}, สถานะ: {status}")
                last_status = status
            time.sleep(0.1)  # ลดการใช้ CPU
    except KeyboardInterrupt:
        print("โปรแกรมหยุดแล้ว")
