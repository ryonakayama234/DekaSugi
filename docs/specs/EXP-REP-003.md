# EXP-REP-003 — 匿名化された条件付き因果世界における質問機会の識別
id: EXP-REP-003-SPEC-V1
status: PROPOSED / DESIGN_ONLY / NOT_RUN
updated: 2026-11-01
tags: research, representation, inquiry, active-learning
issue: https://github.com/ryonakayama234/DekaSugi/issues/133

## 目的と否定可能な問い
主対象: `packages/rep002` の後継となる **Inquiry / World Model（能動探索・因果仮説）**。
補助対象: `representation`（Wake/Sleep/Snapshot）と `evaluation/provenance`（比較と監査）。

EXP-REP-002 の公開DIRECT pilotでは、LQはFAと全評価層で一致し、概念学習固有の利益は示されなかった。公開role=hubがFAへ最適に近い質問対象を教えた可能性がある。本研究では役割ラベルを隠し、状態準備の後でしか見えない条件付き因果法則を導入し、**新たな関係表現の獲得が質問・予測をどう変えるか**を検査する。ただし有利な世界を作れば学習が必要になるとは限らない。先に「改善可能な情報獲得機会が存在するか」を独立に監査する。

## 初期論理: 区別可能性を先に確認する
対象は初期状態では潜在的な離散因果モデルの集合 H。観測履歴 o の下で整合するモデル H(o) を維持する。
次の合法行為列 a_1..a_k に対する予測トランスクリプトが、H(o) の少なくとも二つのモデルで異なるなら、質問には識別機会がある。
- **opportunity witness**: 公開初期状態と合法な行為列で、候補仮説の予測が分岐する有限の具体例。金銭的/計算的予算内で到達できることを要す。
- **no-opportunity witness**: 所与の文法と資源上限内の全到達可能行為列を列挙しても分岐しない証明。未列挙がある場合は UNKNOWN とし、不可能と断定しない。
- 観測上の同値、遷移意味の同値、グラフ同型は別記録とする。無意味なID変換による「新概念」を禁止する。
- Opportunityを発見しただけでは概念学習の価値を実証していない。FAが同じ質問を選べば、学習効果は帰属できない。

## 外界 / 認知 / 観測
最小世界: N=4–6個のBoolean状態を持つ対象。公開情報は順序非依存の匿名ID、観測可能な状態値、法的行為・その費用だけ。hidden_edges、hub/x/yなどの説明用役割、乱数seed、生成クラス、正解法則は learner APIに渡さない。
作用素は setup（合法な状態準備）、pulse（対象に介入）、reset（必要なら費用付き）、observe（操作結果）を分離。意味論は公開された型付きインタープリタによって実装し、潜在的な条件付きゲートを持つ世界で二段階の setup→pulse を必要にできる。
全armに同じ表現文法（direct/conditional, limited composition）、状態観測、状態準備可能性を与える。**文法の供給を学習した新能力と呼ばない**。新しい概念は既存文法で表せる法則/適用条件を学習して登録することから出発する。未知の文法構成子の自律発明は別研究。

## 必須の交絡対照
- LQ: 同じ学習Snapshotを質問と推論に使用。
- LA: LQと同じSnapshotを推論だけに使用し、質問時にbody/applicabilityを封印。
- LR: 同じTRAIN経験に基づく頻度/順位のみ。実行可能bodyは不使用。
- FA: 学習なし、同じ表現文法・共通計算上限の下で最適化された固定の情報獲得器（状態準備と二段階lookaheadを許可）。
- ER: 同じ経験から構造的エピソード検索を行う対照。抽象関係bodyの学習は禁止。
- FX: 固定文法の予算内探索、および可能なら受動観測比較。
- BODY-OFF: LQと同じ学習過程の後で概念bodyのみ無効化（学習効果のアブレーション）。
FAを意図的に弱めない。固定手法を十分探索した場合にもLQが同等なら FIXED_SUFFICIENT を明記する。全arm同一のTRAIN証拠にアクセス可能（FAのTRAIN不使用は意図的対照）、同じlearner-facing入力・合法操作・資源上限・audit世界。能動armの取得観測が異なるのは介入の結果であり、同一証拠だと扱わない。

