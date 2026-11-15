"""Stdlib-only, unlabelled Owner worksheet; no project imports or learner calls."""
import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "experiments/SENTENCE-REVISION-1/preparation/source-lock-v1.json"
LOCK_SHA = "3d31660fe094cb00c83c4542aed1c8f98c222d4c5d792006d8f26f9e31813f96"
LOCK_COMMIT = "ae9d10427c438ba9d82b248ec8001b5ecdccece3"
ROLES = ("initial_1", "initial_2", "correction", "unseen_related",
         "unseen_previous_application", "unseen_near_counterexample")
# Hand-declared structural inputs, selected without any condition search, Case,
# prediction, expected label, source-text interpretation or model feedback.
INPUTS = (
    (("AABCA", 2), ("BCBCB", 2), ("ACADC", 2), ("BDBAD", 2), ("DADAD", 2), ("ACBDC", 2)),
    (("ABAACD", 3), ("BCDABC", 3), ("DABBCD", 3), ("ACDDBA", 3), ("BCBBDA", 3), ("DABCCD", 3)),
    (("ABCCADA", 4), ("BCDABCD", 4), ("CADDBAC", 4), ("DBAACBD", 4), ("DABCDBD", 4), ("CADDCAC", 4)),
    (("ABCDDABA", 3), ("BCABACDB", 3), ("CDAACBDC", 3), ("DABBDCAD", 3), ("ACBDDBCA", 3), ("CDABCBDC", 3)),
)


def canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def verify_source(root=ROOT):
    lock_path = root / LOCK.relative_to(ROOT)
    if sha256(lock_path.read_bytes()).hexdigest() != LOCK_SHA:
        raise ValueError("source lock changed; no automatic reseal")
    lock = load_json(lock_path)
    for path, expected in lock["source_sha256"].items():
        data = (root / path).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError("pinned source changed: " + path)
    return lock


def state(text, cursor):
    if (type(text) is not str or not 4 <= len(text) <= 8
            or any(c not in "ABCD" for c in text)
            or type(cursor) is not int or not 0 < cursor < len(text)):
        raise ValueError("outside fixed state domain")
    return {"buffer": list(text), "cursor": cursor, "selection": None, "clipboard": []}


def alternatives(before):
    after = copy.deepcopy(before)
    del after["buffer"][after["cursor"]]
    return {"delete_right": after, "keep": copy.deepcopy(before)}


def records():
    return [{"rule_id": f"R{c + 1:02d}", "example_id": f"R{c + 1:02d}-{p + 1:02d}",
             "before": state(text, cursor), "right_character": text[cursor],
             "alternatives": alternatives(state(text, cursor)),
             "owner_choice": None, "owner_note": None}
            for c, case in enumerate(INPUTS) for p, (text, cursor) in enumerate(case)]


def validate_rows(rows):
    if type(rows) is not list or len(rows) != 24:
        raise ValueError("exactly24 rows required")
    seen = set()
    for n, row in enumerate(rows):
        expected_case = f"R{n // 6 + 1:02d}"
        if (set(row) != {"rule_id", "example_id", "before", "right_character",
                         "alternatives", "owner_choice", "owner_note"}
                or row["rule_id"] != expected_case
                or row["example_id"] != f"{expected_case}-{n % 6 + 1:02d}"):
            raise ValueError("row identity/order/fields changed")
        b = row["before"]
        if (type(b) is not dict or set(b) != {"buffer", "cursor", "selection", "clipboard"}
                or type(b["buffer"]) is not list or any(type(c) is not str or c not in "ABCD" for c in b["buffer"])
                or b != state("".join(b["buffer"]), b["cursor"])):
            raise ValueError("state shape changed")
        key = canonical(b)
        if key in seen:
            raise ValueError("duplicate production state across roles/cases")
        seen.add(key)
        if (row["right_character"] != b["buffer"][b["cursor"]]
                or row["alternatives"] != alternatives(b)):
            raise ValueError("mechanical output mismatch")
        if row["owner_choice"] is not None or row["owner_note"] is not None:
            raise ValueError("public preparation must remain unlabelled; Muse private copy only")
    for c in range(4):
        correction, near = rows[6*c+2]["before"], rows[6*c+5]["before"]
        if correction["cursor"] != near["cursor"] or len(correction["buffer"]) != len(near["buffer"]):
            raise ValueError("near structural pairing changed")
        different = [i for i, (a, b) in enumerate(zip(correction["buffer"], near["buffer"])) if a != b]
        if different != [correction["cursor"]]:
            raise ValueError("near row must differ only at the deletion position")
    if rows != records():
        raise ValueError("declared unlabelled input table changed")


def vector(s):
    return f"({''.join(s['buffer'])}, {s['cursor']}, なし, 空)"


