# EXP-REP-004R — G0–G6一括実行計画 v1（未実行）
id: EXP-REP-004R-PLAN-V1
status: DESIGN_ONLY / NOT_RUN / NOT_F0_FROZEN
updated: 2026-11-02
tags: experiment, plan, learning, disclosed, not-run
issue: https://github.com/ryonakayama234/DekaSugi/issues/139

**研究正本**: docs/specs/EXP-REP-004R.md。これは修正後の工学実験を事前に記述した候補であり、別所有の正式F0/FINAL事前登録ではない。作業中に閾値や比較条件を動かすなら別版/新runで追跡する。

| Gate | 作業 | 主要出力 | 前提・不合格時 |
|---|---|---|---|
| G0 | 設計・評価方法・差分規約・source/manifestを固定 | method, digest, NOT_RUN ledger | 採点前承認; 裏付けないformal status禁止 |
| G1 | 旧版でP1/P2の再現; 24置換×16状態×4 pulse検査 | failing tests→pass witness | 反例が残ればSTOP |
| G2 | 最小コード修正、baseline独立化、CI、独立head review | patch, review, checked docs | P1/P2/観測隔離FAILならSTOP |
| G3 | TRAIN0/3/8/16/32/64→Sleep→Snapshotを新規生成 | 6個の保存済Snapshot/概念数/ハッシュ/訓練費用 | TRAINからhost truth流入ならSTOP |
| G4 | 保存物を新プロセスでロード→合法質問→予測確定→手元で使う | USE trace/commit、body mutation/ablation | 保存物非再現/違法操作ならSTOP |
| G5 | disclosed人工世界48×8腕×5予算×6 exposureの採点 | 11,520生行、集約、SHA、旧データとの差 | original archive不変、private/FINAL使用禁止 |
| G6 | 家族単位の結果再集計とレビュー、採否決定 | 不合格含む研究run、PR evidence、将来提案 | formal science/model promotion禁止 |

## 測定明細
- primary universe: UNSEEN_COMPOSITION 12 distinct semantic families。family内の5 action budgetsと64 transition checksは反復測定。
- primary outcomes: signed mean Δ(LQ-LA), Δ(LQ-STATIC-MACRO), Δ(LQ-FA)。family別正/負/同点、0/1/2/4/8の層、行動列差、不可識別/ABSTAINを併記。
- secondary: ライブラリbody数/異なるbody、条件付きガード適合率、同時XOR意味同値性、seen_in_train、train size依存、負の転移、OOD到達可能な矛盾と観測不足を区別した表記。
- cost: paid set/pulse、model checks、actual interpreter evaluations/cache hits、train+sleep+fresh-use+score CPU, RSSが測れなければnot_observed、use N=1/10/100の償却（推測でゼロにしない）。
- n=0は固定対照を含め必ず実行し、n=64の32ファミリー重複を明記。repeat同一データ1/2/5/10の効果は別診断でありneural epochと呼ばない。
- OOD12は同一3-edge chain topologyのrenamingであり12個の独立文法外ファミリーと解釈しない。
- 事前目安: Δ(LQ-LA)>=+0.02 & Δ(LQ-STATIC)>=+0.02 & Δ(LQ-FA)>=+0.02 & 9/12 family positive and all gates clean。目安を達成しても正式科学採用は別ゲート。達成しなければNEGATIVE/NULLを公表。

