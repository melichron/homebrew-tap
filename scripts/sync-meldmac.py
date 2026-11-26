#!/usr/bin/env python3
"""Update the MeldMac cask from its published stable GitHub release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

REPO = "melichron/meld-macos-silicon-native"
CASK = Path(__file__).resolve().parents[1] / "Casks/meldmac.rb"
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
DIGEST = r"[0-9a-f]{64}"


def latest_release():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "meldmac-homebrew-sync"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + token
    request = Request(f"https://api.github.com/repos/{REPO}/releases/latest", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def field(text, name, pattern):
    matches = list(re.finditer(rf'^  {name} "({pattern})"$', text, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"Expected one {name} field in {CASK.name}")
    return matches[0]


def verify_download(url, size, digest):
    checksum = hashlib.sha256()
    received = 0
    # The DMG is public. Its download redirects to a CDN and needs no token.
    with urlopen(Request(url, headers={"User-Agent": "meldmac-homebrew-sync"}), timeout=60) as response:
        while chunk := response.read(1024 * 1024):
            checksum.update(chunk)
            received += len(chunk)
    if received != size or checksum.hexdigest() != digest:
        raise ValueError("Downloaded DMG does not match the GitHub asset size and SHA-256")


def sync(release, path, verify_current=False):
    tag = release["tag_name"]
    if release["draft"] or release["prerelease"] or not re.fullmatch("v" + VERSION, tag):
        raise ValueError(f"Expected a published stable vMAJOR.MINOR.PATCH release, got {tag!r}")
    version = tag[1:]
    text = path.read_text()
    old_version = field(text, "version", VERSION)
    old_digest = field(text, "sha256", DIGEST)
    if tuple(map(int, version.split("."))) < tuple(map(int, old_version[1].split("."))):
        print(f"Keeping newer cask {old_version[1]}")
        return

    name = f"MeldMac-{version}-arm64.dmg"
    assets = [asset for asset in release["assets"] if asset["name"] == name]
    if len(assets) != 1 or assets[0]["state"] != "uploaded":
        raise ValueError(f"Missing uploaded release asset {name}")
    asset = assets[0]
    url = f"https://github.com/{REPO}/releases/download/{tag}/{name}"
    digest = re.fullmatch("sha256:(" + DIGEST + ")", asset.get("digest") or "")
    if not digest or asset["browser_download_url"] != url or asset["size"] <= 0:
        raise ValueError(f"Unexpected asset metadata for {name}")

    if version == old_version[1]:
        if old_digest[1] != digest[1]:
            raise ValueError(f"The checksum changed for the already published version {version}")
        if verify_current:
            verify_download(url, asset["size"], digest[1])
        print(f"Cask already matches {tag}")
        return

    verify_download(url, asset["size"], digest[1])
    text = text[:old_digest.start(1)] + digest[1] + text[old_digest.end(1):]
    path.write_text(field(text, "version", VERSION).re.sub(f'  version "{version}"', text))
    print(f"Updated {path.name} to {tag}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-current", action="store_true")
    try:
        sync(latest_release(), CASK, parser.parse_args().verify_current)
    except (ValueError, KeyError, OSError) as exc:
        sys.exit(f"MeldMac sync failed: {exc}")