def worksheet(rows):
    lines = ["# Owner確認用：24例の状態表", "",
        "id: SENTENCE-OWNER-WORKSHEET-V1", "status: PREPARED / OWNER_UNCONFIRMED / NOT_RUN",
        "updated: 2026-11-15", "tags: owner-session, unlabelled-state-table", "",
        "状態表だけを準備しました。正解・8短文は未入力です。2つの結果候補に推奨はありません。", "",
        "各ケースでは、先頭・直前・カーソル右・末尾の文字の関係を使い、どんなときに右の1文字を消したいかを決めてください。「同じ／違う」の関係を1つ、または2つとも満たす場合までを扱います。ケース間は別の基準で構いませんが、同じケースの6行には一貫した基準を使います。", "",
        "`▏`はカーソル、cursorは左から何文字あるかです。状態の4欄は `(buffer, cursor, selection, clipboard)`。この表の入力ではselectionは「なし」、clipboardは「空」で、どちらの操作後も維持します。削除してもcursorは動きません。", "",
        "各行で「削除／そのまま／保留」を選び、必要ならメモを付けてください。初期選択はありません。答えを記入したコピーはMuseが非公開で保持します。回答済み表や未見正解はGitHubやLeadへ返さないでください。", "",
        "例の選択と短文作成は、予測や成績を見る前に終えます。こちらから正解や規則を代筆しません。"]
    for c in range(4):
        lines += ["", f"## ケース R{c+1:02d}", "",
            "|例ID|編集前（カーソル位置）|編集前4欄|対象文字|削除した場合の4欄|そのままの場合の4欄|Ownerの選択・メモ|",
            "|---|---|---|---|---|---|---|"]
        for r in rows[c*6:(c+1)*6]:
            b = r["before"]; i = b["cursor"]; text = "".join(b["buffer"])
            view = text[:i] + "▏" + text[i:]
            lines.append(f"|{r['example_id']}|`{view}`|`{vector(b)}`|{r['right_character']}|`{vector(r['alternatives']['delete_right'])}`|`{vector(r['alternatives']['keep'])}`|未回答|")
        lines += ["", "初期説明（Ownerの1文）：＿＿＿＿", "", "訂正／確認（Ownerの1文）：＿＿＿＿", "",
                  "読み戻し確認：未確認。保留・修正メモ：＿＿＿＿"]
    lines += ["", "## 2回の進め方", "",
        "|時間|第1回：R01・R02|第2回：R03・R04|", "|---|---|---|",
        "|0〜3分|2候補と保留の説明|前回の保留・変更箇所の確認|",
        "|3〜15分|12行を選択|残る12行を選択|",
        "|15〜22分|初期2文＋訂正2文を作成|初期2文＋訂正／確認2文を作成|",
        "|22〜25分|12例＋4文を読み戻す|24例＋8文を読み戻し、Museへ渡す|", "",
        "50分＋保留解消の余裕10分、合計60分で止めます。セッション間も学習者を走らせません。日程の予約は行っていません。", "",
        "入力状態の変更は、予測前の意図修正としてMuseが元表との差分を記録します。成功例を選ぶための差し替えは行いません。矛盾・文法外の意図・保留が残る場合は固定しません。", "",
        "受入済みsource/settingsは先に固定済みです。この表はまだデータ固定物ではありません。本番の予測取得・採点は別判断です。", ""]
    return "\n".join(lines)


