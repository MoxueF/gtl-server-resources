"""Build Release 4 from the verified Release 3 archive; retain AE UI only."""
import collections
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = 'v4.0.0'
BASE = ROOT / 'dist/GTL-Server-Resources-1.20.1-v3.0.0.zip'
assert hashlib.sha1(BASE.read_bytes()).hexdigest() == 'cc3a2fff14fdb1017181ccde4d726dda247469b6'
NAME = f'GTL-Server-Resources-1.20.1-{VERSION}.zip'
AE = set('advanced_ae ae2 ae2_mega_things ae2_toggleable_view_cell ae2additions ae2insertexportcard ae2omnicells ae2peat ae2things ae2wtlib aeinfinitybooster appbot appelem appflux appliede appliedsorting appmek arseng bigger_ae2 disksavior expandedae expatternprovider extendedae_plus extendedterminal fulleng gregiceng ifsoulsdisks infinitycells mae2 mae2a makeae2better megacells merequester'.split())
UI_PARTS = {'gui', 'guis', 'screens', 'font', 'fonts', 'hud', 'slot', 'slots', 'guides', 'guideme_guides', 'guide', 'patchouli', 'xei', 'book', 'curios'}

def is_ui(name):
    parts = name.split('/')[2:]
    return any(p in UI_PARTS for p in parts) or any(p.lower().startswith(('gui.', 'hud.')) for p in parts)

with zipfile.ZipFile(BASE) as z:
    assert z.testzip() is None
    previous = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
removed = [n for n in previous if n.startswith('assets/') and n.split('/')[1] not in AE and is_ui(n)]
files = {n: b for n, b in previous.items() if n not in set(removed) and 'readme' not in Path(n).name.lower()}
files['pack.mcmeta'] = json.dumps({'pack': {'pack_format': 15, 'description': 'GTL Server Resources v4.0.0 | World textures + AE2 interfaces only'}}, indent=2).encode()
files['CREDITS.txt'] = (b'Release 4: UI overrides are retained only for AE2 and its addons.\n'
    b'Vanilla and unrelated mod GUI/HUD overrides were removed.\n'
    b'All retained world textures and models are byte-identical to Release 3.\n\n'
    + previous['CREDITS.txt'])
out = ROOT / 'dist' / NAME
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n, b in sorted(files.items()):
        info = zipfile.ZipInfo(n, date_time=(2026, 10, 22, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, b, compresslevel=9)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert not any(n.startswith('assets/') and n.split('/')[1] not in AE and is_ui(n) for n in z.namelist())
    assert 'assets/ae2/screens/terminals/terminal.json' in z.namelist()
    assert all(z.read(n) == b for n, b in previous.items() if n.startswith('assets/') and n not in removed)
    assert not any('readme' in Path(n).name.lower() for n in z.namelist())
sha1 = hashlib.sha1(out.read_bytes()).hexdigest()
url = f'https://github.com/MoxueF/gtl-server-resources/releases/download/{VERSION}/{NAME}'
report = {'version': VERSION, 'file': NAME, 'size_bytes': out.stat().st_size, 'sha1': sha1, 'url': url,
          'base_version': 'v3.0.0', 'removed_ui_files': removed, 'removed_by_namespace': dict(collections.Counter(n.split('/')[1] for n in removed)),
          'retained_ae_ui_files': sum(n.startswith('assets/') and n.split('/')[1] in AE and is_ui(n) for n in files),
          'retained_assets': sum(n.startswith('assets/') for n in files)}
(ROOT / 'merge-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
(ROOT / 'CREDITS.txt').write_bytes(files['CREDITS.txt'])
(ROOT / 'server-resource-pack.properties').write_text(f'resource-pack={url}\nresource-pack-sha1={sha1}\nrequire-resource-pack=false\nresource-pack-prompt={{"text":"GTL Release 4: world textures + AE2 interfaces"}}\n', encoding='ascii')
(ROOT / 'dist' / (NAME + '.sha1')).write_text(f'{sha1}  {NAME}\n', encoding='ascii')
(ROOT / 'release-notes.md').write_text('移除原版及非 AE2 模组的 GUI/HUD 替换，保留 AE2 与附属界面。\n保留方块、物品、机器及 Pipez 管道材质。\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'removed_ui_files'}, indent=2))
