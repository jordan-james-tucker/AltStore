"""Apply the reviewed AltSign source patch to its exact official dependency."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
root = Path(__file__).resolve().parent.parent
dependency = root / 'Dependencies/AltSign'
manifest = json.loads((root / 'Patches/AltSign-authentication-identity.json').read_text())
patch = root / 'Patches/AltSign-authentication-identity.patch'
def digest(path):
    # GitHub's editor and Windows checkouts may use CRLF for text sources.
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
assert subprocess.check_output(['git','-C',str(dependency),'rev-parse','HEAD']).decode().strip() == manifest['base_commit']
assert digest(patch) == manifest['patch_sha256']
target = dependency / manifest['path']
if digest(target) == manifest['after_sha256']:
    print('AltSign identity patch already applied and verified.')
else:
    assert digest(target) == manifest['before_sha256'], 'Unexpected AltSign source'
    target.write_bytes(target.read_bytes().replace(b'\r\n', b'\n'))
    with tempfile.TemporaryDirectory() as staging:
        normalized_patch = Path(staging) / 'identity.patch'
        normalized_patch.write_bytes(patch.read_bytes().replace(b'\r\n', b'\n'))
        subprocess.run(['git','-C',str(dependency),'apply','--check',str(normalized_patch)],check=True)
        subprocess.run(['git','-C',str(dependency),'apply',str(normalized_patch)],check=True)
    assert digest(target) == manifest['after_sha256']
    print('Applied and verified AltSign identity patch.')
