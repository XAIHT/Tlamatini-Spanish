# Tlamatini Author Banner — Angela López Mendoza · @angelahack1
"""Real voice validation from the user-confirmed visible console, audio saved only."""
import argparse
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Temp/name-voice-audio'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('all', 'piper', 'orpheus'), default='all')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    sys.path.insert(0, str(ROOT / 'scripts'))
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    from markdown_canvas_visible import visible_console
    visible_console()
    for key in ('TMP', 'TEMP', 'TMPDIR', 'TLAMATINI_TEMP'):
        os.environ[key] = str(ROOT / 'Temp')
    os.environ['TLAMATINI_NO_AUDIO'] = '1'
    os.environ['PYTHONPATH'] = str(ROOT / 'Temp/piper-validation-runtime')
    sys.path.insert(0, os.environ['PYTHONPATH'])
    copy = OUT / 'talker-copy'
    copy.mkdir(exist_ok=True)
    for name in ('talker.py', 'spanish_pronunciation.py'):
        shutil.copy2(ROOT / 'Tlamatini/agent/agents/talker' / name, copy / name)
    original_popen = subprocess.Popen.__init__
    spec = importlib.util.spec_from_file_location('real_talker_validation', copy / 'talker.py')
    talker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(talker)
    # Development children inherit this visible console; product launch behavior is
    # untouched. Do not allow the product's hidden-child guard in a development run.
    subprocess.Popen.__init__ = original_popen
    os.chdir(ROOT)
    text = 'Hola Angela. Jose, Maria, Jesus, Sofia y Raul.'
    report = {'input': text, 'prepared': talker._pronunciation.speech_text(text), 'voices': []}
    if args.engine != 'all' and (OUT / 'results.json').exists():
        report = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
        report['voices'] = [row for row in report['voices'] if row['engine'] != args.engine]
    def save():
        (OUT / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for engine, voice in [('piper', 'es_MX-claude-high')] + [('orpheus', v) for v in sorted(set(talker._FEMALE_VOICES) - talker._PIPER_FEMALE_VOICES)]:
        if args.engine not in ('all', engine):
            continue
        started = time.monotonic()
        print('START REAL VOICE', engine, voice, flush=True)
        config = dict(input_text=text, tts_engine=engine, voice=voice, language='es-MX',
                      model='legraphista/Orpheus:3b-ft-q8', play_audio=False, seed=42,
                      request_timeout=300, output_dir=str(OUT / voice),
                      piper_voices_dir=str(OUT / 'piper-models'), piper_auto_install=False)
        try:
            result = talker.synthesize(config)
            if result['status'] != 'saved':
                raise RuntimeError(result)
            with wave.open(result['output_path'], 'rb') as wav:
                assert wav.getnframes() > wav.getframerate()
            row = {'engine': engine, 'voice': voice, 'result': result, 'passed': True}
            if engine == 'piper':
                from piper import PiperVoice
                model = Path(config['piper_voices_dir']) / 'es_MX-claude-high.onnx'
                native = PiperVoice.load(str(model))
                phonemes = {}
                for name in ('angela', 'Angela', 'ANGELA', 'angéla', 'Angéla', 'Ángela',
                             'Jose', 'Maria', 'Jesus', 'Sofia', 'Raul'):
                    prepared = talker._pronunciation.speech_text(name)
                    phonemes[name] = ''.join(''.join(part) for part in native.phonemize(prepared))
                assert phonemes['Angela'] == phonemes['Angéla'] == phonemes['Ángela']
                assert phonemes['angela'] == phonemes['ANGELA'] == phonemes['angéla'] == phonemes['Ángela']
                assert phonemes['Angela'].startswith('ˈa'), phonemes
                catalog_checks = 0
                for unaccented, canonical in talker._pronunciation.NAME_ACCENTS.items():
                    restored = talker._pronunciation.accent_name(unaccented.title())
                    assert native.phonemize(restored) == native.phonemize(canonical), canonical
                    catalog_checks += 1
                row.update(espeak_voice=native.config.espeak_voice, phonemes=phonemes,
                           catalog_phoneme_checks=catalog_checks)
        except Exception as exc:
            row = {'engine': engine, 'voice': voice, 'passed': False, 'error': str(exc)}
        row['elapsed_seconds'] = round(time.monotonic() - started, 2)
        report['voices'].append(row)
        save()
        print('FINISH REAL VOICE', json.dumps(row, ensure_ascii=False), flush=True)
    print('ALL VOICES FINISHED', flush=True)
    raise SystemExit(0 if all(v['passed'] for v in report['voices']) else 1)


if __name__ == '__main__':
    main()
