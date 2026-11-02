# EXP-REP-005 V2 — 設計と実行状態

id: EXP-REP-005-V2-DECISION-20261102
status: g0a_synthetic_method_implemented_pending_ci_g0b_not_certified
updated: 2026-11-02
tags: experiment, representation, plan, not-run

[研究決定稿](../../../docs/specs/EXP-REP-005-DECISION-V2.md) / [PR整理監査](../../../docs/research/20261102-research-pr-portfolio-audit.md)

| 工程 | 現在の状態 |
|---|---|
| 3有料操作による反例と24役割置換 | 別Draft #145でG0方法プレチェック済み。今回の設計作業では再実行していない |
| G0b：独立80意味ファミリーの構築・検査 | NOT_VERIFIED |
| G1/G2：公開操作・完全意味検査の承認 | NOT_RUN |
| G3：有料TRAIN、Sleep、Snapshot、未知世界使用 | NOT_RUN |
| G4/G5：対照条件・公開人工スコア | NOT_RUN |
| F0正式封印評価、main昇格 | NOT_AUTHORIZED |

この文書は実験成績ではない。NULL、NEGATIVE、NOT_RUNは数値のゼロとは異なる。旧研究の出力や生データは変更しない。

## 2026-11-02 — G0a method implementation checkpoint

- Main-based selective source port of [g0_witness.py](../g0_witness.py) and [witness tests](../../../tests/test_rep005_g0_witness.py) from Draft #145. Unmodified original source blob SHA: 71b306ce520ab82ba412368a92c941ab4dc41eb8 ; test blob SHA: f021433c4aca482087683885f08d8d30915fe9d8 . Earlier Draft results are not newly scored trials.
- New [g0_axes.py](../g0_axes.py) and [adversarial unit tests](../../../tests/test_rep005_g0_axes.py): representation class is independent of eight-action finite hypothesis identification. An intentionally out-of-grammar negative may correctly pass diagnostic G2; node exhaustion must return NOT_CERTIFIED.
- Restricted fixture world family upper bound: 14 role-permutation orbits (guard 12, always 1, never 1). Hence G0b quota 80 is **IMPOSSIBLE WITH THIS RESTRICTED GENERATOR**. The number is an *upper bound* on independently distinct families, not the actual count, and NOT a proof that a richer future full Hplus generator cannot reach 80.
- No trusted signed real-action receipt, full semantic equivalence auditor, 80 verified structural families, preregistered independent split, paid learning, Snapshot, hidden score or statistical power certificate is present. Scientific G0b: FAIL_FEASIBILITY_IN_CURRENT_FIXTURE / STOP. Future redesign can broaden the generator only in a separate preregistered and independently reviewed PR.
- Synthetic unit-test result: PENDING_GITHUB_CI at time of this checkpoint. A local independent prototype of the classification logic exercised 9 unittest cases successfully, but does not certify this exact GitHub head. Exact GitHub CI result must be separately attached without rewriting previous result statements.
