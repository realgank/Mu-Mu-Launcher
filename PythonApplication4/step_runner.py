import cv2, subprocess, time, os, pytesseract, numpy as np

# если Tesseract установлен не в PATH – пропишите вручную
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- вспомогательные adb ----------
def capture_screen(serial: str) -> any:
    raw = subprocess.check_output(["adb", "-s", serial, "exec-out", "screencap", "-p"])
    img_path = "_screen.png"
    with open(img_path, "wb") as f:
        f.write(raw)
    return cv2.imread(img_path)

def adb_tap(serial, x, y):
    subprocess.call(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)])

def adb_swipe(serial, x1, y1, x2, y2, dur=300):
    subprocess.call(["adb", "-s", serial, "shell", "input", "swipe",
                     str(x1), str(y1), str(x2), str(y2), str(dur)])

# ---------- шаблоны и OCR ----------
def template_match(screen, tpl_path, thr=0.8):
    template = cv2.imread(tpl_path)
    if template is None or screen is None:
        return False, (0, 0)
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val >= thr:
        h, w = template.shape[:2]
        return True, (max_loc[0] + w // 2, max_loc[1] + h // 2)
    return False, (0, 0)

def ocr_text(screen) -> str:
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray, lang='eng+rus')

# ---------- универсальный исполнитель ----------
def run_steps(serial: str, steps: list, log=print):
    for st in steps:
        t = st["type"]

        if t == "tap":
            adb_tap(serial, st["x"], st["y"])
            log(f"👉 tap ({st['x']},{st['y']})")

        elif t == "swipe":
            adb_swipe(serial, st["x1"], st["y1"], st["x2"], st["y2"])
            log(f"↔ swipe ({st['x1']},{st['y1']})→({st['x2']},{st['y2']})")

        elif t == "if_match":
            screen = capture_screen(serial)
            found, pos = template_match(
                screen,
                os.path.join("templates", st["template"]),
                st.get("threshold", 0.8)
            )
            log(f"🔍 template '{st['template']}' → {'match' if found else 'no'}")
            sub = st["then"] if found else st["else"]
            run_steps(serial, [sub], log)

        elif t == "if_text":
            screen = capture_screen(serial)
            txt = ocr_text(screen).lower()
            cond = st["contains"].lower()
            ok = cond in txt
            log(f"🔤 text contains '{cond}' → {'yes' if ok else 'no'}")
            sub = st["then"] if ok else st["else"]
            run_steps(serial, [sub], log)

        elif t == "delay":
            time.sleep(st.get("seconds", 1))
            log(f"⏱ delay {st.get('seconds',1)} s")

        elif t == "log":
            log("📝 " + st["message"])

        elif t == "launch_app":
            path = st["path"]
            args = st.get("args", [])
            subprocess.Popen([path] + args)
            log(f"🚀 запущено: {os.path.basename(path)}")

        elif t == "kill_app":
            name = st["name"]
            subprocess.call(["taskkill", "/f", "/im", name])
            log(f"🛑 завершено: {name}")

        elif t == "wait_app":
            name = st["name"]
            timeout = st.get("timeout", 30)
            end = time.time() + timeout
            found = False
            while time.time() < end:
                out = subprocess.check_output(
                    ["tasklist", "/fi", f"imagename eq {name}"], text=True, encoding="cp866"
                )
                if name.lower() in out.lower():
                    found = True
                    break
                time.sleep(1)
            log(f"⏳ ожидание {name}: {'найдено' if found else 'таймаут'}")

        time.sleep(0.3)   # маленькая пауза между действиями