## 実行コマンド（現在のCLI仕様に準拠、修正前に採点しない）
~~~bash
python -m unittest tests.test_rep004_engineering -v
python scripts/check_docs.py
python -m packages.rep004 preflight --output .run/rep004r/preflight.json
python -m packages.rep004 train --train-worlds 64 --snapshot .run/rep004r/snapshot64.json
python -m packages.rep004 inspect --snapshot .run/rep004r/snapshot64.json
python -m packages.rep004 use --snapshot .run/rep004r/snapshot64.json --world-index 501 --arm LQ --budget 8 --trace .run/rep004r/use64.json
python -m packages.rep004 evaluate-disclosed --snapshot .run/rep004r/snapshot64.json --output .run/rep004r/score64.json
~~~
実際の6水準の管理・原本SHA保全・physical-vs-logicalメーターを含むrunnerは後続実装対象であり、上記コマンドの成功をこの設計文書は主張しない。旧採点原本・旧Snapshotへの書込禁止。コード/DATA/CI/diagram/contract/runを同一レビュー可能PRで同期。

## 保全・レビュー
old PR #138 の raw sha=70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3 に触れない。source/manifest/plan/policy SHAを採点開始前にrunへ記載し、最初のscoreより後の方法修正は別run IDを採番。CI greenは学習有効性を証明しない。Independent exact-head reviewが未完了ならreview_pendingを保持する。正式なsealed評価・main merge・Releaseはこの計画の範囲外。


## Hypothesis
- H-INV: fully role-bound atomic/guarded/two-edge AST semantics is invariant under all 24 permutations of four object indices, checked on all 16 states and all 4 pulse actions (and legal set state transformations).
- H-CONTROL: STATIC-MACRO fixed-library query weights/actions/predictions are exactly independent of TRAIN0 vs TRAIN64 and do not read the learned library.
- H-Q: for 12 distinct unseen-composition semantic families the paired family-mean predictive effect Δ(LQ−LA) is positive, tested without assuming any gain.
- H-UNIQUE: the learned concept adds predictive value beyond both an independently installed STATIC-MACRO control and strong fixed FA; if not, no learned-unique claim.
- H-DOSE: variation in distinct training exposure, not deterministic replay epoch count, can change outcomes; no monotonicity assumption.

## Metrics
Primary: equal-family-weighted mean Δ for LQ−LA, LQ−STATIC-MACRO, and LQ−FA over 12 unseen-composition families, each averaging budgets 0/1/2/4/8; per-trial accuracy is correct transitions / 64, ABSTAIN utility is 0 by preregistered convention. Report 12 signed family-level differences, 5 budget strata, counts better/worse/tied, action divergence, coverage and abstentions. 64 audit transitions and 5 budgets are repeated measures, **not independent samples**.
Secondary: TRAIN paid actions, distinct semantic TRAIN families, AST and witness diversity, zero-training control invariance, body logical/physical invocations, cache hits, model checks, fresh-USE CPU, learning + Sleep + Snapshot CPU, resource amortization at 1/10/100 uses; missing metrics are not_observed. The OOD12 are renamed variants of one three-edge-chain topology and cannot establish generalized OOD calibration.

## Acceptance
Engineering preflight PASS requires 24-permutation exact semantic invariance, independent static-macro behavior for TRAIN0/64, valid public-only observed traces, fixed action charges, integrity-correct snapshots, pure interpreter, preserved historical SHA, exact-head tests/docs/review. Any failure causes STOP before scoring.
Exploratory candidate threshold, not scientific significance: Δ(LQ−LA)>=+0.02 AND Δ(LQ−STATIC-MACRO)>=+0.02 AND Δ(LQ−FA)>=+0.02, LQ−LA positive in >=9/12 families, no boundary violation, and full cost disclosures. Otherwise preserve NULL/NEGATIVE and do **not** promote a learned model. Only an independent future custodied, source-frozen fresh-FINAL can support formal scientific adoption.


## Implementation activation receipt (2026-11-02)
The owner authorized one substantial G1–G6 synthetic execution, with discretion over implementation and auditing. The remediation PR adds role-binding and fixed-comparator regression tests, a disclosed six-exposure runner (`scripts/run_rep004r.py`), and CI artifact preservation. A successful workflow run and raw checks are required before **any** measured-result claim. This implementation does not authorize historical holdout access, main merge, F0/FINAL or promoted release.