## 表現の修復と対話的情報獲得
Wake: 仮説→次の質問（情報価値と費用）→結果観測→予測誤差／反例→仮説集合修正。
Sleep: 違う構造・ID・攪乱要因を含む独立TRAIN世界から、再利用可能な条件付き関係候補を帰納。正例・反例・適用条件・由来を保存する。観測不十分は保留。
Dream: 凍結済み仮説を反事実的に実行し、次に候補を分離できる質問を提案。これはシミュレーションであって新しい独立証拠ではない。
Use: 不確実な場合は abstain。未知世界で適用する際は学習した概念候補を public transcript と照合し、反証されたら棄却または適用範囲を縮小する。予測の間違いを「経験不足 / 表現の不足 / 現モデルの誤り」の候補に分けるが、判断を真実として自己承認しない。

## 強い監査と採点前freeze
`ResourceLedgerV2` は expanded primitive nodes、planner rollouts、hypothesis tests、action setup/pulse/reset、CPU、wall、memoryの予算と実測を共通追跡。学習body展開・FA探索・fallback・Dream計算も計上。操作費用だけ合わせて学習前計算を無視しない。
予測器は私的audit入力を見る前に immutable `PredictionCommitV2` として固定。採点器が予測器選択や更新を行うことは禁止。世界単位のpaired AULCと棄権/誤答/全費用、TRAIN世界の構造的独立性を記録。
評価 strata: renamed control、role-blind conditional composition、novel semantics negative transfer、distractors/counterexample revision。開発中に結果を見て選んだ世界は最終評価から除外。世界ファミリを単位とする独立性や必要sample数は正式F0前に設定。

## 学習曲線 — epochという語を曖昧に使わない
TRAIN世界 0,3,8,16,32,64と構造的に異なる世界ファミリ数を独立表示。同一経験の1,2,5,10回再生は決定論的な冪等性検査でありSGD epochではない。観測予算の増減、反例遭遇前後、Snapshot版、活性概念数、未知世界AULC、介入数、全費用を時系列記録。将来SGDの認識器を加えた場合のみ epoch対validationの学習曲線を別系列に設ける。

## 事前の中止条件と採用ゲート
最初にwitnessの充足/非充足/UNKNOWNを検査。意味が異なる候補を区別する合法な質問が予算内にない場合、研究効果を採点せず課題設計を修正する（新しい版と理由を記録）。
観測機会が存在してもFAが成功するなら本研究における「学習固有の価値」はNOT_SUPPORTED。LQ-LAに加えてLQ-FAとLQ-BODY-OFFが異なる独立世界ファミリで改善し、コストと負の転移を含む公正な監査を通るまで概念能力向上を宣言しない。明確な計算上限・採点指標・閾値・検出力を後から都合よく変更しない。
G0–G1の公開人工検証は設計・工学段階。F0正式事前登録、独立custody、DEV/FINAL、初期参照モデル採用は別承認。

## 構想位置づけ
知能を正答の静的蓄積でなく、目的→介入→予測→反例→表現改訂→外部化→次の介入という動的な知的過程として操作的に定義する。これは一般知能の普遍的定義を宣言するものではない。
対話（エージェントと環境、将来は別の知的主体との相互作用）は、相手の変化を受けて問いと表現を更新する能動的学習の場として研究可能。ただし両者が学んだことを同じ評価器で混同しない。
参考: DreamCoder (Ellis et al. PLDI 2021) のWake–Sleep/ライブラリ学習、interventional causal representation learningのidentifiability議論。先行研究の成功は本企画の達成証拠ではない。

## V2 decision source (2026-11-02)
This V1 research proposal is preserved as earlier thinking. The current [science and technical decision V2](EXP-REP-003-DECISION-V2.md), [V2 G0–G5 plan](../../experiments/EXP-REP-003/plan-v2.md), and [dated NOT_RUN design receipt](../../experiments/EXP-REP-003/runs/20261102-design-v2.md) are the normative **owner-approval-pending** design set. No training, implementation or scoring follows from this documentation amendment alone; formal F0 remains separate.
