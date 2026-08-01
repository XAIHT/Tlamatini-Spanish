import json, sys
sys.path.insert(0, '.')
from agent import tts_piper
st = tts_piper.ensure_ready(log=lambda m: print('  ', m, flush=True), attempts=60, retry_wait=3)
print(json.dumps(st, indent=2, ensure_ascii=False))
