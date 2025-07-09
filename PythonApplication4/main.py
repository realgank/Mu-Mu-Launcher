import tkinter as tk
from tkinter import ttk
import subprocess, time, json, os
from step_editor import StepEditor
from step_runner import run_steps
from adb_helper import wait_for_device
# from discord_logger import DiscordLogger   # если нужен веб‑хук

CONFIG = "config.json"
MUMU = r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe"

class EmulatorTask:
    def __init__(self, num):
        self.num = num
        self.sel = tk.BooleanVar()
        self.steps_checked = [tk.BooleanVar() for _ in range(5)]

    def to_dict(self):
        return {"selected": self.sel.get(),
                "steps": [v.get() for v in self.steps_checked]}

    def from_dict(self, d):
        self.sel.set(d.get("selected", False))
        for i, v in enumerate(d.get("steps", [])):
            self.steps_checked[i].set(v)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MuMu Launcher")
        self.geometry("760x640")

        self.emus = [EmulatorTask(i) for i in range(1,11)]
        self.serial_map = {}
        # self.dlog = DiscordLogger("WEBHOOK_URL")  # <- при необходимости

        self.build_ui()
        self.load_cfg()

    # ---------- GUI ----------
    def build_ui(self):
        tk.Label(self, text="Выберите эмуляторы и шаги",
                 font=("Arial",14)).pack(pady=8)

        frame = ttk.Frame(self); frame.pack()
        canvas = tk.Canvas(frame, height=260)
        vs = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.scr_frame = ttk.Frame(canvas)
        self.scr_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.scr_frame, anchor="nw")
        canvas.configure(yscrollcommand=vs.set)
        canvas.pack(side="left", fill="both", expand=True); vs.pack(side="right", fill="y")

        for e in self.emus:
            row = ttk.Frame(self.scr_frame); row.pack(anchor="w", pady=2)
            tk.Checkbutton(row, text=f"MuMu #{e.num}", variable=e.sel).pack(side=tk.LEFT,padx=3)
            for i in range(5):
                tk.Checkbutton(row, text=f"Шаг {i+1}", variable=e.steps_checked[i]).pack(side=tk.LEFT, padx=1)
            ttk.Button(row, text="🛠", width=3,
                       command=lambda n=e.num: StepEditor(self, f"steps/mumu{n}_step1.json")).pack(side=tk.LEFT,padx=4)

        btns = ttk.Frame(self); btns.pack(pady=8)
        ttk.Button(btns, text="▶ Запустить", command=self.run_all).grid(row=0,column=0,padx=5)
        ttk.Button(btns, text="💾 Сохранить", command=self.save_cfg).grid(row=0,column=1,padx=5)
        ttk.Button(btns, text="📥 Загрузить", command=self.load_cfg).grid(row=0,column=2,padx=5)

        tk.Label(self, text="Лог").pack(anchor="w", padx=8)
        self.log_txt = tk.Text(self, height=12, state="disabled", wrap="word")
        self.log_txt.pack(fill="both", expand=True, padx=8, pady=(0,8))

    # ---------- основная логика ----------
    def run_all(self):
        selected = [e for e in self.emus if e.sel.get()]
        if not selected:
            self.log("⚠ Ничего не выбрано"); return
        for emu in selected:
            self.log(f"\n=== MuMu #{emu.num} ===")
            self.start_emulator(emu.num)
            serial = self.wait_adb(emu.num)
            self.log(f"ADB: {serial or 'НЕ найден'}")
            for i, step_flag in enumerate(emu.steps_checked):
                if not step_flag.get(): continue
                if i == 0:
                    self.execute_step_file(serial, emu.num)
                else:
                    self.log(f"Шаг {i+1}: заглушка"); time.sleep(1)
            self.stop_emulator(emu.num)
        self.log("\n✔ Все задачи завершены")

    def start_emulator(self, idx):
        subprocess.Popen([MUMU, "api", "-v", str(idx), "launch_player"])
        self.log("Запуск эмулятора…")

    def stop_emulator(self, idx):
        subprocess.call([MUMU, "api", "-v", str(idx), "shutdown_player"])
        self.log("Закрыт эмулятор")

    def wait_adb(self, idx):
        port = 7555 + idx - 1
        serial = wait_for_device(port, 30)
        if serial: self.serial_map[idx] = serial
        else: serial = f"127.0.0.1:{port}"
        return serial

    def execute_step_file(self, serial, idx):
        path = f"steps/mumu{idx}_step1.json"
        if not os.path.exists(path):
            self.log("⚠ Файл шага не найден")
            return
        steps = json.load(open(path,"r",encoding="utf-8"))
        run_steps(serial, steps, log=self.log)

    # ---------- util ----------
    def log(self, msg:str):
        print(msg)
        # self.dlog.send(msg)                # в Discord, если нужно
        self.log_txt.configure(state="normal")
        self.log_txt.insert("end", msg+"\n")
        self.log_txt.see("end")
        self.log_txt.configure(state="disabled")

    # ---------- конфигурация ----------
    def save_cfg(self):
        data = {e.num: e.to_dict() for e in self.emus}
        json.dump(data, open(CONFIG,"w",encoding="utf-8"), indent=2)
        self.log("💾 Конфигурация сохранена")

    def load_cfg(self):
        if not os.path.exists(CONFIG):
            self.log("Нет сохранённой конфигурации"); return
        data = json.load(open(CONFIG,"r",encoding="utf-8"))
        for e in self.emus:
            if str(e.num) in data or e.num in data:
                e.from_dict(data.get(str(e.num), data.get(e.num)))
        self.log("📥 Конфигурация загружена")

if __name__ == "__main__":
    App().mainloop()

