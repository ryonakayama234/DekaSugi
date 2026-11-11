# 仕様パック: WORLD 最小実験の機械可読仕様（ドラフト v3 付属仕様書）

id: WORLD-PREREG-SPEC-20261110-01
status: specification_pack_draft / not_frozen / not_implementation / no_calibration / no_experiment
updated: 2026-11-10
tags: successor-axis, world-expansion, specification, preregistration-draft, supervisor

> 本書は事前登録ドラフト v2（WORLD-PREREG-DRAFT-20261110-01、PR #194）の付属仕様書であり、Research Lead 再審査（PR #197）と監督者回答（PR #197 コメント 6768141971）、Owner 採用（2026-11-10）に基づき、凍結前 blocking checklist B1〜B6 を PASS 判定可能な形へ落とすための機械可読仕様を集約する。本書の数値は「確定候補」であり、凍結値ではない。凍結は CAL プロトコル承認と CAL 後の事前登録凍結（Q8 の二分）による。

## 0. v2 本文への修正条項（本書が優先する）

- v2 §2 の「デモを経験予算に課金」は廃止し、本書 §1 のデモ規則（別枠・共通固定）に置換する。
- v2 §5 の AULC 定義「台形積分し (B+1) で正規化」は廃止し、本書 §4 の定義に置換する。
- v2 §10 の「Owner による凍結判断 → 校正」は、本書 §7 の2段階手続き（CAL プロトコル承認 → CAL → 事前登録凍結）に置換する。
- それ以外の v2 の規定は本書と矛盾しない範囲で存続する。矛盾があれば本書を優先し、矛盾箇所を Lead 判定時に列挙する。

## 1. 課題提示とデモの規則（B1）

- デモ対の数: family あたり **3対**（確定候補）。提示は当該 family の試行開始前の一括提示のみ。追加取得・再提示は不可。
- デモは全 arm で同一（同一インスタンス、内容の digest を goal contract version とともに記録）。デモは学習予算 b に課金しない。「仕様コスト」として費用ベクトルに別掲する。
- 評価フェーズ: holdout family のデモも同じ3対を課題提示の一部として与える。評価デモの内容を学習へ持ち帰ることは禁止（評価時再学習0）。
- task tag: 法則の生成 seed と独立な登録済み乱数源から引く不透明 ID。同一 law はフェーズ内で同一 tag を再使用し、異なる law が tag を共有しない。割付順序は無作為化する。CAL で ID-only 対照により、tag からの法則予測が偶然水準を超えないことを検査する。
- 公開履歴の定義: H_t = (task_tag, demo_set_digest, 初期観測, (行動, 観測, フィードバック) の列)。公開識別不能とは、到達可能な全ての合法行動列に対して H の列が一致すること。
- フィードバック規則: TRAIN では試行ごとに成功/失敗を返す（費用ベクトルに計上）。評価では完了後の監査専用とし、学習へ戻さない。

## 2. grammar 表と到達可能性（B2）

| 評価器 node | 型・arity | 学習側 constructor | 制約 |
|---|---|---|---|
| ATOM(a) | 原子行動 a（11種）、arity 0 | 生成不可（初期在庫のみ） | 意味名付きマクロなし |
| SEQ(x1..xn) | AST 列、n≥2 | compose | 連接 |
| BIND(v, e, body) | 型付き変数 v、スコープは body 内 | abstract（anti-unification） | 束縛は型一致時のみ |
| CMP(op, l, r) | op ∈ {EQ, LT, LE}、bool | predicate-slot の部品としてのみ | 被演算子は観測特徴・束縛変数・相対位置定数に限る |
| BRANCH(p, t, e) | p は述語型、t/e は AST | branch-construct | 3スロットは経験由来の記号でのみ充填可。初期 snapshot にインスタンスなし |

- 定数: 記号リテラル A〜D、カーソル/選択アンカーへの相対位置 -16〜16。絶対位置の定数は禁止。
- サイズ上限（確定候補）: AST 深さ ≤8、node 数 ≤64、述語 AST の深さ ≤3。
- 到達可能性の定義: H+ の探索空間 = 空 snapshot から上記 constructor の閉包で到達できる AST 全体。FULL の獲得も同じ constructor のみを使うため到達可能集合は同一であり、差は探索誘導と経験効率のみ、と明記する。実装がこの閉包を保証できない場合は「同一候補空間」の記述を撤回し、表現差を開示して再設計する（反証条件）。
- 検査: 空 snapshot で BRANCH の完成インスタンスや意味述語を名前参照で呼べないこと。学習器と評価器の共有コード・read path は本書のアクセス表（§6）に従う。

