# Documentation Index / 資料目録

id: DOC-INDEX
status: active
updated: 2026-10-28
tags: navigation, architecture, research, experiments

**探す → 該当する小さな文書を読む → 必要な依存文書だけを辿る。**
長大な総合仕様書ではなく、永続的なIDとリンクで資料を接続する。

| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| VISION-001 | 研究目的・前提・非目標 | proposed | [mission](vision/mission.md) |
| ARCH-001 | 全体システム図・モジュール関係 | proposed | [system](architecture/system.md) |
| ARCH-002 | データ構造・境界・処理フロー | proposed | [contracts](architecture/contracts.md) |
| ADR-0001 | 研究優先の軽量構成 | proposed | [decision](architecture/decisions/ADR-0001-research-first.md) |
| PROC-001 | 仮説→実験→採否 | active | [workflow](process/workflow.md) |
| PROC-002 | GitHub運用・進捗管理 | active | [github](process/github.md) |
| ROADMAP | 実験ロードマップ | proposed | [roadmap](roadmap.md) |
| EXP-0001 | 型付きプログラム合成ベースライン | accepted baseline (EXP-0001) | [spec](specs/EXP-0001.md) / [plan](../experiments/EXP-0001/plan.md) |
| EXP-0002 | 共通部分式の発見と未知例での比較 | implemented in main; scientific promotion unaccepted | [spec](specs/EXP-0002.md) / [preregistered plan](../experiments/EXP-0002/plan.md) / [runs](../experiments/EXP-0002/runs/README.md) |
| EXP-0002-SEC-003 | Registry偽装と展開予算すり抜けの安全監査 | security remediations reviewed and merged to main | [review record](../experiments/EXP-0002/reviews/20261024-primitive-allowlist-hardening.md) / [PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6) |
| EXP-0002B-EVAL-GATE | 凍結方策による独立DEV/FINAL評価器 | main integrated; FINAL112 numeric gates PASS, not promoted | [evaluator code](../packages/kernel/evaluation.py) / [review gate](../experiments/EXP-0002B/reviews/20261025-evaluator-gate.md) / [Issue #25](https://github.com/ryonakayama234/DekaSugi/issues/25) |
| EXP-0002B-FINAL-ACTIVATION | FINAL112の1回限りの承認済み実行ゲート | completed; once-trigger retired after FINAL run | [activation audit](../experiments/EXP-0002B/reviews/20261025-final-activation.md) / [v2 protocol](../experiments/EXP-0002B/plan-v2.md) |
| EXP-0002B-FINAL-20261025 | FINAL112の保留評価・五つの数値採否・独立再集計 | metrics_pass_not_promoted; no total-CPU benefit proven | [FINAL measured run](../experiments/EXP-0002B/runs/20261025-final112.md) / [run index](../experiments/EXP-0002B/runs/README.md) / [CI #40176125696](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176125696) |
| EXP-0002B-DEV-20261025 | DEV48の工学的検査・生データ再現情報 | engineering smoke PASS; scientific adoption undecided | [measured run](../experiments/EXP-0002B/runs/20261025-dev-smoke.md) / [run index](../experiments/EXP-0002B/runs/README.md) / [CI #40162804951](https://github.com/ryonakayama234/DekaSugi/actions/runs/40162804951) |
| EXP-0002B-FREEZE | TRAIN結果とDataset/PolicySnapshot SHAの評価前固定 | fixed before DEV/FINAL; no new outcome | [freeze record](../experiments/EXP-0002B/freeze-v2.md) / [machine-readable hashes](../experiments/EXP-0002B/freeze-v2.json) / [Issue #23](https://github.com/ryonakayama234/DekaSugi/issues/23) |
| EXP-0002B-TRAIN | 訓練専用のgenerator・8次元features・KNN方策とhash付snapshot | frozen TRAIN policy reused unchanged for FINAL112 | [code](../packages/kernel/__init__.py) / [audit](../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md) / [Issue #21](https://github.com/ryonakayama234/DekaSugi/issues/21) |
| EXP-0002B | 文脈付き技能ON/OFF価値の学習 | FINAL112 numeric acceptance PASS; independent audit done; not promoted | [spec](specs/EXP-0002B.md) / [current v2 protocol](../experiments/EXP-0002B/plan-v2.md) / [historical v1](../experiments/EXP-0002B/plan.md) / [change log](../experiments/EXP-0002B/preregistration-v2-log.md) / [static audit](../experiments/EXP-0002B/reviews/20261024-audit-001.md) / [run index](../experiments/EXP-0002B/runs/README.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7) |
| MEASURE-0001 | verifier内primitive実行費用の観測（Kernel学習の前提） | CI and Codex code review passed; PR #18; no policy | [measurement](architecture/measurement.md) / [audit](../experiments/EXP-0002B/metering-log.md) / [runs index](../experiments/EXP-0002B/runs/README.md) / [Issue #17](https://github.com/ryonakayama234/DekaSugi/issues/17) |
| SEC-004 | Mutable lookupを信用しない実行Registryの再生成 | main-integrated; CI and Codex code-review verified | [security record](../experiments/EXP-0002/reviews/20261025-registry-snapshot-boundary.md) / [Issue #14](https://github.com/ryonakayama234/DekaSugi/issues/14) |
| EXP-0003A | WAKE–SLEEP/Counterfactual DREAMの設計・事前登録 | PR3 TRAIN/DREAM engineering implemented; DEV/FINAL outcomes not evaluated | [spec](specs/EXP-0003A.md) / [plan-v1](../experiments/EXP-0003A/plan.md) / [runs](../experiments/EXP-0003A/runs/README.md) |
| EXP-0003A-TRAIN | PR2の固定生成器・監査付きWAKE/SLEEP技能候補 | TRAIN engineering only, no performance claim | [code](../packages/exp0003a/__init__.py) / [run index](../experiments/EXP-0003A/runs/README.md) / [Issue #32](https://github.com/ryonakayama234/DekaSugi/issues/32) |
| EXP-0003A-PR3 | 固定Dream512プール・B2/B3各96例の選別とB1/B2/B3保守的方策 | TRAIN/DREAM engineering only; DEV/FINAL sealed | [source](../packages/exp0003a/pr3.py) / [CLI](../packages/exp0003a/pr3_cli.py) / [Issue #34](https://github.com/ryonakayama234/DekaSugi/issues/34) / [run index](../experiments/EXP-0003A/runs/README.md) |
| ARCH-UI-001 | Research Consoleパネル→module→data正本 | proposed interface contract, UI not implemented | [UI responsibility map](architecture/ui-panels.md) |
| RSRCH-INDEX | 研究資料の検索入口 | collecting | [research](research/INDEX.md) |
| RSRCH-001 | プログラム合成・抽象化 | notes | [program synthesis](research/program-synthesis.md) |
| TPL-SPEC | 仕様書テンプレート | active | [template](templates/spec.md) |
| TPL-EXP | 実験テンプレート | active | [template](templates/experiment.md) |
| PKG-INDEX | packages責務の一覧 | proposed | [packages](../packages/README.md) |

| EXP-0003A-FREEZE | source/split/policy/selectionのpre-DEV凍結 | PR4準備、DEV/FINAL未採点 | [frozen manifest](../experiments/EXP-0003A/freeze-v1.json) / [freeze record](../experiments/EXP-0003A/freeze-v1.md) / [PR4 code](../packages/exp0003a/freeze.py) / [run index](../experiments/EXP-0003A/runs/README.md) / [Issue #36](https://github.com/ryonakayama234/DekaSugi/issues/36) |

## METRO-0001 — Intelligence Metrology Foundation (design-only)
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| METRO-ONTOLOGY | 能力・可塑性・転移と観測/推定/主張の区別 | proposed | [ontology](metrology/ontology.md) |
| METRO-METRICS | 指標の定義・単位・欠測・比較条件 | proposed | [metrics](metrology/metrics.md) |
| METRO-EVIDENCE | EvidenceEnvelopeと読み取り専用の信頼境界 | proposed | [evidence-model](metrology/evidence-model.md) |
| METRO-VALIDITY | 構成概念妥当性・因果比較・不確実性 | proposed | [validity](metrology/validity.md) |
| ADR-0002 | Agent/Evaluatorから独立した測定層 | proposed | [metrology-boundary](architecture/decisions/ADR-0002-metrology-boundary.md) |
| METRO-0001 | 校正CAL-01：M1–M4の工学的受入条件 | preregistered proposal; not_run | [plan](../experiments/METRO-0001/plan.md) / [runs](../experiments/METRO-0001/runs/README.md) / [Issue #38](https://github.com/ryonakayama234/DekaSugi/issues/38) |

## AI向け検索方針
1. 質問に関連するIDかタグをこの目録で探す。
2. 目的が実装なら `specs` → `architecture/contracts` → 対応する `packages`。
3. 目的が「なぜこの設計か」なら `decisions`。科学的根拠は `research`。
4. 目的が「本当に改善したか」なら `experiments` の計画とrun。**計画と実測を混同しない**。
5. 意見の対立や未解決論点はIssueに登録し、資料には状態を明記。

## 文書の作成ルール
- 冒頭にID・status・updated・tagsを記載（README / AGENTS / GitHubテンプレートは例外）。
- 各文書は一つの責務だけ持つ。内容のコピーを増やさずリンクする。
- 変更時は参照元の図や契約を確認し、この索引も更新する。
- Mermaid図はMarkdown内に埋め込み、GitHub上で読めるようにする。

## METRO-0001 PR2 — 実装時に読む入口
[Fixture-only reducer](../packages/metrology/__init__.py) / [CAL-01 CLI](../packages/metrology/__main__.py) / [regression](../tests/test_metro0001_calibration.py) / [run目録](../experiments/METRO-0001/runs/README.md)。**本体は人工fixture-only**、領域転移やEXP-0003A FINALの独立評価器ではない。

## METRO-0001 CAL-01 実測記録（工学校正のみ）
[CAL-01 CI run record](../experiments/METRO-0001/runs/20261027-cal01-synthetic.md) — synthetic F01–F08 / status engineering_fixture_pass / no intelligence-growth claim。Source PR2独立レビューと採用は別ゲート。

## METRO-0001 CAL-01 Artifact独立再照合
[CAL-01 provenance-verified run](../experiments/METRO-0001/runs/20261027-cal01-provenance-verified.md) — 86 tests PASS / full synthetic fixture manifest and ZIP byte hashes / PR #41 before merge; no intelligence gain claimed.

## METRO-0001 decision — 2026-10-27
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| METRO-CAL01-DECISION | 合成校正の独立レビュー・工学採用・限定事項 | accepted_engineering_calibration | [decision](../experiments/METRO-0001/reviews/20261027-cal01-adoption.md) |
| METRO-CAL01-PROVENANCE | artifact元bytes/fixture hash・工学実測run | recorded | [run](../experiments/METRO-0001/runs/20261027-cal01-provenance-verified.md) |

科学的能力・学習改善・領域間転移は未実証。METRO-0001自体を汎用知能測定器と解釈しない。


## EXP-0003A PR5 — Independent DEV evaluation (not yet executed)
| ID | Theme | Status | Document |
|---|---|---|---|
| EXP-0003A-DEV-EVAL-PR5 | frozen source/policy -> independent B0/B1/B2/B3 DEV64 evaluator | implementation PR; DEV/FINAL not run | [spec](specs/EXP-0003A-DEV-EVALUATOR.md) / [code](../packages/exp0003a_dev/__init__.py) / [engineering plan](../experiments/EXP-0003A/dev-evaluation-pr5.md) / [runs](../experiments/EXP-0003A/runs/README.md) / [Issue #44](https://github.com/ryonakayama234/DekaSugi/issues/44) |

## EXP-0003A DEV64 reviewed one-shot gate (Issue #46)
- [Activation contract](specs/EXP-0003A-DEV64-ACTIVATION.md) — independently
  reviewed main-only, first-attempt-only scoring after PR integration.
- [DEV evaluator](specs/EXP-0003A-DEV-EVALUATOR.md) /
  [execution record](../experiments/EXP-0003A/dev-evaluation-pr5.md) /
  [run index](../experiments/EXP-0003A/runs/README.md).
- Independent artifact verifier:
  `scripts/audit_exp0003a_dev_evidence.py` (read-only, stdlib; no DEV in PR).
  The activation workflow is an execution boundary, not FINAL authorization.

## EXP-0003A DEV64 audit-only recovery and original-evidence chain (Issue #48)
- [Run ledger](../experiments/EXP-0003A/runs/20261027-dev64.md) records
  original one-shot status, raw public/private SHA256, measured arm totals,
  audit-only fix, CI provenance and data-retention limits.
- Read-only `scripts/audit_exp0003a_dev_evidence.py` permits bounded binary64
  CPU/wall rounding only, with integer/verdict/source-hash checks exact.
- Separate `.github/workflows/exp0003a-dev64-audit-original.yml` downloads
  immutable original Artifact by fixed run/ID; it cannot score DEV or FINAL.
  Original workflow failure is never overwritten.


## POLICY-DIAG-001 — 診断計画（design-only, not_run）
- [仕様書](specs/POLICY-DIAG-001.md) / [事前分析計画](../experiments/POLICY-DIAG-001/plan.md) / [run目録](../experiments/POLICY-DIAG-001/runs/README.md)
- [Issue #52](https://github.com/ryonakayama234/DekaSugi/issues/52) — EXP-0003A B2/B3の凍結方策・保存済みDEV64公開証拠の読み取り専用メカニズム診断。
- 主要実装観測対象：`packages/exp0003a/pr3.py` `ArmSnapshot`/`choose`。提案モジュール：`packages/policy_diagnostics`（**未実装**）。
- 実装着手前に測定対象・仮説P-H1〜P-H5・データ出典・欠測規則・合否条件を固定する。既存EXP-0003A v1/FINAL128は不変更。

## POLICY-DIAG-001 — implementation (independent read-only module)
- [diagnostic code](../packages/policy_diagnostics/__init__.py) / [synthetic + TRAIN-only tests](../tests/test_policy_diagnostics.py) / [diagnostic run index](../experiments/POLICY-DIAG-001/runs/README.md). The code does not evaluate DEV/FINAL; actual DEV per-task results remain not_observed unless authorized archived public evidence is supplied.


## POLICY-DIAG-001 original-public evidence analysis (complete within archived-public scope)
- [Descriptive diagnosis run](../experiments/POLICY-DIAG-001/runs/20261028-archive-public-diagnosis.md) / [aggregate JSON](../experiments/POLICY-DIAG-001/runs/20261028-archive-public-diagnosis.json) / [hash-gated script](../scripts/analyze_policy_diag_archives.py) / [archive validation tests](../tests/test_policy_diag_archives.py).
- Results: Dream overlap 24/96; 5NN overlap mean 2.890625/5; different neighbors 61/64 yet different vote/saving only 1/64; different action 1/64 but observed primitive costs identical 64/64. This is an exploratory **partial** explanation, not fresh holdout inference or H3 confirmation. DEV public TaskSpecs absent: distances/close_support not_observed; FINAL128 sealed.

## OPPORTUNITY-001 — 能力上限・学習機会の実装前設計（2026-10-28）
| ID | テーマ | 現在状態 | 研究正本 |
|---|---|---|---|
| OPPORTUNITY-001 | 固定技能ON/OFFの正答・費用機会、Kernelの取り逃がし、表現/探索制約の識別 | proposed_design_only; not_run; numerical preregistration not frozen | [spec](specs/OPPORTUNITY-001.md) / [plan proposal](../experiments/OPPORTUNITY-001/plan.md) / [run ledger](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #56](https://github.com/ryonakayama234/DekaSugi/issues/56) |

- 主対象モジュールは`evaluation`、将来の専用モジュール `packages/evaluation/opportunity.py` は**未実装**。参照元は `kernel`/`learning`、メトリクスと欠測契約は既存METRO-0001を踏襲する。
- [ARCH-001](architecture/system.md)に全体処理図、[ARCH-002](architecture/contracts.md)に二択paired evidenceとlearner/evaluator信頼境界。旧POLICY-DIAG-001のDEV事後診断は新しい確証データではない。
- 本計画はreview待ちの設計案。split・seed・検定・進路選択の数値閾値の固定は後続の独立レビュー済みcommitで行う。未実行のため実測結果なし。

## OPPORTUNITY-001 PR2 — synthetic-only test instrument
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-001-PR2 | 固定二択の人工fixture分類、欠測/偽解/費用regret校正 | implemented_synthetic_only; scientific not_run | [module](../packages/evaluation/opportunity.py) / [tests](../tests/test_opportunity_fixture.py) / [spec](specs/OPPORTUNITY-001.md) / [run ledger](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #58](https://github.com/ryonakayama234/DekaSugi/issues/58) |

実データを実際に採点・認証するadapterは未実装（PR8の純粋normalizerは未起動）。旧EXP-0003A DEV64/FINAL128には触れず、METRO CAL-01のfixture認証も拡大解釈しない。

## OPPORTUNITY-001 PR3 — fresh TRAIN pilot method fixed (no execution)
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-001-PILOT-V1 | 新規TRAIN64、seed/変換規則/公開2例+非公開audit/固定技能/3つの既存Kernelの評価前方法固定 | method_spec_frozen; source/manifest freeze pending; not_run | [pilot method](../experiments/OPPORTUNITY-001/pilot-v1.md) / [run ledger](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #60](https://github.com/ryonakayama234/DekaSugi/issues/60) |

Method-only PR3: 旧DEV/FINALを使用せず、新しい課題の実測も未実行。今後のsource-firstハッシュ凍結と実データadapterは別PR。

## OPPORTUNITY-001 PR4 — fresh TRAIN64 public manifest generator
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-PILOT-GEN | 事前登録済み新規TRAIN64のsourceを実装し、公開2例とハッシュのみ出力（第三auditは非公開） | generator implemented; **not scored**; source/manifest lock pending | [module](../packages/evaluation/opportunity_pilot.py) / [tests](../tests/test_opportunity_pilot.py) / [method](../experiments/OPPORTUNITY-001/pilot-v1.md) / [runs](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #60](https://github.com/ryonakayama234/DekaSugi/issues/60) |

CLI: `python -m packages.evaluation.opportunity_pilot --mode hash-only` — public manifest SHA only, no paid trials/old DEV/FINAL. Actual adapter and before-trial chronological source lock remain future gates.

## OPPORTUNITY-001 PR5 — independently recomputed TRAIN64 identity
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-PILOT-AUDIT | project generatorをimportしないstdlib独立実装で公開SHA再計算、第三auditはSHAコミットのみ | source-only verification proposed/in review; no trial | [script](../scripts/audit_opportunity_pilot_public.py) / [tests](../tests/test_opportunity_pilot_independent.py) / [method](../experiments/OPPORTUNITY-001/pilot-v1.md) / [runs](../experiments/OPPORTUNITY-001/runs/README.md) |

Expected source hash `bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85`; original raw evidence preservation is NOT established by this hash-only auditor.

## OPPORTUNITY-001 PR6 — 実装前ソース・課題・固定方策凍結
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-001-PILOT-SOURCELOCK-V1 | source Blob SHA ×9、公開64件と第三監査SHA、既存技能/B1/B2/B3 snapshot SHA、Python版の照合 | source-only frozen; scoring **not authorized**; not_run | [lock](../experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json) / [verifier](../scripts/verify_opportunity_generator_lock.py) / [tests](../tests/test_opportunity_generator_lock.py) / [method](../experiments/OPPORTUNITY-001/pilot-v1.md) / [runs](../experiments/OPPORTUNITY-001/runs/README.md) |

実研究アダプタ・policy before-trial timestamp・結果原本保全は別途。旧DEV/FINAL未使用。

## OPPORTUNITY-001 PR7 — 採点前のB1/B2/B3方策判断
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-001-PRETRIAL-V1 | 新規TRAIN64 × 固定B1/B2/B3の事前選択を公開TaskSpecのみから計算し、GitHub CIに独立成果物を保存 | engineering pretrial only; paired `not_run` | [module](../scripts/prepare_opportunity_decisions.py) / [tests](../tests/test_opportunity_pretrial.py) / [workflow](../.github/workflows/opportunity-pretrial.yml) / [lock](../experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json) |

実測の前に別の不変commitで公開decision payload SHAを封印する。第三監査・探索結果は本成果物に入れない。

### PR7 no-old-holdout-generation P1 remedial source
The initial PR7 pretrial code unintentionally invoked historical `verify_frozen` which regenerates old DEV/FINAL (not scoring). Its initial SHA is **diagnostic only**. The corrected [stdlib 14-source verifier](../scripts/verify_opportunity_legacy_sources.py) runs before project import, then direct old TRAIN/DREAM-only policy restoration; [regression tests](../tests/test_opportunity_pretrial.py) mock old withheld generators to fail if called.

## OPPORTUNITY-001 PR9 — 採点前事前判断の長期保全・品質試験設計（2026-10-28）
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-001-CHOICE-CUSTODY-DESIGN-V1 | 原本bytes/論理payload/生成経路/保持と時系列を分けるEvidence Capsule設計 | proposed_design_only; no_scoring | [設計契約](specs/OPPORTUNITY-001-CHOICE-LOCK-DESIGN.md) / [ARCH-001](architecture/system.md) / [ARCH-002](architecture/contracts.md) / [Issue #68](https://github.com/ryonakayama234/DekaSugi/issues/68) |
| OPPORTUNITY-001-CHOICE-CUSTODY-PREREG-V1 | C01–C09品質観測、N01–N12人工改変検査、失敗停止規則 | planned; not_run | [品質試験計画](../experiments/OPPORTUNITY-001/choice-custody-preregistration.md) / [run ledger](../experiments/OPPORTUNITY-001/runs/README.md) |

- **主対象モジュール**: `evaluation / provenance`。実装は後続のPR9、今回追加したものは設計文書のみ。保存予定の公開decision JSONとchoice-lock JSONは**現時点では作成・検証していない**。
- 正式事前判断元はPR #65統合済みmain `c6b01c2`、Actions run `40659741488`、artifact `12803053107`。公式sourceの採点前判断原本はGitHub Actionsに存在しても90日保管であり、元member raw SHAも未採取。計画された保存copyとprivate原本保全を既存のものとして記載しない。
- PR #67は別の実証データ正規化器でレビュー中。古いINDEX記述（実アダプタ未実装など）は各工程の記録として扱い、現在の設計検討はこの行から辿る。新TRAIN64 paired scoring 0件、旧FINAL128は封印を維持。

## OPPORTUNITY-001 PR9 — public Evidence Capsuleの取得・照合・Git保全
| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| OPPORTUNITY-001-CHOICE-LOCK-V1 | 公式Actions事前判断**公開原本**のbyte SHA、source/policy、64×3選択、保存済みGitコピー | original_public_bytes_verified_engineering; independent merge review pending; no paired scores | [original copy](../experiments/OPPORTUNITY-001/evidence/pilot-choices-public-v1.json) / [provenance lock](../experiments/OPPORTUNITY-001/pilot-choice-lock-v1.json) / [stdlib verifier](../scripts/verify_opportunity_choice_lock.py) / [negative tests](../tests/test_opportunity_choice_lock.py) |
| OPPORTUNITY-001-PR9-CUSTODY-RUN | 2026-10-28公式run 40659741488原本からの安全な保管runと限界 | engineering observed / research outcome not_run | [observed run](../experiments/OPPORTUNITY-001/runs/20261028-pr9-public-choice-custody.md) / [run index](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #68](https://github.com/ryonakayama234/DekaSugi/issues/68) |

- 主対象`evaluation / provenance`（`scripts/verify_opportunity_choice_lock.py`）。公開原本27360 bytesのSHA `1d08e6…`とcanonical JSON decision digest `8a8625…`を**別に検証済み**。比較元はmain `c6b01c2`・公式Actions run `40659741488` / job `122719482732` / artifact `12803053107`。取得・検証run [#40668908541](https://github.com/ryonakayama234/DekaSugi/actions/runs/40668908541)成功。
- 同じ原本を元のArtifact以外の公開Gitへ保全したが、GitHub外の改変不能バックアップを保証するものではない。既存PR7の初期禁止経路runは同じdigestでも権威ある原本ではない。
- 古い「source lock pending」「実adapter未実装」などの行は当時の履歴記述であり、今回のpublic provenance保全を採点器の実装や研究効果へ読み替えない。PR #67の実paired正規化器は別レビュー。新TRAIN64 ON/OFFは0、private raw custody・実scorer・one-shot activationは#66未達。

## OPPORTUNITY-001 PR8 — non-activated canonical tuple normalizer
- [Adapter contract](specs/OPPORTUNITY-001-REAL-ADAPTER.md) / [pure module](../packages/evaluation/opportunity_actual.py) / [synthetic adversarial tests](../tests/test_opportunity_actual.py) / [run ledger](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).
- PR8 is a **review-gated draft** for *normalizing* canonical nine-field audited tuples, not a trusted live scorer/real-evidence provenance verifier. It strictly checks search status/program, SHA trace, canonical meter, same task/budget and redaction.
- Scientific status: new TRAIN/DEV/FINAL scores = **0, not_run**. PR7 public pretrial choice seal is now retained by PR #70; verifiable private-original custody, separate activation/independent recount are outstanding. Earlier PR1–PR6 descriptions are historical milestones and do not override this gate.

## EXP-0003A DEV64 — uploaded local ZIP verified without private publication (2026-10-28)
- [Local exact-byte verification and custody limitation](../experiments/EXP-0003A/runs/20261028-local-zip-integrity.md): the user-supplied outer ZIP (65,315 bytes) and both nested original/audit artifact ZIPs match historical SHA-256 records; inner SHA256SUMS 4/4 + 2/2 PASS. This is a **read-only original-byte integrity attestation**, not new scoring, an independently durable second backup, or a valid OPPORTUNITY-001 TRAIN64 privacy archive.
- Original confidential ZIP stays **off public GitHub**; only hashes and nonprivate statuses are indexed. [Architecture](architecture/system.md) / [data flow](architecture/contracts.md) / [DEV ledger](../experiments/EXP-0003A/runs/20261027-dev64.md) / [Issue #48](https://github.com/ryonakayama234/DekaSugi/issues/48).


## OPPORTUNITY-001 — actual canonical OFF/ON pair engine, still blocked
- [Real pair engine contract](specs/OPPORTUNITY-001-REAL-PAIR-ENGINE.md) / [unactivated engine](../scripts/opportunity_real_pair_engine.py) / [synthetic-only tests](../tests/test_opportunity_real_pair_engine.py) / [Issue #76](https://github.com/ryonakayama234/DekaSugi/issues/76).
- The OFF/ON *execution wiring* is newly implemented for later separate activation; `SCORING_ACTIVATED=false` and **fresh TRAIN64 actual scored pairs=0**. Private original capture and external secure versioned archive/restore remain unverified; the owner-only off-Git Google Drive folder is an empty destination, not proof of custody.


## OPPORTUNITY-001 — private TRAIN64 archive preparation, NOT scored
- [Private-origin custody readiness specification](specs/OPPORTUNITY-001-PRIVATE-CUSTODY.md) / [read-only local two-copy SHA checker](../scripts/verify_opportunity_private_copy.py) / [synthetic adversarial tests](../tests/test_opportunity_private_copy.py) / [Issue #72](https://github.com/ryonakayama234/DekaSugi/issues/72).
- 64 public TaskSpecs and 192 original public policy decisions are retained, but fresh ON/OFF scored rows = **0**; the historical DEV64 local ZIP is unrelated. The checker can verify byte equality only, **not** private access controls, archival version/retention, actual scorer provenance or scientific results. [run status](../experiments/OPPORTUNITY-001/runs/README.md) / [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).


## OPPORTUNITY-001 — new TRAIN64 source-first audit-original capture engineering (no score)
- [Private capture and boundary contract](specs/OPPORTUNITY-001-PRIVATE-CAPTURE.md) / [manual off-repository CLI](../scripts/capture_opportunity_private_original.py) / [synthetic negative tests](../tests/test_opportunity_private_original_capture.py) / [Issue #74](https://github.com/ryonakayama234/DekaSugi/issues/74).
- Implementation under PR review; genuine third-audit original capture **0**; OFF/ON scored pairs **0**. Source-first old14+new9 frozen bytes, official 27,360-byte 192-choice raw original, and frozen third audit SHA gate are mandatory. Two owner-private local raw files with SHA readback are not by themselves independently durable restricted custody. [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66) remains blocked.

- [WSL2 operator runbook: one-time private capture, local GPG encryption and encrypted Google Drive upload/restore](specs/OPPORTUNITY-001-PRIVATE-OPERATOR.md) (draft; do not execute before PR #75 review and merge; no scoring). 

- [OPPORTUNITY-001 one-shot OFF/ON private-host scoring runner (currently hard-off, synthetic tests only)](specs/OPPORTUNITY-001-ONE-SHOT-RUNNER.md): source-first original validation, fixed frozen skill/policies, irreversible local ledger, separate activation gate.

- [OPPORTUNITY-001 distinct one-shot owner-only main activation specification (real scoring prohibited in CI)](specs/OPPORTUNITY-001-ACTIVATION.md): clean approved origin/main, scoped dual switches, irreversible private ledger, external custody and independent review.

- [OPPORTUNITY-001 owner-private read-only original/skill/choice preflight — no new scored trial and no irreversible STARTED](specs/OPPORTUNITY-001-LIVE-READONLY-PREFLIGHT.md).


- [OPPORTUNITY-001 — 2026-10-29 actual new TRAIN64 64-pair OFF/ON result, independent private read-only recount and frozen **UNDERIDENTIFIED** branch](../experiments/OPPORTUNITY-001/runs/20261029-train64-real-paired-recount.md). **Latest research status**: scored 64/64 once, OFF=ON=48/64 correct, B1/B2/B3 errors 0/16 eligible, no rescoring. Preceding `not_run` entries are historical pretrial records, not present status. Report publication PR #85 is kept off main pending inherited main-push old DEV workflow/sourcelock remediation; the result is also logged under Issue #82.

## CI-SAFE-V2 — unsafe historical main-push DEV smoke migration (Issue #88; staged)
- The previous original `.github/workflows/docs-check.yml` is immutable PILOT-V1 research source and **not changed**. [Successor specification](specs/CI-SAFE-V2.md) / [versioned new workflow](../.github/workflows/research-verification-v2.yml) / [byte and command allowlist checker](../scripts/check_research_ci_v2.py) / [synthetic test runner](../scripts/run_research_ci_v2_tests.py) / [negative tests](../tests/test_research_ci_v2.py).
- [ADR-0004](architecture/decisions/ADR-0004-ci-safe-successor.md) / [migration evidence ledger](process/ci-safe-v2-ledger.md) / [Issue #88](https://github.com/ryonakayama234/DekaSugi/issues/88). CI narrows old broad evaluation to documentation, source-only integrity and synthetic cases. **No owner workflow disablement or main integration yet**; PR CI cannot verify GitHub control-plane state. Old DEV/FINAL reruns and original TRAIN64 repeat forbidden.

## Latest research decision — OPPORTUNITY-002 capability boundary & identifiability (2026-10-29)
- **Latest state:** OPPORTUNITY-001 PILOT-V1 64 genuine paired rows were completed and independently read-only recounted; report [PR #85](https://github.com/ryonakayama234/DekaSugi/pull/85) is **merged**. The previous bottom-of-index statement describing PR #85 as pending is an earlier chronological checkpoint, not current state.
- **OPPORTUNITY-002 PR1 design-only** ([Issue #86](https://github.com/ryonakayama234/DekaSugi/issues/86)): [research specification](specs/OPPORTUNITY-002.md), [independent review checklist](specs/OPPORTUNITY-002-REVIEW-CHECKLIST.md), [method / experimental plan](../experiments/OPPORTUNITY-002/plan.md), [run index](../experiments/OPPORTUNITY-002/runs/README.md), [architecture decision](architecture/decisions/ADR-0003-opportunity002-identifiability.md), [system/flow](architecture/system.md), [contracts](architecture/contracts.md).
- Status: proposed; no OPPORTUNITY-002 implementation, synthetic execution, new paired scoring, source freeze or new scientific result; independent PR exact-head review and CI **pending**. The source inspection predicts OFF=40 / ON=47 4-expanded-node candidates, independently unverified.
- Main merge blocked until inherited main-push historical DEV smoke/source-lock conflict is safely resolved under a separate review; old score/original and EXP-0003A DEV64/FINAL128 stay sealed. Historical `not_run` statements in prior entries are not current OPPORTUNITY-001 outcome assertions.

## OPPORTUNITY-002 / PR2 — synthetic-only boundary checker
- [独立実装](../scripts/opportunity2_boundary.py)、[人工テスト](../tests/test_opportunity2_boundary.py)、[run台帳](../experiments/OPPORTUNITY-002/runs/README.md)。3つの原始操作と仮想の二操作マクロでOFF40/ON47構文、表現集合同値、候補予算5の人工例をチェックする。**学習・正式技能・本番スコア・元SkillCandidateのhash認証ではない**。
- 元の[PR1仕様](specs/OPPORTUNITY-002.md)・[独立レビューリスト](specs/OPPORTUNITY-002-REVIEW-CHECKLIST.md)を継承。研究者レビュー・source lock・本番実験の事前登録は別ゲート。main統合安全阻害要因は[Issue #88](https://github.com/ryonakayama234/DekaSugi/issues/88)。
