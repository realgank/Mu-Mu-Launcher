import tkinter as tk
from tkinter import ttk
import subprocess
from adb_helper import wait_for_device

MUMU = r"C:\\Program Files\\Netease\\MuMuPlayerGlobal-12.0\\shell\\MuMuManager.exe"

class PlayerRow(ttk.Frame):
    def __init__(self, master, idx):
        super().__init__(master)
        self.idx = idx
        self.sel = tk.BooleanVar()
        self.port_var = tk.StringVar(value="")
        tk.Checkbutton(self, text=f"MuMu #{idx}", variable=self.sel).pack(side="left", padx=3)
        tk.Label(self, textvariable=self.port_var, width=10).pack(side="left")

    def set_port(self, port: int):
        self.port_var.set(f"port {port}")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MuMu Launcher")
        self.geometry("300x400")
        self.rows = []
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Выберите MuMu Player", font=("Arial", 12)).pack(pady=8)
        self.rows_frame = ttk.Frame(self)
        self.rows_frame.pack(fill="both", expand=True)
        self.add_row()
        ttk.Button(self, text="+", width=3, command=self.add_row).pack(pady=4)
        ttk.Button(self, text="▶ Запустить", command=self.run_all).pack(pady=4)
        tk.Label(self, text="Лог").pack(anchor="w", padx=5)
        self.log_txt = tk.Text(self, height=8, state="disabled", wrap="word")
        self.log_txt.pack(fill="both", expand=True, padx=5, pady=(0,8))

    def add_row(self):
        row = PlayerRow(self.rows_frame, len(self.rows) + 1)
        row.pack(anchor="w", pady=2)
        self.rows.append(row)

    def run_all(self):
        selected = [r for r in self.rows if r.sel.get()]
        if not selected:
            self.log("⚠ Ничего не выбрано")
            return
        for row in selected:
            self.log(f"Запуск MuMu #{row.idx}...")
            self.start_emulator(row.idx)
            port = self.wait_adb(row.idx)
            row.set_port(port)
            self.log(f"Порт {port}")
        self.log("✔ Готово")

    def start_emulator(self, idx):
        subprocess.Popen([MUMU, "api", "-v", str(idx), "launch_player"])

    def wait_adb(self, idx):
        port = 7555 + idx - 1
        wait_for_device(port, 30)
        return port

    def log(self, msg: str):
        print(msg)
        self.log_txt.configure(state="normal")
        self.log_txt.insert("end", msg + "\n")
        self.log_txt.see("end")
        self.log_txt.configure(state="disabled")

if __name__ == "__main__":
    App().mainloop()