## 3. arm の権限・費用 matrix（B2/B5）

| arm | 構築の許可 | USE の許可 | 特記事項 |
|---|---|---|---|
| FULL | compose/abstract/predicate-slot/branch-construct の全て | 獲得した全記号 | 主張の本体 |
| OFF | FULL と同一の訓練（同一 snapshot） | 獲得物の USE のみ評価時にマスク。再学習・別前処理は禁止 | 同一性は snapshot digest で確認 |
| PRED-ONLY | branch-construct を除く全て | BRANCH を含む AST は snapshot 読込時に拒否 | 構築・USE の双方で禁止 |
| REC | 観測の feature map（CMP を含まない統計量への写像）の学習のみ | 固定形の第一階方策テンプレート内での feature 使用 | 述語型 AST の生成は型で不可能にする |
| RANK-ONLY | なし（候補集合は H+ と同一閉包） | 探索順序（prior）の学習のみ | 候補集合の同一性は §2 の閉包定義による |
| FIXED-IF | なし | 贈与された完成 BRANCH スキーマと、FULL と同じ述語発見の範囲 | 贈与アドバンテージを開示。「同一 seed」とは記さない |
| LOOKUP | なし | 凍結した距離関数・容量・abstain 方針による episode 記憶の検索のみ | 距離関数と容量は本書の確定時に固定 |
| H+ | なし（探索のみ） | §2 の閉包全体への同予算探索 | 無制限 oracle は主成績に含めない（機会診断専用） |

- 全 arm 共通: 主比較は同一の事前割付公開 trace のリプレイ。能動収集は副比較として分離し、因果主張を限定する。
- 費用ベクトル（単位ごとに独立照合）: 予算 b（原始呼出累積）、episode 数、候補評価数、有料問い合わせ、成功フィードバック数、学習準備費、USE 費、CPU、wall、RSS、保存量。単一の加重和に混ぜない。
- 停止条件・holdout・公開情報は全 arm で同一とする。

## 4. 測定の確定定義（B4）

- 予算軸: b = 学習器が発行した原始操作呼出の累積（no-op を含む）。上限 B は CAL プロトコルで固定する確定候補値を持つ。
- checkpoint: b ∈ {0, B/8, B/4, 3B/8, B/2, 5B/8, 3B/4, 7B/8, B} の9点。s_f(b) は checkpoint 時点の凍結 snapshot を評価して得る成功率（棄権・打切り・INVALID は分母に残す）。checkpoint 評価費は測定費として全 arm 共通・別掲し、b に課金しない。
- AULC_f = （s_f の台形積分） / B（B>0）。全 checkpoint で s=1 なら 1。
- 主エンドポイント: Δ_f = AULC_f(FULL) − AULC_f(control) の family ペア差。最強対照の事後選択には family 単位 max-T bootstrap による同時95%区間を用いる。
- 判定の階層: 第一に AULC（点推定 ≥ +0.15 かつ同時区間下限 >0）、追加 AND ゲートとして B 時点の達成率（G1 ≥90%、G2 ≥80%、最強対照差 ≥ +10pp、いずれも確定候補で CAL 時に1回だけ改訂可）。
- G2 の長さは「初期 buffer 長」と定義する（13〜16）。中間 buffer は上限16を超えられないため、可解性は CAL で類型ごとに列挙し、容量で到達不能な類型は生成規則として事前に除外し、元の分母と除外数を報告する。

## 5. 法則母集団・検出力・route 決定表（B4）

