# WORLD CAL 実装 GO — 監督者への仕様解釈逆質問（実装から分離）

id: WORLD-CAL-IMPLEMENTATION-RQ-20261111-01
status: OPEN_QUESTIONS / SUPERVISOR_RESPONSE_REQUIRED / NOT_CAL_AUTHORIZED
updated: 2026-11-11
tags: world-expansion, cal-implementation, research-lead, supervisor-questions, fail-closed

**根拠**: [仕様第6版（PR #194 exact head）](https://github.com/ryonakayama234/DekaSugi/blob/351016fe0e2d468c80736a477133a274cfb713b8/docs/research/WORLD-PREREG-SPEC-20261110-06-specification-pack-v6.md)、[Owner 承認プロトコル（PR #204 exact head）](https://github.com/ryonakayama234/DekaSugi/blob/156491a5e710b2ef8b7ea38d9fa92f83439aa9f5/docs/research/WORLD-CAL-PROTOCOL-20261111-01-lead-draft.md)、[実装計画 §2/§3（PR #205）](https://github.com/ryonakayama234/DekaSugi/pull/205)。本逆質問は計測・承認値の変更を提案するものではなく、不整合を解釈で埋めないための別紙である。

## RQ-CAL-IMPL-01: K0 BFS の具体 token 数

実装計画 §2 は `k0_open_loop` の action token を「24」と述べる。一方、仕様第6版付表Aは11種類（INSERT(Sym) を含む）で、phase live alphabet の Sym が4個なら `11-1+4=14` 個の単一呼出可能 concrete token と読める。**24 の内訳**を明示してほしい。何かが `SET_ANCHOR` などのパラメータ付加で増えるなら、付表Aと Space の token domain に規範上の根拠が必要である。暫定実装は14 token を全列挙し、24 を暗黙に追加していない。完全 K0 監査は回答前 PASS としない。

## RQ-CAL-IMPL-02: PRF 53-bit open-interval の binary64 上端

プロトコル §5 は `x` を53-bit整数として `u=(x+0.5)/2^53` を binary64 に置く。最大 `x=2^53-1` の数学的有理数は 1 未満だが、**binary64 最近接偶数丸めでは 1.0** になり得る。Box–Muller の `0<u<1` と衝突する。現候補は `u>=1` を `STOP_UNKNOWN` とする（clamp/re-draw/range変更は実装判断でしない）。監督者は仕様の丸め規則（例: directed rounding、`nextafter`）、閾値一致の検証要件を明示してほしい。固定 source を黙って変更しない。

## RQ-CAL-IMPL-03: Contrast B の gate aggregation

Gθ 仕様は「FULL − max(7対照の B 時点集約成功率)」を同一 Y から作るが、2 gate = G1/G2 のどちらをどう集約するかが、当該一文だけでは一意でない。暫定 `gtheta.aggregate_law` は G1 成功率を参照するが、**規範決定・10 AND 検査としての使用は未承認**。二 gate の同重み平均か、G1/G2 いずれかか、別に評価する量かを確定してほしい。解決まで integrated power を実装・実行せず STOP_UNKNOWN。

## RQ-CAL-IMPL-04: exact Sampford の独立検算・数値停止

`world_cal/sampford.py` には小 N 独立全列挙と、同じ exact Sampford law の加重 Poisson-binomial 多項式を利用した `pi_ll'` DP 候補を置いた。**N=336 の q、certainty 分離、n 全域の数値条件は未独立監査**。監督者側の別 actor による exact 二次包含照合、退化 `pi_ll'=0`、float tolerance と STOP 条件の確認を依頼する。近似 `pi_ll'` への無断置換はしない。

## RQ-CAL-IMPL-05: 計測された CPU feasibility の次の関門

[profiler 報告](WORLD-CAL-SYNTHETIC-PROFILER-REPORT-20261111-01.md)では、小規模単体 PRF/Gθ カーネル速度で `n=2..336` 全走査の理論 binary outcomes に対して **約63.2 wall日**の単純外挿が示される一方、統合段階の要件を測っていない。実資源制限の監査条件が未定義。**現在は STOP_UNKNOWN** とし、どの現実的 CPU/wall/RSS 確認が別 Owner の CAL_AUTHORIZED 判断に必要かを明示してほしい。算術的 calls cap の余裕を実行可能性と混同しない。

以上は**解決待ち**であり、検査の迂回・仕様／プロトコル改訂・正式 CAL の GO を意味しない。
