#!/usr/bin/env python3
"""Execute independent-role OS read-denial checks, no CAL, K0 or simulation.

Requires Linux bubblewrap with unprivileged user namespaces. If unavailable,
fail CLOSED as STOP_UNKNOWN instead of treating the in-process ACL as proof.
"""
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import tempfile
from world_cal.role_boundary import launch_isolated, SandboxUnknown

PROBE = r'''
import json
import os
from pathlib import Path
attempts = {}
for path in ("/role/public/trace", "/role/private/verifier_truth",
             "/role/design/split_metadata", "/role/abstract/generator_laws",
             "/role/audit/logs", "/etc/shadow"):
    try:
        attempts[path] = {"opened":True,"size":len(Path(path).read_bytes())}
    except (OSError, PermissionError):
        attempts[path] = {"opened":False}
print(json.dumps({"pid":os.getpid(),"role":os.environ.get("WORLD_CAL_ROLE"),
                  "paths":attempts},sort_keys=True))
'''

def audit():
    with tempfile.TemporaryDirectory(prefix="world-cal-role-audit-") as directory:
        root=pathlib.Path(directory)
        code=root/"code";code.mkdir()
        (code/"role_probe.py").write_text(PROBE,encoding="utf-8")
        stages={};results={}
        for role,pub in (("LEARNER_ARMS","public/trace"),
                         ("EVALUATOR","private/verifier_truth")):
            stage=root/role;stage.mkdir()
            p=stage/pub;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(("synthetic-"+role+"-marker").encode())
            stages[role]=(stage,{pub:hashlib.sha256(p.read_bytes()).hexdigest()})
        for role,(stage,manifest) in stages.items():
            out=launch_isolated(role,code_root=code,role_stage=stage,
                    entrypoint="role_probe.py",manifest=manifest)
            result=json.loads(out)
            if result["role"]!=role:raise SandboxUnknown("STOP_UNKNOWN: wrong role identity")
            permitted="/role/"+next(iter(manifest))
            if not result["paths"][permitted]["opened"]:
                raise SandboxUnknown("STOP_UNKNOWN: permitted read failed")
            if any(info["opened"] for path,info in result["paths"].items()
                   if path!=permitted):
                raise SandboxUnknown("STOP_UNKNOWN: cross-role read succeeded")
            results[role]=result
        return {"kind":"SYNTHETIC_PROCESS_AND_MOUNT_NAMESPACE_READ_PATH_AUDIT",
                "status":"LOCAL_ROLE_NEGATIVE_TEST_PASS_NOT_INDEPENDENT_SUPERVISOR_PASS",
                "environment":{"python":platform.python_version(),
                               "platform":platform.platform()},
                "results":results,"secret_created":False,
                "cal_executed":False,"sealed_split_materialized":False}

if __name__=="__main__":
    try:print(json.dumps(audit(),sort_keys=True,indent=2))
    except SandboxUnknown as exc:
        print(json.dumps({"kind":"SYNTHETIC_OS_ROLE_AUDIT","status":"STOP_UNKNOWN",
                          "reason":str(exc)}),file=sys.stderr)
        sys.exit(2)