def make(folder):
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    lock = verify_source()
    rows = records(); validate_rows(rows)
    cases = [{"rule_id": f"R{c+1:02d}", "intended_role": "revise" if c < 3 else "confirmation",
              "role_status": "preassigned_intent_not_guaranteed_initial_error_or_correctness",
              "initial_text": None, "correction_text": None,
              "allocations": [{"example_id": rows[6*c+p]["example_id"], "planned_role": role,
                               "probe": p, "semantic_role_confirmed": False}
                              for p, role in enumerate(ROLES)]} for c in range(4)]
    owner = {"schema": "sentence-owner-input-template/1", "custodian": "Muse private copy only",
             "rows": [{"example_id": r["example_id"], "choice": None, "note": None} for r in rows],
             "texts": [{"rule_id": c["rule_id"], "initial_text": None, "correction_text": None,
                        "readback_confirmed": False} for c in cases],
             "session_minutes": [None, None], "reserve_minutes": None, "status": "not_answered"}
    plan = {"schema": "sentence-muse-allocation-proposal/1", "status": "pending_owner_and_Muse_data_freeze",
            "source_lock_commit": LOCK_COMMIT, "cases": cases,
            "allocation_counts": {"initial": 8, "correction": 4, "unseen": 12},
            "structural_design": "Each near row changes only the correction-input right character. Related rows rename symbols. All24 input states are distinct and length5..8. No condition search or predictions were used.",
            "semantic_roles": "Related/previous-application/near-counterexample are provisional intentions. Muse must confirm against Owner intent/labels. Structural similarity alone does not establish applicability or opposite truth. No post-prediction relabelling/replacement.",
            "before_data_freeze": ["Owner supplies24 choices and8 texts privately; no prefilled labels",
                "Read back every selected complete final state and each sentence; retain corrections/history and time totals",
                "Muse checks domain, duplication, consistent Owner intent and allowed grammar without obtaining learner predictions",
                "Confirm provisional8/4/12 allocations and all semantic roles before final presentation order",
                "Seal public initial8+4 initial texts, disclosure4+4 correction texts, evaluator-only unseen12 gold/roles as distinct files",
                "Hash full24/8 texts, split, presentation order, source pin and custody references in one private manifest",
                "Never copy unseen gold to Lead or public repository; unresolved/contradictory cases remain not_ready; no invented answers",
                "Any required runtime/source change invalidates the pin; preserve history and do not tune on this table",
                "Seek a separate production execution decision; current official entry stays closed"],
            "lead_visible_expected_outputs": "only both unselected mechanical alternatives; no Owner-selected gold",
            "official_predictions": "not_run", "official_scoring": "not_run"}
    payloads = {"state-table-v1.json": {"schema": "sentence-unlabelled-table/1", "status": "owner_unconfirmed", "rows": rows},
                "owner-input-template-v1.json": owner, "muse-allocation-proposal-v1.json": plan}
    folder.mkdir(exist_ok=False)
    paths = []
    for name, value in payloads.items():
        path = folder / name; path.write_bytes(canonical(value)); paths.append(path)
    path = folder / "owner-worksheet-v1.md"; path.write_text(worksheet(rows)); paths.append(path)
    index = {"schema": "sentence-owner-packet/1", "status": "ready_for_Owner_session_not_data_frozen",
             "source_lock_commit": LOCK_COMMIT, "source_lock_sha256": LOCK_SHA,
             "accepted_source_commit": lock["accepted_commit"],
             "generator_path": str(Path(__file__).relative_to(ROOT)),
             "generator_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
             "files_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in paths},
             "rows": 24, "cases": 4, "owner_choices_entered": 0, "owner_texts_entered": 0,
             "preparation_cpu_seconds": time.process_time()-start_cpu,
             "preparation_wall_seconds": time.perf_counter()-start_wall,
             "active_payload_bytes": sum(p.stat().st_size for p in paths),
             "budget": {"shared_cpu_cap_seconds": 7200, "lead_muse_hours_cap": 16, "external_yen": 0,
                        "owner_minutes_cap": 60, "lifetime_ledger": "Muse joins prior stage/accounting receipts before any production GO; no new run allowance from this preparation receipt"},
             "learner_calls": 0, "model_predictions": 0, "scores": 0,
             "data_freeze": "pending_Muse_after_Owner_confirmation"}
    if index["active_payload_bytes"] > 1048576 or index["preparation_cpu_seconds"] > 60:
        raise ValueError("preparation budget exceeded")
    (folder / "packet-index-v1.json").write_bytes(canonical(index))
    return check(folder)


def check(folder):
    verify_source()
    index = load_json(folder / "packet-index-v1.json")
    if (index["source_lock_commit"] != LOCK_COMMIT or index["source_lock_sha256"] != LOCK_SHA
            or index["generator_sha256"] != sha256(Path(__file__).read_bytes()).hexdigest()):
        raise ValueError("packet pin/provenance changed")
    expected = {"state-table-v1.json", "owner-input-template-v1.json", "muse-allocation-proposal-v1.json", "owner-worksheet-v1.md"}
    if set(index["files_sha256"]) != expected or {p.name for p in folder.iterdir()} != expected | {"packet-index-v1.json"}:
        raise ValueError("missing/extra packet artifact")
    for name, digest in index["files_sha256"].items():
        if sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise ValueError("packet changed: " + name)
    validate_rows(load_json(folder / "state-table-v1.json")["rows"])
    inputs = load_json(folder / "owner-input-template-v1.json")
    if (any(r["choice"] is not None or r["note"] is not None for r in inputs["rows"])
            or any(c["initial_text"] is not None or c["correction_text"] is not None or c["readback_confirmed"] for c in inputs["texts"])):
        raise ValueError("filled Owner input must remain private")
    return {"status": "pass", "source_lock_verified": True, "rows": 24,
            "owner_choices": 0, "owner_texts": 0, "learner_calls": 0,
            "official_predictions": "not_run", "official_scoring": "not_run"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("make", "check"))
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    print(json.dumps(make(args.folder) if args.mode == "make" else check(args.folder), sort_keys=True))