- law の正規形: (テンプレート ID, 述語 AST 正規形, 分岐操作, 対象役割, 正規化パラメータ)。unique ID = 正規形のハッシュ。n は unique law 数で数え、同一 law の再出現は加算しない。重複率・テンプレート別内訳は必須報告。
- 生成分布（確定候補）: 4族（転写/反復コピー/観測依存編集/2段連結）へ均等配分、各族内のテンプレート・パラメータ・長さ・語彙は仕様確定時に固定する抽出分布に従う。推定対象はこの登録分布に限る。
- TRAIN/CAL/holdout は親法則の連結成分で隔離する。G1/G2 の同一 law 派生は同一 cluster。
- 定数（CAL 前に固定）: δ_AULC = 0.15、δ_pp = 0.10、片側 α = 0.025、power = 0.80、n 算定は2ゲート分の Bonferroni α' = 0.0125 を用いる保守形、分散入力は CAL 実測の paired SD と discordance の片側80%上限。
- 決定式:
  - n_binary = ceil( (z(1−α') + z(power))² × (p_d_upper − δ_pp²) / δ_pp² )
  - n_aulc = ceil( ((z(1−α') + z(power)) × sd_upper / δ_AULC)² )
  - n_required = max(n_binary, n_aulc)
  - 比較順序: n_required → N_unique（生成可能な unique law 数）→ 総コスト上限 cost_cap（確定候補は CAL プロトコルで金額・時間に換算して固定）。
  - n_required ≤ N_unique かつコスト内 → STATISTICAL（n = n_required）。
  - 有限 frame が全列挙可能で |frame| ≥ n_min_descriptive（確定候補 30）→ FINITE_DESCRIPTIVE（全件評価、分布外一般化・検出力の主張なし）。
  - それ以外 → STOP_UNKNOWN（対照を弱めない。再設計へ）。
- 閾値候補の改訂は route 計算の前に1回まで、CAL の難易度データのみに基づき、判断ログを残す。

## 6. K0・キル条件の判定表、ログ schema、アクセス表（B3/B5/B6）

### K0（校正系列のみで実施。oracle は上界専用）

| 診断 | PASS（継続） | STOP | UNKNOWN |
|---|---|---|---|
| K0-a 分岐証人 | H_0 が同一で共通 open-loop 系列（H ≤ 確定候補 64 手）が存在せず、分離可能な条件付き方策が存在 | 証人ペアが皆無 | 列挙が未完結 |
| K0-b 公開識別性 | 必要情報が行動選択前に H_t へ到達し、合法な分岐で分離可能 | 列挙完結のうえ識別不能（UNIDENTIFIABLE） | 列挙が未完結 |
| K0-c 同予算の余地 | (oracle AULC − 最強対照 AULC) の同時95%区間上限 ≥ δ | 同上限 < δ（飽和） | oracle 列挙が未完結 |

- K0-a の証人不存在は「二階スキーマ必要性」の主張のみを止め、他の経験効率の問いを自動的に偽とはしない。STOP の原因は診断ごとに分けて記録する。

### キル条件（数値はいずれも確定候補）

| 条件 | 判定式 |
|---|---|
| K1 実使用 | 診断 family（事前固定20件）× checkpoint で、ON/OFF の最初の行動または trace digest が異なる組が1件以上。確率的方策では診断状態の行動分布の total variation > 0.1 の状態が1件以上 |
| K2 等価性 | FULL−REC の AULC 差の両側同時区間が ±0.05 内に収まる場合にのみ「再符号化で説明できる」とする |
| K3 結果区分 | 負 = 区間上限 <0。小さい = \|Δ_AULC\| < 0.05 かつ成功率差 < 5pp。不精確（INCONCLUSIVE）= 区間が 0 と ±δ の双方を跨ぐ |
| K4 INVALID | 汚染が及んだ family のみ隔離し再採点しない。再実行は新しい事前登録版でのみ可能 |

### ログ schema（最小列）

episode_id / law_unique_id（評価側のみ親 ID を併記）/ phase（TRAIN/CAL/EVAL）/ goal_contract_version / task_tag / demo_set_digest / checkpoint_b / step_index / observation_before_digest / legal_action_set_digest / chosen_action / observation_after_digest / outcome_kind（SUCCESS/FAIL/INVALID/ABSTAIN/STOP）/ 費用ベクトル全項目 / symbol_event（feature-only/predicate/macro/schema の型、依存先、proposal/rejection/promotion/USE/OFF、AST digest）/ receipt_digest。

### アクセス表

| 主体 | 読めるもの | 読めないもの |
|---|---|---|
| 学習側 | 公開履歴 H_t、公開 trace、自己の snapshot | 評価 manifest、hidden target/rule、holdout score、生成 seed |
| 評価側 | 全 manifest、verifier の真値、凍結 snapshot | （学習への逆流経路を持たない） |
| 監査者 | digest 一覧、ログ全件（事後） | — |

- receipt: 生成器・本仕様・分析コード・snapshot の digest を source-first の manifest に集約し、第三者は digest 再計算と trace 再生で検証する。

## 7. 手続き（「凍結」の二分、B6）

1. CAL プロトコル承認: 本仕様パックを含む校正の設計と決定規則を Owner が承認する（CAL の実施許可とは別）。
2. CAL 実施 GO: Owner の別途判断。GO の場合のみ、隔離された非採点 CAL を実施する。
3. 事前登録凍結: CAL 結果に基づき、数値・生成器・split・分析手順と digest を Owner が receipt として承認する。
4. 実装・学習・正式評価は、凍結後も段階ごとに別途 Owner GO を要する。
- 決定記録の正本は Issue #195 のコメントとし、凍結時には receipt 文書を repo に置いて Issue から参照する。PR #194/#196/#197 は引き続き Draft とする。
