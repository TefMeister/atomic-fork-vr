"""rec_hq.py start|stop|done ... : Lanes' obs-rec.py, unchanged, run at native size (3440x1440, 30 fps) with a fixed 60 Mbps
(OBS Simple output, "Stream" quality: the presets smoothed the sky's grain away). Tefa 2026-11-20, timelapses for the Keeper PC."""
import importlib.util, os, sys
T = os.path.expanduser("~/github-backups/_lanes-next-wt/plugins/lanes/tools/obs-rec.py")
spec = importlib.util.spec_from_file_location("obsrec", T); m = importlib.util.module_from_spec(spec)
sys.argv = [T] + sys.argv[1:]
spec.loader.exec_module(m) if False else None
src = open(T, encoding="utf-8").read().replace('if __name__ == "__main__":', 'if False:')
exec(compile(src, T, "exec"), m.__dict__)
m.VIDEO_W, m.VIDEO_H, m.FPS = 3440, 1440, 30
real_connect = m.connect
def connect():
    cl = real_connect()
    if cl is None: return cl
    orig = cl.set_profile_parameter
    def spp(cat, name, val):
        if (cat, name) == ("SimpleOutput", "RecQuality"):
            orig("SimpleOutput", "StreamEncoder", "nvenc")
            orig("SimpleOutput", "VBitrate", "60000")      # 60 Mbps, fixed: OBS's quality presets smoothed the sky's grain away
            val = "Stream"                                  # record with the stream settings above
        return orig(cat, name, val)
    cl.set_profile_parameter = spp
    return cl
m.connect = connect
a = sys.argv[1:]
if a[0] == "start":
    m.cmd_start(a[1], a[2], a[a.index("--game") + 1] if "--game" in a else "x")
else:
    getattr(m, "cmd_" + a[0])()
