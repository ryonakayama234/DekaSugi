# DekaSugi

**小さな中枢が、外部の知識・技能・道具を再利用し、自ら新しい操作体系を獲得できるかを検証する研究プロジェクト。**

- 事前学習済みの巨大LLMは初期実験で使わない。
- 失敗した仮説も記録し、未検証の構想と実証済みの成果を区別する。
- Python / Linux (WSL2) / ローカルCPUから始める。
- プロジェクト名は **DekaSugi**。旧構想の仮称「ATELIER」は文献・議論上の呼称であり、リポジトリ名ではない。

## Entry points

| 読者 | 最初に読むもの |
|---|---|
| 初めて参加する人 | [研究目的](docs/vision/mission.md) → [全体構造](docs/architecture/system.md) |
| 実装するAIエージェント | [AGENTS.md](AGENTS.md) → [資料索引](docs/INDEX.md) |
| 実験を再現する人 | [初回実験](experiments/EXP-0001/plan.md) → [実験プロセス](docs/process/workflow.md) |
| 進捗を確認する人 | [ロードマップ](docs/roadmap.md) とGitHub Issues / Pull Requests |

## 現在の状態 (2026-10-25)

**EXP-0002B はFINAL112の一回限りの評価まで完了しました。** [正式実測](experiments/EXP-0002B/runs/20261025-final112.md)で4条件ではなく既定3arm (OFF/ON/LEARNED) を比較し、監査正解はすべて80/112、LEARNEDは候補1520・原始演算6880（OFF1536/6944、ON1744/8160）。事前登録の5数値基準はPASS、ただし**正式技能昇格なし・総CPU利益は未実証**。FINAL起動ステップは削除済み。[統合後CI](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176764493)。

**EXP-0003A は新規の設計・事前登録段階です（未実装・未実行）。** [新計画](experiments/EXP-0003A/plan.md) / [仕様](docs/specs/EXP-0003A.md) / [アーキテクチャ](docs/architecture/system.md) / [データ契約](docs/architecture/contracts.md) / [研究コンソールのUI責務](docs/architecture/ui-panels.md) / [run目録](experiments/EXP-0003A/runs/README.md)。WAKE・SLEEP・DREAMの未知課題評価はまだありません。

**既存の成果**: EXP-0001は非学習baselineとして技術的PASS、EXP-0002は技能候補発見を実装済み（候補の一般的正式採用なし）。SEC-004の実行信頼境界とMEASURE-0001のcanonical primitive meterは継承。

## EXP-0002B の過去の開発コマンド・工程（当時の位置づけ）

ローカル資料検査: `python scripts/check_docs.py`（標準ライブラリのみ）。

## 原則

**課題 → 仮説 → 設計 → 実装 → 実験 → 第三者視点の検証 → 採否決定 → 文書更新**。
コードとともに図・データ契約・実験記録を更新する。詳細は [開発ルール](docs/process/workflow.md)。

## EXP-0001: 動くベースライン

前提: Python 3.12+ / Linux または WSL2。追加のPython依存は不要。

```bash
python -m unittest discover -s tests -v
python scripts/check_docs.py
python -m packages.cli --task experiments/EXP-0001/tasks/composition.json
python -m packages.cli --suite --output /tmp/exp0001.json
```

- 事前登録の7ケースは `--suite` で検証する。
- 出力は探索状態・候補数・解法AST・探索順ハッシュ・実行時間を含む。
- 実行結果の採否は [実験run記録](experiments/EXP-0001/runs/README.md) で管理。
- **EXP-0001は自動学習ではない。** 学習による改善の検証は後続の実験。

## EXP-0002: 共通部分式から技能候補を作る

独立した訓練エピソードの解法ASTから共通部分式を抽出し、許可済みDSLだけで新しい技能候補を実行する。学習条件と固定baselineを同じ候補数・**展開後の原始ASTノード数**で比較する。

```bash
python -m packages.evaluation --output .run/EXP-0002-result.json
```

機能/効率の実測と、技能を標準ライブラリへ正式採用する判断は別段階。[設計図](docs/architecture/system.md) / [仕様](docs/specs/EXP-0002.md)。

## EXP-0002B：訓練専用Kernel（研究段階）

