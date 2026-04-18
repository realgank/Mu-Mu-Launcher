import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json, os

class StepEditor(tk.Toplevel):
    def __init__(self, master, save_path: str):
        super().__init__(master)
        self.title("Редактор шага")
        self.geometry("420x430")
        self.save_path = save_path
        self.steps = []

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btns = ttk.Frame(self); btns.pack(pady=5)
        ttk.Button(btns, text="➕ TAP",   command=self.add_tap ).grid(row=0, column=0, padx=3)
        ttk.Button(btns, text="➕ SWIPE", command=self.add_swipe).grid(row=0, column=1, padx=3)
        ttk.Button(btns, text="➕ if MATCH", command=self.add_if_match).grid(row=0, column=2, padx=3)
        ttk.Button(btns, text="➕ if TEXT",  command=self.add_if_text ).grid(row=0, column=3, padx=3)

        ttk.Button(btns, text="🚀 LAUNCH APP", command=self.add_launch_app).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(btns, text="🛑 KILL APP",   command=self.add_kill_app  ).grid(row=1, column=1, padx=3, pady=3)
        ttk.Button(btns, text="⏳ WAIT APP",   command=self.add_wait_app  ).grid(row=1, column=2, padx=3, pady=3)

        ttk.Button(self, text="💾 Сохранить", command=self.save).pack(pady=8)

        # если файл уже существует – загрузим
        if os.path.exists(save_path):
            try:
                self.steps = json.load(open(save_path, "r", encoding="utf-8"))
                self.refresh()
            except Exception:
                pass

    # ---------- добавление блоков ----------
    def add_tap(self):
        x = ask_int("X координата", 100);   y = ask_int("Y координата", 200)
        if x is None: return
        self.steps.append({"type": "tap", "x": x, "y": y})
        self.refresh()

    def add_swipe(self):
        x1 = ask_int("X1", 100); y1 = ask_int("Y1", 500)
        x2 = ask_int("X2", 100); y2 = ask_int("Y2", 100)
        if x1 is None: return
        self.steps.append({"type": "swipe",
                           "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        self.refresh()

    def add_if_match(self):
        tpl = filedialog.askopenfilename(title="PNG шаблон", filetypes=[("PNG","*.png")])
        if not tpl: return
        then_x = ask_int("Если найден – tap X", 300)
        then_y = ask_int("Если найден – tap Y", 300)
        self.steps.append({
            "type": "if_match",
            "template": os.path.basename(tpl),
            "threshold": 0.8,
            "then": {"type": "tap", "x": then_x, "y": then_y},
            "else": {"type": "log", "message": "Шаблон не найден"}
        })
        self.refresh()

    def add_if_text(self):
        txt = simpledialog.askstring("Условие", "Введите текст для поиска:")
        if not txt: return
        then_x = ask_int("Если найден – tap X", 400)
        then_y = ask_int("Если найден – tap Y", 900)
        self.steps.append({
            "type": "if_text",
            "contains": txt,
            "then": {"type": "tap", "x": then_x, "y": then_y},
            "else": {"type": "log", "message": "Текст не найден"}
        })
        self.refresh()

    def add_launch_app(self):
        path = filedialog.askopenfilename(
            title="Выберите приложение",
            filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
        )
        if not path: return
        args_str = simpledialog.askstring("Аргументы", "Аргументы командной строки (необязательно):", initialvalue="")
        args = args_str.split() if args_str else []
        self.steps.append({"type": "launch_app", "path": path, "args": args})
        self.refresh()

    def add_kill_app(self):
        name = simpledialog.askstring("Завершить процесс", "Имя процесса (например: notepad.exe):")
        if not name: return
        self.steps.append({"type": "kill_app", "name": name})
        self.refresh()

    def add_wait_app(self):
        name = simpledialog.askstring("Ожидание процесса", "Имя процесса (например: notepad.exe):")
        if not name: return
        timeout = ask_int("Таймаут (секунды)", 30)
        if timeout is None: timeout = 30
        self.steps.append({"type": "wait_app", "name": name, "timeout": timeout})
        self.refresh()

    # ---------- UI helpers ----------
    def refresh(self):
        self.listbox.delete(0, tk.END)
        for i, s in enumerate(self.steps, 1):
            t = s["type"]
            if t == "launch_app":
                label = f"{i}. launch_app: {os.path.basename(s.get('path', ''))}"
            elif t == "kill_app":
                label = f"{i}. kill_app: {s.get('name', '')}"
            elif t == "wait_app":
                label = f"{i}. wait_app: {s.get('name', '')} (таймаут {s.get('timeout', 30)} с)"
            elif t == "tap":
                label = f"{i}. tap ({s.get('x')}, {s.get('y')})"
            elif t == "swipe":
                label = f"{i}. swipe ({s.get('x1')},{s.get('y1')})→({s.get('x2')},{s.get('y2')})"
            else:
                label = f"{i}. {t}"
            self.listbox.insert(tk.END, label)

    def save(self):
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        json.dump(self.steps, open(self.save_path,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
        messagebox.showinfo("OK", f"Сценарий сохранён → {self.save_path}")
        self.destroy()

def ask_int(title, default):
    val = simpledialog.askstring("Ввод", f"{title}:", initialvalue=str(default))
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

