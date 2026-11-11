"""OS process and filesystem isolation for WORLD CAL roles (Linux bubblewrap).

The Python AccessMatrix is only defense-in-depth. Independent roles MUST be
different processes in different mount namespaces, with only their allowed
source files mounted. This module refuses to execute if bubblewrap or user
namespace isolation is unavailable. No in-process role switch fallback.
"""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

from .ledger import AccessDenied, ROLE_READS, check_role_read

ROLE_DIRS={
    "LEARNER_ARMS":("public", "self"),
    "EVALUATOR":("private",),
    "CAL_ORACLE":("abstract",),
    "BLIND_DESIGN_CALCULATOR":("design","analysis"),
    "AUDITOR":("audit",)
}


class SandboxUnknown(PermissionError):
    pass


def verify_role_stage(role,stage,allowed_sources,*,cal_authorized=False):
    """Trusted launcher validates every staged file before mounting it."""
    if role not in ROLE_DIRS or not isinstance(allowed_sources,dict):
        raise SandboxUnknown("STOP_UNKNOWN: invalid role/stage map")
    root=pathlib.Path(stage).resolve(strict=True)
    if not root.is_dir() or root.is_symlink():
        raise SandboxUnknown("STOP_UNKNOWN: invalid stage root")
    for relative,expected_digest in allowed_sources.items():
        if not isinstance(relative,str) or not relative or relative.startswith("/"):
            raise SandboxUnknown("STOP_UNKNOWN: noncanonical source path")
        name=pathlib.PurePosixPath(relative)
        if ".." in name.parts or name.parts[0] not in ROLE_DIRS[role]:
            raise SandboxUnknown("STOP_UNKNOWN: path outside source-first role")
        src=root/relative
        if src.is_symlink() or not src.is_file() or root not in src.resolve(strict=True).parents:
            raise SandboxUnknown("STOP_UNKNOWN: linked or absent source")
        logical=relative
        if role=="BLIND_DESIGN_CALCULATOR" and relative=="design/split_metadata":
            logical="design/split_metadata:N_eligible,q,parent_cluster"
        if role in ROLE_READS and logical not in ROLE_READS[role]:
            raise SandboxUnknown("STOP_UNKNOWN: source not in approved read allowlist")
        if role in ("CAL_ORACLE","BLIND_DESIGN_CALCULATOR") and not cal_authorized:
            raise SandboxUnknown("STOP_UNKNOWN: CAL authorization absent")
        if not isinstance(expected_digest,str) or len(expected_digest)!=64:
            raise SandboxUnknown("STOP_UNKNOWN: missing source hash")
        if hashlib.sha256(src.read_bytes()).hexdigest()!=expected_digest:
            raise SandboxUnknown("STOP_UNKNOWN: source bytes changed")
    present={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    if present!=set(allowed_sources):
        raise SandboxUnknown("STOP_UNKNOWN: unregistered files in role stage")
    return True


def _mount_system_ro():
    # Minimal interpreter and shared library paths; neither /home nor /mnt
    # nor the host working tree is visible in the namespace.
    paths=[]
    for path in ("/usr","/bin","/lib","/lib64"):
        if pathlib.Path(path).exists() and path not in paths:
            paths.extend(["--ro-bind",path,path])
    prefix=pathlib.Path(sys.prefix).resolve()
    if not (str(prefix)=="/usr" or str(prefix).startswith("/usr/")):
        if not any(str(prefix)==x or str(prefix).startswith(x+"/")
                   for x in ("/usr","/bin","/lib","/lib64","/etc")):
            paths.extend(["--ro-bind",str(prefix),str(prefix)])
    return paths


def launch_isolated(role,*,code_root,role_stage,entrypoint,manifest,
                    payload=b"",cal_authorized=False,timeout=180,
                    synthetic_filesystem_only=False):
    """Run a verified role inside a restrictive mount/PID/network namespace.

    Stage is trust-boundary input: the caller must prepare an exclusive,
    non-symlink directory of byte-hashed data. Only that directory is mounted
    at /role. Secrets remain on the host in a DIFFERENT unmapped directory.
    """
    # Host-network mode is restricted to explicit PUBLIC fixture auditing;
    # production role launch always requires independent network isolation.
    if synthetic_filesystem_only and (cal_authorized or role not in ("LEARNER_ARMS","EVALUATOR")):
        raise SandboxUnknown("STOP_UNKNOWN: fixture-only network exception denied")
    bwrap=shutil.which("bwrap")
    if sys.platform!="linux" or not bwrap:
        raise SandboxUnknown("STOP_UNKNOWN: bubblewrap isolation unavailable")
    verify_role_stage(role,role_stage,manifest,cal_authorized=cal_authorized)
    code=pathlib.Path(code_root).resolve(strict=True)
    script=code/entrypoint
    if not script.is_file() or script.is_symlink() or code not in script.resolve().parents:
        raise SandboxUnknown("STOP_UNKNOWN: invalid entrypoint")
    if not isinstance(payload,bytes):
        raise SandboxUnknown("STOP_UNKNOWN: payload must be bytes")
    cmd=[bwrap,"--die-with-parent","--new-session","--unshare-user",
         "--unshare-pid","--unshare-ipc",
         *(["--share-net"] if synthetic_filesystem_only else ["--unshare-net"]),
         "--unshare-uts",
         "--ro-bind",str(code),"/code","--ro-bind",
         str(pathlib.Path(role_stage).resolve()),"/role",
         *_mount_system_ro(),"--tmpfs","/tmp","--proc","/proc",
         "--dev","/dev","--chdir","/code",
         "--setenv","HOME","/tmp","--setenv","PYTHONPATH","/code",
         "--setenv","WORLD_CAL_ROLE",role,
         "--",sys.executable,"-I","-c",
         "import runpy,sys; sys.path.insert(0, '/code'); "+
         "runpy.run_path("+repr(str(pathlib.Path("/code")/entrypoint))+",run_name='__main__')"]
    try:
        result=subprocess.run(cmd,input=payload,capture_output=True,
                              timeout=timeout,check=False,env={
                              "PATH":"/usr/bin:/bin",
                              "PYTHONHASHSEED":"0","OPENBLAS_NUM_THREADS":"1",
                              "OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1"})
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise SandboxUnknown("STOP_UNKNOWN: isolated process unavailable") from exc
    if result.returncode:
        raise SandboxUnknown("STOP_UNKNOWN: isolated process failed code="+str(result.returncode)
                             +" stderr="+result.stderr[:250].decode("utf-8","replace"))
    return result.stdout