```bash
python -m packages.kernel --mode preflight --output .run/EXP-0002B-preflight.json
python -m packages.kernel --mode train --output .run/EXP-0002B-train-only.json
```

このコマンドが出力する内容は**TRAINのみ**。データセットhashは計算するが、FINALの探索・評価は実行しない。参照：[事前登録v2](experiments/EXP-0002B/plan-v2.md) / [実装監査](experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## EXP-0002B — 評価前に固定した学習方策

TRAIN144問での学習と復元可能なKNN方策がCIで一致。**[DatasetとPolicySnapshotの凍結記録](experiments/EXP-0002B/freeze-v2.md)**を先に保存してから、DEVとFINALの別工程で独立評価する。TRAIN証拠は凍結済み。DEV48の工学的診断結果および後続FINAL112の正式結果は別runとして保存した。

## EXP-0002B — DEVとFINALの独立ゲート

学習済みKernelの改変を検出する評価器を[監査手順](experiments/EXP-0002B/reviews/20261025-evaluator-gate.md)として追加。コードPR内では訓練fixturesのみをテストし、レビュー済みmainでDEV48 smokeを実施し、その証拠を保存した。FINALは独立レビュー後に専用トリガーから実行済みであり、トリガーは削除済み。

## METRO-0001 と現行研究の関係 (2026-10-27)
この節を最も新しい工程注記とする。上記2026-10-25のEXP-0003A「未実装」は当時の履歴であり現在状態ではない。WAKE/SLEEPのTRAIN160、DREAM512・選別B2/B3各96、方策snapshotは実装・工学的実行済み。pre-DEV source/split/policy凍結は[PR #37](https://github.com/ryonakayama234/DekaSugi/pull/37)でmain統合済み。**EXP-0003A DEV64/FINAL128の評価結果は未確認であり、技能昇格や総CPU利益を意味しない。**
[METRO-0001](experiments/METRO-0001/plan.md)は知能測定の設計とCAL-01校正を扱う新研究で、現行の凍結済みplan-v1/freeze-v1を変更しない。初期phaseはdocs-onlyの提案で、校正用計測器・能力実測の新結果は未実装。[ontology](docs/metrology/ontology.md) / [metrics](docs/metrology/metrics.md) / [evidence](docs/metrology/evidence-model.md) / [validity](docs/metrology/validity.md)。

## METRO-0001 CAL-01 engineering (PR2)
[Issue #40](https://github.com/ryonakayama234/DekaSugi/issues/40) は凍結済み[校正計画](experiments/METRO-0001/plan.md)をstd-libのread-only測定器とsynthetic fixtureで検査する独立作業。プログラム合成の性能向上、未使用holdoutの評価、一般知能の検証とは独立。[run目録](experiments/METRO-0001/runs/README.md)を参照。

## METRO-0001 initial calibration completion (2026-10-27)
- 設計・事前登録 [PR #39](https://github.com/ryonakayama234/DekaSugi/pull/39) と合成fixture測定器 [PR #41](https://github.com/ryonakayama234/DekaSugi/pull/41) はmain統合済み。merge後 [CI #40460951680](https://github.com/ryonakayama234/DekaSugi/actions/runs/40460951680)成功。
- [CAL-01工学採用判断](experiments/METRO-0001/reviews/20261027-cal01-adoption.md): M1–M4を人工F01–F08で校正PASS、86 testsとArtifact hash独立照合。**METRO-0001の限定された工学目標は完了**。実験評価器やAI知能の向上が証明されたわけではない。
- 今後の実際のTRAIN証拠への接続、未知課題への転移の検証、EXP-0003AのDEV/FINALは別研究・別ゲートで扱う。上記の以前の「未実装」「レビュー中」は各時点の歴史的記録。


## EXP-0003A PR5 — Independent DEV evaluation (2026-10-27)
[Issue #44](https://github.com/ryonakayama234/DekaSugi/issues/44)
starts the source-first, frozen-policy independent four-arm DEV64
engineering evaluator in `packages/exp0003a_dev`. **Implementation-stage
proposal: DEV64/FINAL128 are not scored, no new performance result exists.**
No frozen learner code or manifest may be changed; DEV requires a separately
reviewed main-only gate, and FINAL128 needs a separate explicit approval.
[Specification](docs/specs/EXP-0003A-DEV-EVALUATOR.md).

## 次期研究候補 — OPPORTUNITY-001（2026-10-28、設計のみ）

[POLICY-DIAG-001の事後分析](experiments/POLICY-DIAG-001/runs/20261028-archive-public-diagnosis.md)を受けて、技能ON/OFFに実際の改善機会が存在するか、Kernelがそれを取り逃がすか、表現力/探索予算の制約に起因するかを区別する[OPPORTUNITY-001の研究設計案](docs/specs/OPPORTUNITY-001.md)を追加。現時点で新実験や新知能能力の測定は**未実行**。 [事前登録案](experiments/OPPORTUNITY-001/plan.md)は独立レビュー・数値閾値凍結前であり、実装・DEV/FINAL評価の許可ではない。既存EXP-0003A FINAL128は封印のまま。

## 最新研究方針 — OPPORTUNITY-002（2026-10-29、PR1設計案）
上記の2026-10-25/27/28節は当時の履歴です。最新の公開研究事実は[OPPORTUNITY-001の真のTRAIN64ペア監査レポート](experiments/OPPORTUNITY-001/runs/20261029-train64-real-paired-recount.md)（[PR #85 merged](https://github.com/ryonakayama234/DekaSugi/pull/85)）です。64ペアで両arm正解48、片側のみ正解0、費用のみの一意差16、両失敗16。前登録判定は **UNDERIDENTIFIED** です。

次の[Issue #86](https://github.com/ryonakayama234/DekaSugi/issues/86)は能力境界・識別可能性を研究する[PR1設計案](docs/specs/OPPORTUNITY-002.md)と[新実験計画案](experiments/OPPORTUNITY-002/plan.md)です。原始演算による表現可能性、予算内探索、選択/観測情報、学習・転移を区別します。**新しい採点・能力改善結果はありません。** 既存original 64/DEV64/FINAL128は不変・再採点禁止。main統合には既存main-push DEV smokeと凍結source lockの安全な整合が必要です。

## ACTIVE-001 — 新規研究の事前登録案 (2026-10-30)
現行mainで最後に統合された研究はOPPORTUNITY-002の**人工fixtureによる監査技術**であり、能力の伸長は未実証です。次の独立課題[ACTIVE-001 #93](https://github.com/ryonakayama234/DekaSugi/issues/93)は、公開例から残る仮説を使い、自ら何を質問するかを選ぶ **同一課題内の能動的適応** を計測する[提案仕様](docs/specs/ACTIVE-001.md)と[未凍結研究計画](experiments/ACTIVE-001/plan.md)です。既存の3演算互換検査と新規隔離8演算人工環境を区別し、B0/B1/B2で独立した未知入力を比較します。質問方策の学習（Stage II）や領域転移（Stage III）は未実装・未実証。旧実験原本は不変更、PR1は文書のみで、科学的スコアの新規取得は未承認です。

## ACTIVE-001 PR2 — synthetic-only progress (stacked, 2026-10-30)
The [isolated finite grammar](packages/inquiry_world/__init__.py) and [active query engine](packages/active_learning/__init__.py) have a [five-test local synthetic calibration receipt](experiments/ACTIVE-001/runs/20261030-pr2-local-synthetic.md): 878 meaningfully different finite-domain programs among 4,681 syntactic candidates. The independent evaluator is NOT implemented, the H1 scored study has not been run, and source/CI review and historic main-push safety verification still block merge.

## ACTIVE-001 PR2 review-driven synthetic hardening (2026-10-30)
[PR #95](https://github.com/ryonakayama234/DekaSugi/pull/95) addresses query-state, input partition and policy replay integrity with new negative fixture tests. [System diagram](docs/architecture/system.md) / [Data contract](docs/architecture/contracts.md) / [run receipt](experiments/ACTIVE-001/runs/20261030-pr2-integrity-repair.md). This is engineering-only; there is no scored ACTIVE-001 trial, learned policy or demonstrated transfer. Safe main integration still requires a fresh independent review and verified historical workflow disablement.

## ACTIVE-001 PR2 — question-history and input-boundary hardening (2026-10-30)
[Draft PR #95](https://github.com/ryonakayama234/DekaSugi/pull/95) stages active-query/2: verify the full canonical public/query/evaluator split and revalidate each question-choice/answer prefix. [System flow](docs/architecture/system.md) / [Data contract](docs/architecture/contracts.md) / [Engineering receipt](experiments/ACTIVE-001/runs/20261030-pr2-history-boundary-integration.md). This does not authorize a real scored study, assert acquired skill or imply independent Oracle trust.

## ACTIVE-001 PR2 — fixed-world Catalog integrity (2026-10-30)
The [draft PR #95](https://github.com/ryonakayama234/DekaSugi/pull/95) adds cached canonical Catalog checks so reconstructed local class signatures and by_id lookups cannot forge the supposed absence of informative queries. [Architecture](docs/architecture/system.md) / [contracts](docs/architecture/contracts.md) / [engineering receipt](experiments/ACTIVE-001/runs/20261030-pr2-catalog-integrity.md). Synthetic tests and CI do not certify source-authenticated scientific improvement, independent Oracle custody or generalization.

## ACTIVE-001 PR2 — canonical lookup execution boundary (2026-10-30)
Review-driven [PR #95](https://github.com/ryonakayama234/DekaSugi/pull/95) uses a cached **internal** canonical Catalog for all predictions and program lookup, not a caller-supplied `MappingProxyType` which can hide overridden mapping reads. Synthetic adversarial regression, [ARCH-001](docs/architecture/system.md), [ARCH-002](docs/architecture/contracts.md), and [engineering receipt](experiments/ACTIVE-001/runs/20261030-pr2-lookup-canonicalization.md) are synchronized. No real scored tasks, new learned policy or independently authenticated evaluator are claimed.

## ACTIVE-001 PR2 — exact-state types and replay (2026-10-30)
[Draft PR #95](https://github.com/ryonakayama234/DekaSugi/pull/95) now checks that externally reconstructed semantic-class ID tuples and proposal/answer fields contain exact Python primitive types, preventing equality-preserving subclass operations from changing question scores. [System map](docs/architecture/system.md), [data contract](docs/architecture/contracts.md), [synthetic run](experiments/ACTIVE-001/runs/20261030-pr2-container-types.md). No historical scoring, independent source custody or measured intelligence gain is claimed.

## ACTIVE-001 #96 — refined scientific design v2 (2026-10-30; review draft)
[Decision text v2](experiments/ACTIVE-001/method-v2-decision-draft.md) / [ADR-0006](docs/architecture/decisions/ADR-0006-active001-scientific-design.md) / [PR #97](https://github.com/ryonakayama234/DekaSugi/pull/97).
A future **read-only structural Gate F** precedes a separately authorized, source-locked proposed **N4096** paired evaluation of independent with-replacement uniform semantic-class/public-pair task draws. N, seed, evaluator and source identity remain **NOT_FROZEN**, zero new scored ACTIVE-001 trials, no claim of Stage II learning or transfer.

## ACTIVE-001 P3 — 統計的検出力の非採点チェック（2026-10-31）
一次仮説B2−B1の**課題単位**差分に対し、Student-t 95% CIと有界IID Hoeffdingの保守的CIを人工差分だけで検査する [P3数値検証器](packages/active_statistics/__init__.py) を追加。4,096課題で真の+5ppのときの最悪分散の**正規近似**約89%検出力は保証ではなく、Hoeffdingによる保守的な80%十分条件は約8,138課題。どちらの標本数も研究採点用として凍結していない。実際の正答率を測らず旧データを再実行しない。[方法](experiments/ACTIVE-001/p3-inference-numerical-draft.md) / [記録](experiments/ACTIVE-001/runs/20261031-p3-invented-stat.md)。

## ACTIVE-001 E0 — 独立評価のためのデータ入口の検査（2026-10-31）
AI側に渡せるJSON項目を公開観測・合法な質問候補・その質問への1回答だけに制限する [E0インターフェース](packages/active_custody_boundary/__init__.py) を追加。正解ID、秘密Seed、採点用ラベル、将来の回答、結果の混入・不正な再送・入力分割の改ざんを**合成負例テストで拒否**する。**重要：まだ真の独立評価器ではない**。本物の採点は別プロセス保管、正式な方法凍結と別途実行承認が必要。[設計](experiments/ACTIVE-001/e0-custody-boundary-draft.md) / [Issue #104](https://github.com/ryonakayama234/DekaSugi/issues/104).
