"""timelapse.py (2026-11-20, Tefa's 24 h comparison videos) <profile> <label>: start the flat game on <profile> (it loads the newest save by itself), hide the HUD,
speed time up so 24 game hours take RECORD_S seconds, record the game window with obs-rec.py, then close the game."""
import os, sys, subprocess, time
TOOLS = os.path.expanduser("~/github-backups/atomic-fork-vr/tools")
OBS = os.path.expanduser("~/github-backups/_lanes-next-wt/plugins/lanes/tools/obs-rec.py")
MO2, GAME = "C:/Modlists/Atomic Fork VR", "C:/Steam/steamapps/common/Fallout New Vegas"
RECORD_S = 360
TIMESCALE = round(24 * 3600 / RECORD_S)          # 240: one game day in six minutes
prof, label = sys.argv[1], sys.argv[2]
def running(n): return n.lower() in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
def console(*lines): print(" console", lines, subprocess.run([sys.executable, os.path.join(TOOLS, "console_type.py"), *lines], capture_output=True, text=True).returncode, flush=True)
assert not running("FalloutNV.exe") and not running("ModOrganizer.exe"), "game or MO2 already running"
start = time.time()
subprocess.Popen([MO2 + "/ModOrganizer.exe", "-p", prof, "moshortcut://:Atomic Fork VR"], cwd=MO2)
log = GAME + "/nvse.log"
while time.time() - start < 240:
    try:
        if os.path.getmtime(log) > start and "DoLoadGameHook" in open(log, encoding="latin-1").read(): break
    except OSError: pass
    time.sleep(3)
else:
    sys.exit("the save never loaded")
print("loaded after", round(time.time() - start), "s", flush=True)
time.sleep(15)
console("tgm", "tcai", "set timescale to %d" % TIMESCALE)
console("tm")                                         # HUD off, last, so the console is shut before recording
time.sleep(2)
print(subprocess.run([sys.executable, OBS, "start", "FalloutNV.exe", label, "--game", "atomic-fork-vr"], capture_output=True, text=True).stdout[-300:], flush=True)
time.sleep(RECORD_S + 5)
print(subprocess.run([sys.executable, OBS, "stop"], capture_output=True, text=True).stdout[-400:], flush=True)
console("tm", "set timescale to 30")
subprocess.run(["taskkill", "/IM", "FalloutNV.exe"], capture_output=True)
t = time.time()
while running("FalloutNV.exe") and time.time() - t < 120: time.sleep(2)
print("game closed" if not running("FalloutNV.exe") else "GAME STILL UP", flush=True)
while running("ModOrganizer.exe") and time.time() - t < 180: time.sleep(2)
