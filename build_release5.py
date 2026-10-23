"""Merge the verified Release 4 with Fusion Connected Glass, without GUI changes."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = 'v5.0.0'
BASE = ROOT / 'dist/GTL-Server-Resources-1.20.1-v4.0.0.zip'
GLASS = ROOT.parent / 'gtl-bloom-setup/connected-glass/Fusion Connected Glass v1.0.1 for Minecraft 1.20-1.21.8.zip'
assert hashlib.sha1(BASE.read_bytes()).hexdigest() == 'dca70f8ce54964a3a7a688d2236fc95e0b3e4bf1'
assert hashlib.sha1(GLASS.read_bytes()).hexdigest() == '48210e165b4df035509c2cdaba654afdb0ad27b3'

def read_pack(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n: z.read(n) for n in z.namelist() if not n.endswith('/')}

base, glass = read_pack(BASE), read_pack(GLASS)
addition = {n: b for n, b in glass.items() if n.startswith('assets/')}
assert all(not any(p in {'gui', 'guis', 'screens', 'hud', 'font'} for p in n.split('/')) for n in addition)
files = dict(base)
files.update(addition)
files['pack.mcmeta'] = json.dumps({
    'pack': {'pack_format': 15, 'description': 'GTL Server Resources v5.0.0 | Connected glass + AE2 interfaces'},
    'fusion': json.loads(glass['pack.mcmeta'])['fusion'],
}, indent=2).encode()
files['CREDITS.txt'] = (b'Release 5 adds Fusion Connected Glass v1.0.1 by SuperMartijn642.\n'
    b'https://modrinth.com/resourcepack/fusion-connected-glass\n'
    b'Requires client-side Fusion (Connected Textures) 1.2.11 or newer.\n'
    b'https://modrinth.com/mod/fusion-connected-textures\n\n' + base['CREDITS.txt'])
files = {n: b for n, b in files.items() if 'readme' not in Path(n).name.lower()}
name = f'GTL-Server-Resources-1.20.1-{VERSION}.zip'
out = ROOT / 'dist' / name
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n, b in sorted(files.items()):
        info = zipfile.ZipInfo(n, date_time=(2026, 10, 23, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, b, compresslevel=9)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(set(z.namelist()))
    assert all(z.read(n) == b for n, b in base.items() if n.startswith('assets/') and n not in addition)
    assert all(z.read(n) == b for n, b in addition.items())
    assert not any('readme' in Path(n).name.lower() for n in z.namelist())
    for n in addition:
        if n.endswith(('.json', '.mcmeta')):
            json.loads(z.read(n))
sha1 = hashlib.sha1(out.read_bytes()).hexdigest()
url = f'https://github.com/MoxueF/gtl-server-resources/releases/download/{VERSION}/{name}'
report = {'version': VERSION, 'file': name, 'size_bytes': out.stat().st_size, 'sha1': sha1,
          'url': url, 'base_version': 'v4.0.0', 'added_glass_assets': len(addition),
          'overridden_assets': sorted(set(addition) & set(base)), 'client_dependency': 'Fusion >=1.2.11',
          'provided_client_jar': 'fusion-1.3.16-forge-mc1.20.1.jar'}
(ROOT / 'merge-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
(ROOT / 'CREDITS.txt').write_bytes(files['CREDITS.txt'])
(ROOT / 'server-resource-pack.properties').write_text(f'resource-pack={url}\nresource-pack-sha1={sha1}\nrequire-resource-pack=false\nresource-pack-prompt={{"text":"GTL Release 5: connected glass; requires client Fusion"}}\n', encoding='ascii')
(ROOT / 'dist' / (name + '.sha1')).write_text(f'{sha1}  {name}\n', encoding='ascii')
(ROOT / 'release-notes.md').write_text('新增无缝玻璃，保留现有材质及 AE2 附属界面。\n客户端需安装附件 Fusion JAR，服务器自动下发材质包。\n', encoding='utf-8')
print(json.dumps(report, indent=2))
