"""Public invented-only GnuPG roundtrip rehearsal under caller's Linux UID.

NEVER processes genuine source, hidden targets, private keys, or real receipts.
Uses a fresh random disposable SYMMETRIC passphrase confined to a 0700
temporary folder. It is NOT a production key-management design, not a
scientific evaluator, and not evidence of independent custody.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import shutil
import stat
import subprocess
import tempfile

STATUS="PUBLIC_DUMMY_GPG_ROUNDTRIP_ONLY"
DUMMY=b"EXP-COEV-001 PUBLIC INVENTED FIXTURE. NOT SCIENTIFIC SOURCE.\n"

def _private_bytes(path: Path, content: bytes) -> None:
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as out:
            out.write(content)
    except BaseException:
        try: os.unlink(path)
        except OSError: pass
        raise

def _gpg(gpg_bin: str, home: Path, password: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    cmd=[gpg_bin,"--no-options","--homedir",str(home),
         "--batch","--yes","--pinentry-mode","loopback","--no-symkey-cache",
         "--passphrase-file",str(password),*args]
    environment={"PATH":"/usr/bin:/bin","HOME":str(home),
                 "GNUPGHOME":str(home),"LC_ALL":"C"}
    return subprocess.run(cmd,capture_output=True,check=False,timeout=20,env=environment)

def public_gpg_rehearsal() -> dict[str,object]:
    if os.geteuid()==0:
        raise RuntimeError("Do not run test as root; use unprivileged custodian UID")
    gpg=shutil.which("gpg")
    if gpg is None:
        raise RuntimeError("GnuPG executable unavailable")
    old_umask=os.umask(0o077)
    try:
        with tempfile.TemporaryDirectory(prefix="coev-f0d-public-toy-") as temp:
            base=Path(temp)
            if stat.S_IMODE(base.stat().st_mode)!=0o700:
                raise RuntimeError("Temporary directory must be owner-only")
            home=base/"gnupg"
            home.mkdir(mode=0o700)
            original=base/"toy.txt"
            encrypted=base/"toy.gpg"
            recovered=base/"recovered.txt"
            wrong_target=base/"wrong.txt"
            passfile=base/"toy-pass"
            wrongpass=base/"wrong-pass"
            _private_bytes(original,DUMMY)
            _private_bytes(passfile,secrets.token_hex(32).encode("ascii")+b"\n")
            _private_bytes(wrongpass,secrets.token_hex(32).encode("ascii")+b"\n")
            created=_gpg(gpg,home,passfile,"--cipher-algo","AES256","--symmetric",
                         "--output",str(encrypted),str(original))
            if created.returncode!=0 or not encrypted.is_file():
                raise RuntimeError("Public dummy encryption failed")
            if encrypted.read_bytes()==DUMMY:
                raise RuntimeError("Dummy ciphertext equals original bytes")
            restored=_gpg(gpg,home,passfile,"--decrypt","--output",
                          str(recovered),str(encrypted))
            if restored.returncode!=0 or recovered.read_bytes()!=DUMMY:
                raise RuntimeError("Public dummy roundtrip mismatch")
            rejected=_gpg(gpg,home,wrongpass,"--decrypt","--output",
                          str(wrong_target),str(encrypted))
            if rejected.returncode==0:
                raise RuntimeError("Wrong dummy passphrase unexpectedly accepted")
            if stat.S_IMODE(passfile.stat().st_mode)!=0o600:
                raise RuntimeError("Disposable dummy passphrase file not owner-only")
            # Only return Boolean/metadata. No path, passphrase, ciphertext, seed or labels.
            return {"status":STATUS,"cipher":"AES256",
                    "correct_passphrase_roundtrip":True,
                    "wrong_passphrase_rejected":True,
                    "temporary_files_automatically_removed":True,
                    "scientific_source_generated":False,
                    "real_keys_or_labels_accessed":False,
                    "third_party_custody_verified":False}
    finally:
        os.umask(old_umask)

def main() -> int:
    print(json.dumps(public_gpg_rehearsal(),sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
