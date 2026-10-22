"""Merge user-supplied packs; do not execute files inside them."""
import collections
import hashlib
import io
import json
import pathlib
import struct
import sys
import zipfile
import zlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / 'Downloads'
VERSION = 'v1.0.1'
NAME = f'GTL-Server-Resources-1.20.1-{VERSION}.zip'
REPO = 'MoxueF/gtl-server-resources'
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
files, owners, documents = {}, {}, {}
conflicts, removed, sources = [], [], []
repairs = []

def ingest(label, raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        # Some source ZIP directory entries have malformed CRC fields;
        # each actual file is CRC-checked by ZipFile.read below.
        source = {'name': label, 'sha256': hashlib.sha256(raw).hexdigest()}
        if 'pack.mcmeta' in z.namelist():
            source['metadata'] = json.loads(z.read('pack.mcmeta').decode('utf-8-sig'))
        sources.append(source)
        for item in z.infolist():
            n = item.filename
            if item.is_dir():
                continue
            assert not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts
            if not n.startswith('assets/'):
                if n != 'pack.png':
                    documents[f'sources/{len(sources):02d}/{n}'] = z.read(n)
                continue
            if pathlib.PurePosixPath(n).suffix.lower() in {'.bak', '.old', '.oldred', '.aseprite'} or pathlib.PurePosixPath(n).name.startswith('crash-'):
                removed.append({'source': label, 'file': n, 'reason': 'backup, editor source or old crash report'})
                continue
            data = z.read(n)
            if n in files:
                conflicts.append({'file': n, 'previous': owners[n], 'winner': label, 'identical': files[n] == data})
            files[n], owners[n] = data, label

# Low to high priority. Only the three requested packs are included.
for n in ['GToTextureBackportGTLv3.2.zip', 'XingLuo_AE2_1.21_GUIExpansion 2.7.9.zip', '多功能机械方块重置.zip']:
    ingest(n, (SOURCE / n).read_bytes())

n = 'assets/kubejs/textures/block/flotation_cell.png.mcmeta'
original = files[n].decode('utf-8-sig')
value, end = json.JSONDecoder().raw_decode(original.lstrip())
assert original.lstrip()[end:].strip() == '}'
files[n] = (json.dumps(value, indent=2) + '\n').encode('utf-8')
repairs.append({'file': n, 'change': 'Removed one extra trailing closing brace.'})

n = 'assets/buildinggadgets2/textures/item/construction_paste_container_creative.png'
b = files[n]
assert b.startswith(b'\x89PNG\r\n\x1a\n')
position, chunks, dropped, original_idat = 8, [], 0, []
while position < len(b):
    size = struct.unpack('>I', b[position:position+4])[0]
    kind = b[position+4:position+8]
    data = b[position+8:position+8+size]
    crc = struct.unpack('>I', b[position+8+size:position+12+size])[0]
    chunk = b[position:position+12+size]
    if crc != zlib.crc32(kind+data):
        assert kind == b'iCCP', 'Unexpected corrupted critical PNG chunk'
        dropped += 1
    else:
        chunks.append(chunk)
    if kind == b'IDAT':
        original_idat.append(data)
    position += size + 12
assert dropped == 1
files[n] = b[:8] + b''.join(chunks)
assert all(data in files[n] for data in original_idat)
repairs.append({'file': n, 'change': 'Removed one corrupt duplicate iCCP color-profile chunk; retained all image-data chunks unchanged.'})

credits = '''GTL Server Resources — merged collection for Minecraft 1.20.1

This is a merged collection, not original artwork. Original authors retain their rights.
Priority (highest first): multifunctional casing override; XingLuo AE2 Refreshed
2.7.9; GToTextureBackportGTL v3.2.
Changes: merged matching paths according to priority, removed backup/editor files
and an accidentally bundled old crash report, replaced root pack metadata.
Repaired an extra JSON closing brace in flotation-cell texture metadata and
removed a corrupt duplicate color-profile chunk from one Building Gadgets PNG.
The PNG pixel data was not changed.
Photon GAMS is a shader pack and is NOT included.

GToTextureBackportGTL v3.2: adapted by 虾比事李跌; sources named by the pack
include GTOCore, Re:Avaritia and AE2. Its supplied license states CC BY-NC-SA 4.0.
Original source and license text are preserved under sources/01/.
XingLuo AE2 Refreshed 2.7.9: XingLuo (from its supplied metadata).
The casing override's author is not clearly identified in its supplied metadata.
Original metadata is preserved under sources/.
No blanket license is granted over third-party assets; original terms still apply.
Bundling does not establish additional redistribution rights.

Compatibility: pack_format 15 targets Minecraft 1.20–1.20.1.
UI layouts and mod-specific rendering must be checked in the actual modded client.
'''
files['pack.mcmeta'] = json.dumps({'pack': {'pack_format': 15, 'description': f'GTL Server Resources {VERSION} | GTo + XingLuo AE2 + Casing'}}, ensure_ascii=False, indent=2).encode('utf-8')
with zipfile.ZipFile(SOURCE / 'XingLuo_AE2_1.21_GUIExpansion 2.7.9.zip') as z:
    files['pack.png'] = z.read('pack.png')
files['CREDITS.txt'] = credits.encode('utf-8')
files.update(documents)

# Check JSON syntax while retaining upstream JSON-with-comments where present.
json_warnings = []
for n, b in files.items():
    if n.endswith(('.json', '.mcmeta')):
        try:
            json.loads(b.decode('utf-8-sig'))
        except Exception as e:
            json_warnings.append({'file': n, 'source': owners.get(n, 'source metadata'), 'error': str(e)})

pack = OUT / NAME
with zipfile.ZipFile(pack, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n in sorted(files):
        info = zipfile.ZipInfo(n, date_time=(2026, 10, 22, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, files[n], compresslevel=9)
with zipfile.ZipFile(pack) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(set(z.namelist()))
    assert json.loads(z.read('pack.mcmeta'))['pack']['pack_format'] == 15
    for n, owner in owners.items():
        assert z.read(n) == files[n], (n, owner)

sha1 = hashlib.sha1(pack.read_bytes()).hexdigest()
url = f'https://github.com/{REPO}/releases/download/{VERSION}/{NAME}'
config = f'resource-pack={url}\nresource-pack-sha1={sha1}\nrequire-resource-pack=false\nresource-pack-prompt={{"text":"GTL server textures and AE-style interfaces"}}\n'
(ROOT / 'server-resource-pack.properties').write_text(config, encoding='ascii')
(OUT / (NAME + '.sha1')).write_text(f'{sha1}  {NAME}\n', encoding='ascii')
(ROOT / 'CREDITS.txt').write_text(credits, encoding='utf-8')
report = {'version': VERSION, 'file': NAME, 'size_bytes': pack.stat().st_size, 'sha1': sha1, 'url': url,
          'asset_count': len(owners), 'files': len(files), 'sources_low_to_high': sources,
          'conflicts': conflicts, 'removed': removed, 'json_warnings': json_warnings,
          'repairs': repairs,
          'final_source_counts': dict(collections.Counter(owners.values()))}
(ROOT / 'merge-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['sources_low_to_high','conflicts','removed','final_source_counts']}, ensure_ascii=False, indent=2))
print('CONFLICTS',len(conflicts),'REMOVED',len(removed))
