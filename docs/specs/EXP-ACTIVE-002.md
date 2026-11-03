# EXP-ACTIVE-002 — 経験から獲得する質問技能 / Design V2

id: EXP-ACTIVE-002-SPEC
status: proposed; OWNER_DESIGN_APPROVED; METHOD_NOT_FROZEN; NOT_IMPLEMENTED; NOT_TRAINED; NOT_SCORED
updated: 2026-11-03
tags: active-learning, inquiry-skill, representation, wake-sleep, causal-inference

## Decision and scope
[Issue #162](https://github.com/ryonakayama234/DekaSugi/issues/162)でownerが2026-11-03に**研究方向V2**へ合意。これは方法・母集団・閾値の独立査読済み凍結ではない。PR1はdocs onlyで実験起動権限を持たない。研究目的は「公開された有料経験から獲得した型付き質問技能を外部化して、新しい構造の世界で合法な次行動を因果的に変え、未知操作の予測と取得情報の効率を改善できるか」。AIの一般知能を主張しない。

主責務: prospective `packages/inquiry_learning`。既存mainの`packages/active_learning`はACTIVE-001固定Catalog・2-question基準であり変更・改名しない。Draft `rep005_g0c` / `rep005_study_v4`は参照証拠であって、main搭載モジュールでも検証済み研究基盤でもない。将来の再利用は別々の監査可能なPRで行う。

## Problem decomposition and falsifiable hypotheses
| Gate | Hypothesis | Falsifier / stop |
|---|---|---|
| H1 / G0 | 固定世界集合・事前分布・初期状態・合法操作・予算に、早期分岐に依存した正の適応利益が存在する | 厳密閉クラスで最強open-loopと同値、期限切れ/枠外は`NOT_CERTIFIED` |
| H2 / G1 | 公開有料観測から世界モデルの未知予測が改善する | 強い同文法・同データの静的ベースラインと同点以下 |
| H3 / G2/G3 | 獲得した質問技能の**質問選択へのdispatchのみ**ONにすると次行動と下流効用が改善する | 合法行動差ゼロ、または差があっても有用性なし |
| H4 / G2/G3 | 構造独立TRAIN世界から獲得し保存した技能を、構造が異なるUSE世界で再利用できる | 同一トポロジーのrole-renamingのみ、またはOFFとの差なし |
| H5 / future | 既存表現の有限意味域での不足を反例が証明し、型付き拡張が未知予測を改善する | 旧表現でも同じ意味を表現可能、探索失敗を表現不能と誤認 |
| H6 / future | TRAIN費用を含む長期的な再利用効率が改善する | 使用回数を含めた償却で利益が負 |

H3/H4が次期研究の中心。H1は機会診断、H2は世界モデルの予備的学習能力、H5/H6は拡張課題。学習された**新しい技能AST**と、研究者が固定した**技能メタ文法**を混同しない。名前の付替え、記録を固定規則として再生するだけの行為、訓練後の単なる重み変更は「新しい表現力」の証明ではない。

## Alternative designs and rationale
1. Exact finite posterior + optimal adaptive planning: closed finite classの理論上限/公平な比較には強いが、他課題への技能獲得を実装しない。
2. Instance/KNN retrieval: 公開経験を記憶する強い対照だが、抽象的探究手順の獲得とは別。
3. **Selected: typed policy synthesis + prior/posterior + fixed-codec two-part MDL**: learned executable branch, provenance and ablationを監査可能。メタ文法に拘束される限界を明示。
4. Small MLP: controlled exploratory control (n=0/1/4/16 epochs and training exposures candidates); main mechanism acceptanceから分離。
5. End-to-end RL: data/compute/confound costが大きいため今回は保留。

最適化対象はラベルやLaw IDの特定ではなく、**事前固定された未知の合法操作結果の予測**。Law-ID MAPは診断的な補助指標のみ。各世界の同値法則を正答扱いにするかは、評価意味域での振る舞いの同値性に基づき定義する。

## Formalized inquiry opportunity
有限クラス `H={h_1,...,h_k}`, 事前分布 `p(h)`, 公開初期状態 `x0`, 状態依存合法行動 `A(x,hist)`, 予算 `B`, 末端効用 `u`を**検査前**に固定する。
- Adaptive: `V_ad = max_{policy: observations→legal actions} E_p[u | policy,B]`.
- Open-loop: `V_ol = max_{legal contingent-independent schedules} E_p[u | schedule,B]`; 状態依存の合法性が異なる場合には「全潜在経路で合法な事前操作列」に限定し、比較可能性を審査。
- `gain=V_ad - V_ol`; 正の証明がない環境はmechanistic positive群に採用しない。等値は真のNULLとして保存。
- 値の意味は`law_id_MAP`か`heldout_prediction_utility`かをレシート内で厳格に固定。前者の正の差から後者の正の差を**推論しない**。
- 同値・非到達・最初の情報が最終ステップ・強い固定列で全解決・予算上限・タイムアウトを分ける。計算上限に達した証明は`NOT_CERTIFIED`。
- 調査は二系列: (a) 自作positive/negative fixturesで機構を校正、(b) 結果選別なしの新しい事前固定母集団で適応機会の割合を測定。前者の成功率は後者の有病率や能力汎化を意味しない。

G0C-3の48 root attempts/45 valid/3 invalid、9 valid closed 4-law panels and zero certified adaptive MAP advantageは既存Draftの探索的診断。n=9を母集団の独立検証と呼ばない。role-orbitsは独立研究ファミリーの証明ではない。既存sourceとゼロ証拠を改竄せず、新しい分布ならversion/new seed/ancestryを切る。

## Learning and policy mechanisms
### WAKE (fast within-world state)
`belief_t(h) ∝ p(h) ∏_{j≤t} P(o_j | h, a_j, history_j)`; noiseless finite baselineなら正規化した整合集合。未観測反事実や隠れたLawを使わない。候補集合が空なら`MODEL_INCONSISTENT`で停止/修復へ通知し、捏造再重み付けをしない。設定したprior自体の妥当性、学習したpriorの事前知識を別レポートに分離。

### Inquiry policy
`policy(history, belief, snapshot, action_budget) → PolicyDecision`。最初は厳密期待末端効用と情報獲得（例: entropy/Gini）の差を診断し、実用方策は限界資源付きの合法先読み。行動を選ぶ前に`PolicyDecision`をcommitし、公開回答受信後にのみ次の決定を行う。予測関数・belief support・公共prefixの一致を保って`skill_dispatch=ON/OFF`を介入する。ONが単に候補空間/表現力を拡げた場合は質問効果ではなく別コントラストへ分割。

### SLEEP (slow cross-world learning)
複数の構造別TRAIN世界の**有料観測された軌跡のみ**から、typed DSLの条件・行為・分岐・適用条件の候補ASTを合成。固定された符号化長`L(skill)+L(public_data|skill)`と型/最小支援/反例検査で候補化。MDL codec, tie-break, training world groupingと候補文法は独立レビュー後にversion固定。トレースの取得方策によるselection biasを監視し、未選択の行動結果を観測値として扱わない。

### DREAM
Snapshot+学習世界モデルが想像したcounterfactualは**model-generated hypothesis**。真の公開世界から取得した有料回答に偽装せず、教師ラベルや独立検証事例に流用しない。候補が仮想世界で良いだけなら正式登録しない。

### Snapshot
Typed immutable candidate with `schema`, `body_ast`, `applicability`, `evidence_digest`, `source_version`, `codec_version`, `status`, `digest`. Persist and reload in a fresh learner process before USE; integrity digestは改変検知であり、独立証拠の認証ではない。正式`library`への自動昇格はなし。

### Representation-repair fork
`inconsistent`は必要条件にすらならない: ノイズ、観測の実装ミス、候補不足、推定失敗、資源制限を先に切り分ける。旧L0有限意味域の完全列挙で非表現性を証明した場合のみ新規typed predicate ASTを「表現拡張候補」と呼ぶ。新DSLと同じexpressivityのSTATICコントロールに勝たなければ、学習された発明の価値としては採用しない。

## Measurement and controls
単位は`independent mechanism family`; family内world/seed/role-renaming/audit probesは技術的反復であり独立標本を増やさない。事前固定のfamily重みで一度world平均→family平均。whole-populationには機会ゼロ、識別不能、負の転移を含む。conditional opportunity-positive分析は副次であって主母集団へ一般化不可。

事前固定したevaluator-only未使用の合法probe集合で、`U_w=(correct - wrong)/N_probes`（abstain=0）を候補効用とする。正答率、誤答率、coverage、予測較正（確率を出す場合）、操作回数も併記。Uの正規化分母に棄権を含む。ユーティリティ定義自体は提案でありmethod freeze前に独立審査する。

`Delta_inquiry = mean_family(mean_world(U_ON - U_OFF))`; ON/OFFは同一構造のworldと同一pre-divergence公開prefix・同一Snapshot・同一prediction engine/posterior/hypothesis supportを使用し、違うのは質問技能をselectorが利用できるかだけ。分岐後の公開履歴はそれぞれ合法に実行し、別々の結果を受け取る。世界間の試行に状態持ち越しなし。**まず同一prefixでの合法なアクション差、その後独立未知probeの予測利益**を両方確認。ON/OFFとともにFIXED, STATIC (同じ表現可能文法・CPU上限・先読み), RETRIEVAL, rank-only learned, body-off and exact ORACLEを区別。Oracleの真値・後知恵best-armをlearnerへ渡さない。

費用: `C_lifetime=C_train+M*C_use` (Mを複数値で報告); paid train+USE interventions、planner model evaluations、expanded primitive operations、CPU/wall/RSSの測定値は別軸。処理時間からprimitive費用を推測しない。比較は同一公開データ予算、同一テスト時操作上限、候補の表現力、計算上限と資源超過扱いを宣言。

初期の候補ゲート `Delta≥+0.05` and family-cluster 95% interval lower>0 は**人間が合意した開発上の方向づけのみ**。独立なfamily定義・標本数・power>=80%・区間法・多重比較・母集団重み・事前停止・alphaは未審査で`METHOD_NOT_FROZEN`。既存n/スコアから後付けで適切な閾値を決めない。旧FINAL・DEVと今回のDraft診断を新しい確証研究へ使わない。

## Failure reporting and nonclaims
`PASS_MECHANISM`はlegal selector change、`PASS_LEARNING`はunseen world benefit、`PASS_TRANSFER`はstructural disjoint holdout、`NEGATIVE`は有効な負の測定、`UNDERIDENTIFIED`は分母/独立性/証明不足、`NOT_RUN`は未実行、`INVALID`は信頼境界破壊。これらを一本の「成功」へまとめない。

Reference: [method plan](../../experiments/EXP-ACTIVE-002/plan.md) / [ADR](../architecture/decisions/ADR-ACTIVE-002.md) / [evidence ledger](../../experiments/EXP-ACTIVE-002/runs/README.md) / [mission](../vision/mission.md) / [METRO-VALIDITY](../metrology/validity.md).
