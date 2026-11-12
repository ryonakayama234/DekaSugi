"""E2 normalized ACL + role read separation, exact CSV bytes and fail-closed logs."""
import csv
import hashlib
import io
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

ACL_SHA="faf1962fd4737033f6056f24a9cd1e6b629826e1aeb6ad8bdbc7cb50fa76b44c"
ARMS=("FULL","OFF","PRED-ONLY","REC","RANK-ONLY","FIXED-IF","LOOKUP","H+")
PAIRS=(("ATOM","NONE"),("SEQ","COMPOSE"),("SEQ","ABSTRACT"),("BIND","COMPOSE"),
       ("BIND","ABSTRACT"),("COMPARE","PREDICATE_SLOT"),
       ("BRANCH","BRANCH_CONSTRUCT"),("BRANCH","SEED_GIFT"))
PHASES=("TRAIN","G1","G2","CAL")
SOURCES=("PUB","SELF_SNAPSHOT","SEED_GIFT","SPACE_ENUM","CAL_ORACLE","CAL_DESIGN_META","SEC")
ACTIONS=("READ","REGISTER","USE")

ROLE_READS={
"LEARNER_ARMS":frozenset(("public/token_table","public/demo","public/history",
                          "public/trace","self/allowed_snapshot")),
"EVALUATOR":frozenset(("private/manifest","private/verifier_truth",
                       "private/frozen_snapshot","private/analysis_rule")),
"CAL_ORACLE":frozenset(("abstract/generator_laws",
                        "abstract/generator_instance_distribution","abstract/demo_distribution",
                        "abstract/feedback_rule","abstract/budget_rule")),
"BLIND_DESIGN_CALCULATOR":frozenset(("design/split_metadata:N_eligible,q,parent_cluster",
                                    "analysis/approved_theta_epsilon","analysis/alpha_beta",
                                    "analysis/G_theta_model","analysis/sampling_and_tests")),
"AUDITOR":frozenset(("audit/digests","audit/logs"))
}

class AccessDenied(PermissionError):pass

class AccessMatrix:
    def __init__(self,path=None):
        if path is None:
            path=Path(__file__).parent/"normative"/"WORLD-CAL-ACL-20261111-01-normalized-manifest.csv"
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=ACL_SHA:
            raise AccessDenied("E2 raw byte digest mismatch")
        lines=list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        expected={(arm,node,constructor,phase,source,action)
                  for arm in ARMS for node,constructor in PAIRS for phase in PHASES
                  for source in SOURCES for action in ACTIONS}
        self.rows={}
        if len(lines)!=5376:
            raise AccessDenied("E2 missing rows")
        for row in lines:
            key=tuple(row[x] for x in ("arm","node","constructor","phase","read_source","use_action"))
            if key in self.rows or key not in expected or row["allow"] not in ("true","false","True","False","1","0"):
                raise AccessDenied("E2 malformed/duplicate row")
            self.rows[key]=row["allow"].lower() in ("true","1")
        if set(self.rows)!=expected or sum(self.rows.values())!=383:
            raise AccessDenied("E2 key/allow set mismatch")
        for arm in ARMS:
            for pair in PAIRS:
                for phase in PHASES:
                    for source in ("SEC","CAL_ORACLE","CAL_DESIGN_META"):
                        for action in ACTIONS:
                            if self.rows[(arm,*pair,phase,source,action)]:
                                raise AccessDenied("learner privilege escape")
        for key,allowed in self.rows.items():
            if key[3]=="CAL" and allowed:raise AccessDenied("CAL learner escape")

    def check(self,arm,node,constructor,phase,source,action):
        if not self.rows.get((arm,node,constructor,phase,source,action),False):
            raise AccessDenied("E2 default deny")
        return True

def check_role_read(role,path,*,authorized=False):
    if path not in ROLE_READS.get(role,frozenset()):
        raise AccessDenied("role source read denied")
    if role in ("CAL_ORACLE","BLIND_DESIGN_CALCULATOR") and not authorized:
        raise AccessDenied("CAL role not yet authorized")
    return True

def require_uncontaminated(family_statuses):
    if "FAMILY_INVALID" in family_statuses:
        raise AccessDenied("STOP_INVALID: never valid-only reaggregate")

@dataclass(frozen=True)
class EpisodeRecord:
    episode_id: str
    phase: str
    task_tag: str
    action_event: str
    episode_outcome_kind: str
    observation_before_digest: str
    observation_after_digest: str
    full_cost_vector: dict
    event_kind: str|None=None

@dataclass(frozen=True)
class FamilyRecord:
    family_status: str

@dataclass(frozen=True)
class RunRecord:
    run_status: str
    run_inference_outcome: str|None=None
    all_digests: dict=field(default_factory=dict)

    def __post_init__(self):
        if self.run_status!="COMPLETE" and self.run_inference_outcome is not None:
            raise ValueError("STOP cannot carry inference outcome")

def audit_json_bytes(record):
    return (json.dumps(asdict(record),sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")

def trace_sha256(raw):
    return hashlib.sha256(raw).hexdigest()
