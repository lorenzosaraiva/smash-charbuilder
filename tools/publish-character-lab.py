"""Publish a checked local Character Lab snapshot after its source is pushed.

Creates a new release and updates the permanent latest/download URLs.
The independent Remix preview remains unchanged.
Git credentials remain in memory and are only sent to GitHub's API/upload hosts.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'
REPO = 'lorenzosaraiva/smash-charbuilder'
API = 'https://api.github.com/repos/'+REPO
TAG = None
FILES = ('character-lab.z64', 'character-lab.zip', 'build-info.json', 'SHA256SUMS.txt')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    global TAG
    assert git('remote', 'get-url', 'origin').rstrip('/').removesuffix('.git') == 'https://github.com/'+REPO
    head = git('rev-parse', 'HEAD')
    assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == head, 'Push the exact source first.'
    assert not git('status', '--porcelain'), 'Commit local source changes first.'
    info = json.loads((DIST/'build-info.json').read_text())
    TAG = 'build-local-'+info['built_at'][:10].replace('-', '')+'-'+head[:9]
    assert info['commit'] == head and info['source_dirty'] is False
    assert info['source_directory'] == 'ssb-decomp-re'
    for row in (DIST/'SHA256SUMS.txt').read_text().splitlines():
        digest, name = row.split('  ')
        assert name in FILES and hashlib.sha256((DIST/name).read_bytes()).hexdigest() == digest
    assert hashlib.sha256((DIST/FILES[0]).read_bytes()).hexdigest() == info['rom_sha256']
    with zipfile.ZipFile(DIST/FILES[1]) as archive:
        assert archive.testzip() is None
        assert json.loads(archive.read('build-info.json')) == info
        assert archive.read(FILES[0]) == (DIST/FILES[0]).read_bytes()
        for row in archive.read('SHA256SUMS.txt').decode().splitlines():
            digest, name = row.split('  ')
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    credentials = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', cwd=ROOT,
                                 capture_output=True, text=True, check=True,
                                 env={**os.environ, 'GCM_INTERACTIVE': 'never'}, timeout=30)
    token = dict(line.split('=', 1) for line in credentials.stdout.splitlines() if '=' in line)['password']

    def request(url, method='GET', data=None, binary=False, missing_ok=False):
        assert urllib.parse.urlparse(url).hostname in ('api.github.com', 'uploads.github.com')
        headers = {'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.github+json',
                   'User-Agent': 'smash-charbuilder-local-release', 'X-GitHub-Api-Version': '2022-11-28'}
        if data is not None:
            headers['Content-Type'] = 'application/octet-stream' if binary else 'application/json'
            if not binary:
                data = json.dumps(data).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=240) as response:
                content = response.read()
                return json.loads(content) if content else None
        except urllib.error.HTTPError as error:
            if error.code == 404 and missing_ok:
                return None
            details = json.loads(error.read())
            raise RuntimeError(f'GitHub {error.code}: {details.get("message", "request failed")}') from None

    repo = request(API)
    assert repo['full_name'] == REPO and not repo['private'] and repo['permissions']['push']
    ref = request(API+'/git/ref/tags/'+TAG, missing_ok=True)
    if ref:
        assert ref['object']['type'] == 'commit' and ref['object']['sha'] == head, 'Snapshot tags never move.'
    else:
        request(API+'/git/refs', 'POST', {'ref': 'refs/tags/'+TAG, 'sha': head})
    release = request(API+'/releases/tags/'+TAG, missing_ok=True)
    body = (DIST/'release-notes.md').read_text(encoding='utf-8')
    if not release:
        release = request(API+'/releases', 'POST', {'tag_name': TAG, 'target_commitish': head,
                          'name': 'Character Lab '+info['version']+' - '+info['built_at'][:10], 'body': body,
                          'draft': True, 'prerelease': False, 'make_latest': 'true'})
    upload = release['upload_url'].split('{')[0]
    for name in FILES:
        data = (DIST/name).read_bytes()
        digest = 'sha256:'+hashlib.sha256(data).hexdigest()
        old = next((asset for asset in release['assets'] if asset['name'] == name), None)
        if old and old.get('digest') == digest:
            continue
        if old:
            assert release['draft'], 'Published snapshot assets cannot be replaced.'
            request(API+'/releases/assets/'+str(old['id']), 'DELETE')
        asset = request(upload+'?'+urllib.parse.urlencode({'name': name}), 'POST', data, binary=True)
        assert asset['state'] == 'uploaded' and asset.get('digest') == digest
        print('Uploaded and checksum checked: '+name, flush=True)
    ready = request(API+'/releases/'+str(release['id']))
    assert {asset['name'] for asset in ready['assets']} == set(FILES)
    for asset in ready['assets']:
        assert asset.get('digest') == 'sha256:'+hashlib.sha256((DIST/asset['name']).read_bytes()).hexdigest()
    published = request(API+'/releases/'+str(release['id']), 'PATCH', {'draft': False, 'prerelease': False, 'make_latest': 'true', 'body': body})
    for name in FILES[:2]:
        url = 'https://github.com/'+REPO+'/releases/download/'+TAG+'/'+name
        # Public downloads/redirects carry no credential headers.
        with urllib.request.urlopen(url, timeout=240) as response:
            digest = hashlib.sha256()
            while block := response.read(1024*1024):
                digest.update(block)
        assert digest.hexdigest() == hashlib.sha256((DIST/name).read_bytes()).hexdigest()
        print('Verified public download: '+name, flush=True)
    print('Published: '+published['html_url'], flush=True)


if __name__ == '__main__':
    main()
