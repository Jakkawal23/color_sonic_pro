import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import mss
from PIL import Image
import time
import pynput.mouse
from tkinter import ttk

default_colors = [
    {"rgb": (107, 203, 119), "label": "ถูกต้อง (เขียว)", "active": True, "action": [], "action_active": False},
    {"rgb": (181, 226, 220), "label": "ใกล้เคียง (ฟ้า)", "active": True, "action": [], "action_active": False},
    {"rgb": (244, 218, 146), "label": "บริบท (ส้ม)", "active": True, "action": [], "action_active": False},
    {"rgb": (247, 192, 181), "label": "ไม่ใกล้เคียง (แดง)", "active": True, "action": [], "action_active": False},
    {"rgb": (244, 237, 226), "label": "ยังไม่รู้ (เทา)", "active": True, "action": [], "action_active": False},
    {"rgb": (255, 251, 245), "label": "พื้นหลัง (ขาว)", "active": True, "action": [], "action_active": False},
]

class ColorDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Sonic Pro")
        # self.root.iconbitmap("color_sonic_pro.ico")
        self.selected_pos = None
        self.running = False
        self.last_status = None
        self.listener_thread = None
        self.detect_thread = None
        self.color_list = [c.copy() for c in default_colors]
        self.tolerance = 30  # default tolerance

        # Top: Position display & select button
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.pos_label = tk.Label(top_frame, text="ตำแหน่ง: ยังไม่ได้เลือก", font=("Arial", 12))
        self.pos_label.pack(side=tk.LEFT)
        self.select_btn = tk.Button(top_frame, text="เลือกตำแหน่ง", command=self.select_position)
        self.select_btn.pack(side=tk.RIGHT)
        self.adv_btn = tk.Button(top_frame, text="Advance", command=self.open_advance_dialog)
        self.adv_btn.pack(side=tk.RIGHT, padx=5)

        # Middle: Log/chat area
        self.log_area = scrolledtext.ScrolledText(root, height=15, state='disabled', font=("Consolas", 11))
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Bottom: Start/Stop buttons
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        self.start_btn = tk.Button(bottom_frame, text="Start", command=self.start_detect, state='normal', bg="#5cb85c", fg="white")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(bottom_frame, text="Stop", command=self.stop_detect, state='disabled', bg="#d9534f", fg="white")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def select_position(self):
        self.log("กรุณาคลิกตำแหน่งบนหน้าจอ...")
        self.select_btn.config(state='disabled')
        self.stop_detect()  # auto stop เมื่อเริ่มเลือกตำแหน่ง
        def on_click(x, y, button, pressed):
            if pressed:
                self.selected_pos = (x, y)
                self.pos_label.config(text=f"ตำแหน่ง: X={x}, Y={y}")
                self.log(f"เลือกตำแหน่ง X={x}, Y={y}")
                self.select_btn.config(state='normal')
                return False
        self.listener_thread = threading.Thread(target=lambda: pynput.mouse.Listener(on_click=on_click).run())
        self.listener_thread.start()
        
    def open_advance_dialog(self):
        from tkinter import ttk
        adv_win = tk.Toplevel(self.root)
        adv_win.title("จัดการสีและสถานะ")
        # adv_win.iconbitmap("color_sonic_pro.ico")

        # Tolerance input (top row)
        tk.Label(adv_win, text="Tolerance:").grid(row=0, column=0, padx=2, sticky="w")
        tol_entry = tk.Entry(adv_win, width=5, validate='key')
        tol_entry['validatecommand'] = (tol_entry.register(lambda v: v.isdigit() or v==''), '%P')
        tol_entry.grid(row=0, column=1, padx=2, sticky="w")
        tol_entry.insert(0, str(self.tolerance))

        def update_tolerance():
            val = tol_entry.get()
            if val.isdigit():
                self.tolerance = int(val)
                self.log(f"Tolerance ถูกตั้งค่าใหม่เป็น {self.tolerance}")

        tol_entry.bind('<FocusOut>', lambda e: update_tolerance())
        tol_entry.bind('<Return>', lambda e: update_tolerance())

        # Separator line between tolerance and add colorฟ
        sep_top = ttk.Separator(adv_win, orient='horizontal')
        sep_top.grid(row=1, column=0, columnspan=11, sticky="ew", pady=8)

        # Add color section (now row 2)
        tk.Label(adv_win, text="R:").grid(row=2, column=0, padx=2)
        r_entry = tk.Entry(adv_win, width=5, validate='key')
        r_entry['validatecommand'] = (r_entry.register(lambda v: v.isdigit() or v==''), '%P')
        r_entry.grid(row=2, column=1, padx=2)
        tk.Label(adv_win, text="G:").grid(row=2, column=2, padx=2)
        g_entry = tk.Entry(adv_win, width=5, validate='key')
        g_entry['validatecommand'] = (g_entry.register(lambda v: v.isdigit() or v==''), '%P')
        g_entry.grid(row=2, column=3, padx=2)
        tk.Label(adv_win, text="B:").grid(row=2, column=4, padx=2)
        b_entry = tk.Entry(adv_win, width=5, validate='key')
        b_entry['validatecommand'] = (b_entry.register(lambda v: v.isdigit() or v==''), '%P')
        b_entry.grid(row=2, column=5, padx=2)
        # ปุ่มเลือกสีจากหน้าจอ (ด้านบนตาราง)
        def pick_color_for_add():
            self.log("กรุณาคลิกตำแหน่งบนหน้าจอเพื่อเลือกสี...")
            def on_click(x, y, button, pressed):
                if pressed:
                    rgb = self.get_color(x, y)
                    r_entry.delete(0, tk.END)
                    r_entry.insert(0, str(rgb[0]))
                    g_entry.delete(0, tk.END)
                    g_entry.insert(0, str(rgb[1]))
                    b_entry.delete(0, tk.END)
                    b_entry.insert(0, str(rgb[2]))
                    self.log(f"เลือกสีจากหน้าจอ: {rgb}")
                    pick_add_btn.config(state='normal')
                    return False
            pick_add_btn.config(state='disabled')
            threading.Thread(target=lambda: pynput.mouse.Listener(on_click=on_click).run()).start()
        pick_add_btn = tk.Button(adv_win, text="เลือกสีจากหน้าจอ", command=pick_color_for_add)
        pick_add_btn.grid(row=2, column=6, padx=2)
        tk.Label(adv_win, text="Label สถานะ:").grid(row=2, column=7, padx=2)
        label_entry = tk.Entry(adv_win, width=20)
        label_entry.grid(row=2, column=8, padx=2)
        add_btn = tk.Button(adv_win, text="เพิ่ม", command=lambda: add_color())
        add_btn.grid(row=2, column=9, padx=2)

        # Table with header
        columns = ("No", "R", "G", "B", "Label", "Active", "Action Active")
        tree = ttk.Treeview(adv_win, columns=columns, show="headings", selectmode="browse", height=8)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=60 if col not in ["Label", "Action Active"] else 160, anchor=tk.CENTER)
        tree.grid(row=3, column=0, columnspan=11, padx=5, pady=5)

        def refresh_table():
            tree.delete(*tree.get_children())
            for idx, c in enumerate(self.color_list, 1):
                r, g, b = c["rgb"]
                label = c["label"]
                active = "✅" if c["active"] else "❌"
                action_active = "✅" if c.get("action_active") else "❌"
                tree.insert("", "end", iid=idx-1, values=(idx, r, g, b, label, active, action_active))

        refresh_table()

        def add_color():
            r = r_entry.get()
            g = g_entry.get()
            b = b_entry.get()
            label = label_entry.get().strip()
            try:
                r = int(r)
                g = int(g)
                b = int(b)
            except Exception:
                messagebox.showerror("Error", "RGB ต้องเป็นตัวเลขเท่านั้น")
                return
            if not label:
                messagebox.showerror("Error", "กรุณากรอก Label สถานะ")
                return
            self.color_list.append({"rgb": (r, g, b), "label": label, "active": True, "action": [], "action_active": False})
            refresh_table()
            self.log(f"เพิ่มสีใหม่: ({r}, {g}, {b}) → {label}")
            r_entry.delete(0, tk.END)
            g_entry.delete(0, tk.END)
            b_entry.delete(0, tk.END)
            label_entry.delete(0, tk.END)

        # Edit color/label (double click)
        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            # ทำสำเนาข้อมูลสีไว้ก่อนแก้ไข
            orig_item = self.color_list[idx].copy()
            item = self.color_list[idx].copy()
            edit_win = tk.Toplevel(adv_win)
            edit_win.title("แก้ไขข้อมูลสี")
            # edit_win.iconbitmap("color_sonic_pro.ico")
            tk.Label(edit_win, text="R:").grid(row=0, column=0)
            r_edit = tk.Entry(edit_win, width=5)
            r_edit.insert(0, str(item["rgb"][0]))
            r_edit.grid(row=0, column=1)
            tk.Label(edit_win, text="G:").grid(row=0, column=2)
            g_edit = tk.Entry(edit_win, width=5)
            g_edit.insert(0, str(item["rgb"][1]))
            g_edit.grid(row=0, column=3)
            tk.Label(edit_win, text="B:").grid(row=0, column=4)
            b_edit = tk.Entry(edit_win, width=5)
            b_edit.insert(0, str(item["rgb"][2]))
            b_edit.grid(row=0, column=5)
            # ปุ่มเลือกสีจากหน้าจอ
            def pick_color_from_screen():
                self.log("กรุณาคลิกตำแหน่งบนหน้าจอเพื่อเลือกสี...")
                def on_click(x, y, button, pressed):
                    if pressed:
                        rgb = self.get_color(x, y)
                        r_edit.delete(0, tk.END)
                        r_edit.insert(0, str(rgb[0]))
                        g_edit.delete(0, tk.END)
                        g_edit.insert(0, str(rgb[1]))
                        b_edit.delete(0, tk.END)
                        b_edit.insert(0, str(rgb[2]))
                        self.log(f"เลือกสีจากหน้าจอ: {rgb}")
                        pick_btn.config(state='normal')
                        return False
                pick_btn.config(state='disabled')
                threading.Thread(target=lambda: pynput.mouse.Listener(on_click=on_click).run()).start()
            pick_btn = tk.Button(edit_win, text="เลือกสีจากหน้าจอ", command=pick_color_from_screen)
            pick_btn.grid(row=0, column=6, padx=5)
            tk.Label(edit_win, text="Label สถานะ:").grid(row=0, column=7)
            label_edit = tk.Entry(edit_win, width=20)
            label_edit.insert(0, item["label"])
            label_edit.grid(row=0, column=8)

            # Active checkbox
            active_var = tk.BooleanVar(value=item.get("active", True))
            active_cb = tk.Checkbutton(edit_win, text="Active", variable=active_var)
            active_cb.grid(row=1, column=0, columnspan=2, pady=5)

            # Action active checkbox
            action_active_var = tk.BooleanVar(value=item.get("action_active", False))
            action_active_cb = tk.Checkbutton(edit_win, text="Action Active", variable=action_active_var)
            action_active_cb.grid(row=1, column=2, columnspan=2, pady=5)

            # Action input field
            tk.Label(edit_win, text="Action Keys:").grid(row=2, column=0)
            action_keys_var = tk.StringVar(value=" + ".join(item.get("action", [])))
            action_keys_entry = tk.Entry(edit_win, textvariable=action_keys_var, width=30)
            action_keys_entry.grid(row=2, column=1, columnspan=5, sticky="w")

            def on_action_key(event):
                key_name = event.keysym
                # Numpad mapping: KP_7 → num7, KP_8 → num8, ...
                if key_name.startswith("KP_") and len(key_name) == 4 and key_name[3].isdigit():
                    key_name = "num" + key_name[3]
                # Add only if not duplicate or not same as last
                if not item["action"] or key_name != item["action"][-1]:
                    if key_name not in item["action"]:
                        item["action"].append(key_name)
                        action_keys_var.set(" + ".join(item["action"]))
                        action_keys_entry.icursor(tk.END)

            action_keys_entry.bind("<Key>", on_action_key)

            # Button to clear action keys (right of Action Keys)
            def clear_action():
                item["action"] = []
                action_keys_var.set("")
            clear_action_btn = tk.Button(edit_win, text="ล้าง Action", command=clear_action)
            clear_action_btn.grid(row=2, column=6, padx=5, sticky="w")

            # Button to delete this color (red) and save (right, same row)
            def delete_color():
                self.color_list.pop(idx)
                refresh_table()
                self.log(f"ลบสี: {orig_item['rgb']} → {orig_item['label']}")
                edit_win.destroy()
            del_btn = tk.Button(edit_win, text="ลบรายการนี้", command=delete_color, bg="#d9534f", fg="white")
            del_btn.grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="w")

            def save_edit():
                try:
                    r = int(r_edit.get())
                    g = int(g_edit.get())
                    b = int(b_edit.get())
                    label = label_edit.get().strip()
                    if not label:
                        messagebox.showerror("Error", "กรุณากรอก Label สถานะ")
                        return
                    # update original item only when save
                    self.color_list[idx]["rgb"] = (r, g, b)
                    self.color_list[idx]["label"] = label
                    self.color_list[idx]["active"] = active_var.get()
                    self.color_list[idx]["action_active"] = action_active_var.get()
                    self.color_list[idx]["action"] = item["action"]
                    refresh_table()
                    self.log(f"แก้ไขสี: ({r}, {g}, {b}) → {label}")
                    edit_win.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"ข้อมูลไม่ถูกต้อง: {e}")
            save_btn = tk.Button(edit_win, text="บันทึก", command=save_edit, bg="#5cb85c", fg="white")
            save_btn.grid(row=4, column=6, columnspan=2, pady=5, padx=5, sticky="e")

        tree.bind("<Double-1>", on_double_click)

    def get_color(self, x, y):
        with mss.mss() as sct:
            screenshot = sct.grab({"top": y, "left": x, "width": 1, "height": 1})
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            return img.getpixel((0, 0))

    def check_answer(self, pixel):
        tolerance = self.tolerance
        for c in self.color_list:
            if not c["active"]:
                continue
            key = c["rgb"]
            if all(abs(pixel[i] - key[i]) < tolerance for i in range(3)):
                return c["label"]
        return "ไม่รู้จักสี"

    def detect_loop(self):
        import pyautogui
        self.last_status = None
        while self.running:
            if self.selected_pos:
                pixel = self.get_color(*self.selected_pos)
                status = self.check_answer(pixel)
                if status != self.last_status:
                    # Find color config
                    action_str = ""
                    for c in self.color_list:
                        if c["label"] == status and c["active"]:
                            if c.get("action_active") and c.get("action"):
                                action_str = " | Action: " + " + ".join(c["action"])
                                # Map key names for Numpad and modifiers
                                def map_key(key):
                                    # Numpad mapping: num0-num9 (already mapped in on_action_key)
                                    if key.startswith("num") and len(key) == 4 and key[3].isdigit():
                                        return key
                                    # Control_L → ctrl, Shift_L → shift, Alt_L → alt
                                    if key in ["Control_L", "Control_R"]:
                                        return "ctrl"
                                    if key in ["Shift_L", "Shift_R"]:
                                        return "shift"
                                    if key in ["Alt_L", "Alt_R"]:
                                        return "alt"
                                    return key.lower()
                                keys = [map_key(k) for k in c["action"] if k]
                                # If only one key, just press
                                if len(keys) == 1:
                                    try:
                                        pyautogui.press(keys[0])
                                    except Exception:
                                        pass
                                elif len(keys) > 1:
                                    # Hold all keys down, then release in reverse
                                    try:
                                        for k in keys:
                                            pyautogui.keyDown(k)
                                        for k in reversed(keys):
                                            pyautogui.keyUp(k)
                                    except Exception:
                                        pass
                    # self.log(f"Pixel: {pixel}, สถานะ: {status}{action_str}")
                    self.log(f"สถานะ: {status}{action_str}")
                    self.last_status = status
            time.sleep(0.1)

    def start_detect(self):
        if not self.selected_pos:
            messagebox.showwarning("ยังไม่ได้เลือกตำแหน่ง", "กรุณาเลือกตำแหน่งก่อนเริ่มตรวจจับ")
            return
        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.detect_thread = threading.Thread(target=self.detect_loop)
        self.detect_thread.start()
        self.log("เริ่มตรวจจับสี...")

    def stop_detect(self):
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log("หยุดตรวจจับสีแล้ว")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorDetectorGUI(root)
    root.mainloop()
