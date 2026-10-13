from datetime import datetime
from pathlib import Path

LOGFILE = Path("timing.log")

ts_old=0
def time(libelle: str, mod: str) -> None:
    global ts_old
    ts = datetime.now().timestamp()
    LOGFILE.write_text(
        LOGFILE.read_text(encoding="utf-8") + 
        f"{ts:.6f} ({ts - ts_old:.6f}) - {mod} - {libelle}\n",
        encoding="utf-8"
    )
    ts_old = ts