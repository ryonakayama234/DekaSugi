"""Deterministic Markdown from saved batch results; no learner feedback."""
import json

from .arms import ARMS
from .artifacts import attributed
from .foundation import Fault, Meter


def _safe(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("\n", "<br>").replace("`", "&#96;")


def render(results, *, meter):
    if type(meter) is not Meter:
        raise Fault("required shared Meter")
    with attributed(meter, "shared/report"), meter.phase("report"):
        if type(results) is not list or len(results) != 4:
            raise Fault("report requires all four batch-scored cases")
        lines = ["# SENTENCE-REVISION-1 — artificial engineering report", "",
                 "人工fixtureのみ。固定renderer。独立単位は4ケース。192予定出力中、主診断は未見96出力。", "",
                 "予算・棄権・空候補を成功として補完しない。母集団推定・能力認定は行わない。", "",
                 "実行完了はcompletion.jsonで確認する。stop.jsonがあれば、本票を含む途中成果物より停止状態を優先する。", ""]
        for case in results:
            lines += [f"## Case {case['case']} / {_safe(case['rule_id'])}", "",
                      f"事前の役割: {_safe(case['intended_role'])}", "",
                      f"初期文: {_safe(case['initial_text'])}", "",
                      f"訂正／確認文: {_safe(case['correction_text'])}", "",
                      "|方式|未見 前→後|差|初期正答の喪失|訂正 前→後|近接反例 前→後|規則変更|残候補|除外候補|", "|---|---:|---:|---:|---:|---:|---|---:|---:|"]
            for a in ARMS:
                r = case["arms"][a]
                count = lambda x: "—" if x is None else len(x)
                lines.append(f"|{a}|{r['unseen_before']}→{r['unseen_after']}|{r['delta']}|{r['lost_initial_correct']}|{r['correction_before']}→{r['correction_after']}|{r['near_before']}→{r['near_after']}|{r['selection_changed']}|{count(r['remaining'])}|{count(r['removed'])}|")
            lines += ["", "費用（CPU/wallの実測はcost-receipts-NNN.jsonのscope別記録とcompletion.jsonを参照）。", "",
                      "|方式|列挙|候補×例検査|条件原子評価|原子遷移|提出|", "|---|---:|---:|---:|---:|---:|"]
            for a in ARMS:
                owned = [x for x in meter.receipts if x.get("scope", "").startswith(f"case{case['case']}/{a}/")]
                totals = {k: sum(x["counts"][k] for x in owned) for k in meter.counts}
                lines.append("|" + a + "|" + "|".join(str(totals[k]) for k in meter.counts) + "|")
            lines += ["", "共有準備・保存・検証・採点・結果票の費用はshared/caseの別scopeに記録し、方式の便益へ付け替えない。", ""]
            for a in ARMS:
                r = case["arms"][a]
                lines += ["", f"### {a}", "", f"観察: {r['observation']} / empty_after={r['empty_after']}", ""]
                for label, view in (("before", r["before"]), ("after", r["after"])):
                    lines += [f"{label}: {_safe(None if view is None else view['selected_ast'])}", "",
                              f"説明: {_safe(None if view is None else view['explanation'])}", ""]
                for label, hypotheses in (("残存", r["remaining"]), ("除外", r["removed"])):
                    lines += [f"{label}仮説:", ""]
                    if hypotheses is None:
                        lines += ["適用外（完全一致記憶）。", ""]
                    elif not hypotheses:
                        lines += ["0件。", ""]
                    else:
                        lines += [f"- {h['id']}: {_safe(h['ast'])} — {_safe(h['explanation'])}" for h in hypotheses] + [""]
            lines += ["### 全予定出力（probe0/1=初期、2=訂正、3/4/5=未見、5=近接反例）", "",
                      "|slot|入力全状態|status|correct|selected|期待全状態|出力全状態|", "|---|---|---|---|---|---|---|"]
            for row in case["rows"]:
                fmt = lambda value: _safe(json.dumps(value, ensure_ascii=False, sort_keys=True))
                lines.append(f"|{row['slot']}|{fmt(row['input'])}|{row['status']}|{row['correct']}|{row['selected_id']}|{fmt(row['expected'])}|{fmt(row['output'])}|")
            meter.checkpoint((case, lines))
        text = "\n".join(lines) + "\n"
        meter.checkpoint((results, lines, text))
        return text
