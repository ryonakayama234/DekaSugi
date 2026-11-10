# WORLD-PREREG-R6-20261110-06 — Research Lead 第4版 exact-head 再判定・最終受け入れ申請の前提

id: WORLD-PREREG-R6-20261110-06
status: research_lead_v4_review / REVISE_WITH_CLOSED_REPAIR_PROPOSAL / NOT_DESIGN_CONSENSUS / NOT_FROZEN / NO_CAL_APPROVAL / NO_CAL_GO / NO_IMPLEMENTATION / NO_EXPERIMENT
updated: 2026-11-10
tags: world-expansion, preregistration, research-lead, exact-head-review, docs-only, no-execution
author_role: Research Lead (ChatGPT)
review_target: [PR #194 exact head 6f3a97b5be23b847405828f63530d7a3c2d76c31](https://github.com/ryonakayama234/DekaSugi/pull/194)
acceptance_request: [WORLD-PREREG-RQ6-20261110-06](WORLD-PREREG-RQ6-20261110-06-final-closure-proposal-to-muse.md)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **審査権限の範囲**: 本書も別紙も Research Lead の設計上の判定・処方であり、Owner／監督者の採用や CAL プロトコル承認ではない。CAL GO、CAL、事前登録凍結、実装、学習、評価、結果認定、既存 PR の Draft 解除・main merge を行わない。数値はすべて凍結前の候補。例示の反例は仕様に対する論理的検証であり、CAL や実装テストはしていない。

## 0. 審査対象・判定基準・総合

- **現行正本**: [WORLD-PREREG-SPEC-20261110-04 §0〜§7・付表A](https://github.com/ryonakayama234/DekaSugi/blob/6f3a97b5be23b847405828f63530d7a3c2d76c31/docs/research/WORLD-PREREG-SPEC-20261110-04-specification-pack-v4.md)、blob `1b6cae0c16da158ce216c69aa834f007fef89d49`。-01／-02／-03 は履歴であり混用しない。
- **存続範囲の照合**: 同じ head の [ドラフト v2](https://github.com/ryonakayama234/DekaSugi/blob/6f3a97b5be23b847405828f63530d7a3c2d76c31/docs/research/WORLD-PREREG-DRAFT-20261110-01-minimal-experiment.md)、blob `f0218f9454a92eb9512463be444f69e3c6fc7530`。v4 §0.1 で明示的に置換された v2 規則は競合として再計上しない。
- **判断来歴**: [Muse の R5/RQ5 受け入れ判断 6770105397](https://github.com/ryonakayama234/DekaSugi/pull/200#issuecomment-6770105397)、[Owner 採用 6770241854](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6770241854)（文言は設計採用であり CAL 承認なし）。[R5/RQ5 PR #200](https://github.com/ryonakayama234/DekaSugi/pull/200)。
- **PASS** = CAL 値と実装前でも設計上の定義・判定・分母・権限が非矛盾で fail-closed に実施可能。**PARTIAL** = 主要改善は成立するが、形式的・操作的な閉鎖を要する。**FAIL** = 項目の中核的な推定/判定規則に、相容れない規則または検証不可能な主張が存続。数値未凍結のみでは減点しない。

**R6 対象現行版の判定: B1 PARTIAL／B2 PARTIAL／B3 PARTIAL／B4 FAIL／B5 PARTIAL／B6 PASS。PASS 1・PARTIAL 4・FAIL 1。総合 REVISE。設計合意は現時点で未成立。** 以下の未解決事項を **[RQ6 の一括終結処方案](WORLD-PREREG-RQ6-20261110-06-final-closure-proposal-to-muse.md)** によって閉じることを Muse に提案する。**提案の記載自体を v4 PASS と誤認しない**。

## 1. B1〜B6、§0.2 と独立に本文を確認した結果

| 項目 | 判定 | 本文/付表で確認した改善 | 現行 v4 に残る理由 |
|---|---|---|---|
| **B1: goal contract・識別可能性** | **PARTIAL** | §1: デモ3対、law/episode 2層、EVAL は未見 law の「TRAIN で同定した結果」を持たずデモ/初期観測から一時推論のみ、tag 射影 π(H)、ID-only AUC。§2: 正解対応なしの公開 token table。§1 証人は長さ4、候補であると明示。 | §1 の K0-a **証人候補** `ABAB→ABABA` / `ADAD→ADADC` は **付表A の成功時自動終了を利用する長さ7の共通 open-loop** により反証される（次節の厳密トレース）。未見 law のデモ3対が行動選択前に何を区別するか、law 横断推論と law 当ての証拠上限は §6 の K0-b に依存する。候補を成功例として扱わず失格登録・再探索規則へ変える必要。 |
| **B2: seed grammar・arm 権限** | **PARTIAL** | §2/付表A: `Alphabet(phase)` の live `Sym` と rename equivariance、公開入力経路 token table/デモ/観測、law の正解対応は非公開。§3: 共有特徴だけで書く FIXED-IF、PRED-ONLY の SEQ/BIND マクロ USE 許可、Space と R_FULL の分離、候補探索の費用ベクトル。 | §3 の表は arm×「構築・USE」であり、監督者が受け入れた **arm×node×constructor×READ×USE の具体的 access matrix ではない**。「共通 read path」との宣言に対するファイル/フィールド別の可否・昇格時 ACL、候補評価単価/先渡しの境界が未列挙。§2 の Sym「役割名」の表示順から G1 改名の正解役割が一意に回復しないよう、token table に semantic ordering が無いことを明記する必要。 |
| **B3: K0-a/b/c・UNKNOWN** | **PARTIAL** | §6: 同一 law の異なる instance に K0-a、異なる law には TRAIN/EVAL を分ける K0-b、状態ペア BFS と履歴木 DP、K0-c 抽象 support 上の厳密値、holdout 非アクセス、UNKNOWN 優先。 | **§6 K0-a** の BFS は成功時終了を absorbing success とするか未明記。これは §1 の「証人候補を BFS で確定する」条件の真偽を変える。現行の成功時終了で計算すると長さ7の共通 open-loop が存在し、当該候補は**失格**である。K0-c 抽象分布の列挙完結証明/厳密値証明書・K0-b の比較単位を CAL プロトコル入力として固定する必要。 |
| **B4: AULC・抽出・power・route** | **FAIL** | §4/§5: `F`、`H=F∩holdout`、`q_l`、正しい HT `q_l/π_l`（certainty `q_l`）、Sampford、SYG、10成分 AND、union bound、閾値より上の ε planning alternative、CAL 後の α/power 判定への順序を確認。R5 の HT/estimand/ゲート9問題は修復。 | §5 の **FINITE_DESCRIPTIVE route** はなお `|frame|≥30` なら「全件評価」と記す。frame は §5 で **全適格 F** と定義した一方、推定対象・評価適格数は **H** なので、F 全件なら TRAIN/CAL と overlap し、H 全件なら `|F|≥30` という条件は不適切。例えば `|F|=100, |H|=1, n_required>1` でも FINITE_DESCRIPTIVE に入る読みに見える。別途 §4 で汚染 family を集約から除外した完走を許容すると、HT の包含確率を維持したままサンプルが非無作為に欠け得る。さらに `same split` の CAL power simulation が sealed holdout の law-level q / split 情報を読めるのか §6 access と対応していない。 |
| **B5: 帰属・等価性・null / invalid** | **PARTIAL** | §3: PRED-ONLY 第一階マクロの USE、§6: 機構説明を抑えた K2、片側主検定と両側等価性の区別、3階層の event/family/run status、失敗を含む outcome の網羅的な決定順序。hash mismatch に STOP_INVALID、再集計禁止を確認。 | §4 は FAMILY_INVALID を「有効な集約から除外」、§6 は K4 family 隔離、hash mismatch 時だけ run STOP と規定。**hash 以外の K4 汚染**で一部 family を除いて run COMPLETE にすると、§5 の事前包含確率 `π_l` に基づく HT 推定が不完全になる。結果の主張・停止状態を一本化する必要。§6 outcome 順序の最初の FAMILY_INVALID は「COMPLETE かつ集約可能」条件との関係を明文化する必要。 |
| **B6: CAL 分離・封印・改訂来歴** | **PASS** | §0.1 と §7 により v2 改訂条項を明示置換。§7 の DESIGN_DRAFT→PROTOCOL_APPROVED（初期値・許可更新規則 lock）→CAL_AUTHORIZED（別 GO）→CAL_COMPLETE（許された1回更新）→FROZEN（別 Owner receipt）→EXECUTION_GO（別 GO）は一貫。§6 は sealed holdout の非アクセスと digest 不一致の STOP を明記。 | **PASS は手続きの構造に対する判定**であり、現在の時点で Owner CAL 承認を代行した意味ではない。具体的 ε/更新幅/乱数源/manifest 型と digest は PROTOCOL_APPROVED でロックする候補・成果物であり、現在未凍結であることを単独の不合格としない。ただし B4 の power calculation access を具体化するのは依然必要。 |

## 2. MODIFY 条件の実装監査（前回 Muse 判定と照合）

| 条件 | 確認 | 記載の照合結果 |
|---|---|---|
| **RQ5 Q1 MODIFY: 長さ4証人は候補、open-loop 不在は BFS 待ち** | **文章上は遵守。ただし候補は反証可能どころか反証される** | v4 **§1** に「候補」「BFS 反例なら失格」、**§6** に状態ペア BFS。ただし終了時 success を考慮すると次節の反例。 |
| **Q2 MODIFY: 公開 Alphabet と law 役割秘匿、入力経路3つ** | **遵守、封印細則を提案** | v4 **§2** は Alphabet の値集合を公開し、law の正解対応を非公開。token table／デモ／観測に限定。 |
| **Q2 MODIFY: FIXED-IF 専用 feature は増やさない** | **遵守** | v4 **§2** 全 arm 共有語彙、**§3** `COMPARE(EQ, カーソル位置の記号, Sym 役割名)`。 |
| **Q2: arm×READ×USE 全表** | **部分反映** | v4 **§3** 構築/USE と「共通 read path」宣言。row×node×constructor×read-field の全量表まではない。 |
| **Q3 PATCH A のみ、条件付き estimand、certainty q** | **遵守** | v4 **§0.1/§5** に H/q/HT、全母集団への一般化の不採用、n=|H| 全列挙式。 |
| **Q4 MODIFY: m=10、閾値+ε、CAL 後 ε 選択禁止** | **遵守** | v4 **§5** の10成分/β=0.02×10、ε の選択関数をプロトコル事前承認。 |
| **Q5 3階層、hash mismatch run STOP** | **遵守。ただし K4 非 hash ケースの推定整合不足** | v4 **§4/§6** に status 3階層と STOP_INVALID。 |
| **Q6 6段階、初期値・1回更新** | **遵守** | v4 **§7** の3区分＋6状態。 |
| **Q7 MODIFY: INSERT/PASTE 容量式、oracle は抽象 support 上の値** | **遵守** | v4 **付表A** `L-r+1` と `L-r+|clipboard|`、**§6**「抽象 support 上の厳密値」と sealed holdout 非アクセス。 |

## 3. 発見した新規・存続不整合（v4 §0.1 の意図的置換は除く）

| ID | 種別・位置 | 問題と必要な処方 |
|---|---|---|
| **R6-1 実行可能な反例** | v4 §1 / §6 K0-a / 付表A 終了 | 候補として掲示された pair が共通 open-loop 長7で成功する。BFS の吸収成功状態を明文化し、当該候補失格を記録。 |
| **R6-2 F/H 記述的ルート衝突** | v4 §4/§5 | F と H を分けたが FINITE_DESCRIPTIVE は `|frame|` と「全件評価」。`|H|` の条件で H のみ全件を測ること。 |
| **R6-3 HT の非応答問題** | v4 §4/§5/§6 | K4 で family を除外したまま complete できれば HT の元の inclusion design を破壊。complete/invalidate を fail-closed に。 |
| **R6-4 CAL power の読み取り境界** | v4 §5/§6 | `same split` の CAL simulation と sealed holdout 不参照が併記。実 law 母集団の q/適格集合をどの role がいつ読むか、事前固定の summary か CAL surrogate を使うか確定要。 |
| **R6-5 arm アクセス表の未達** | v4 §2/§3/§6 | Muse が受け入れた row×node×constructor×READ×USE が本文にない。宣言だけでは evaluator/learner の権限監査不可。 |
| **R6-6 Sym token table の順序情報** | v4 §2 / §3 FIXED-IF | 公開 token table 自体は適切だが、列挙順・表示役割が TRAIN から G1 へ正解対応を符号化し得る。役割は学習 API 非公開とし、α-equivariance を law を含むデモ/score まで確認。 |
| **R6-7 v2 非置換との運用境界** | v2 §0/§3/§9、v4 §3/§5/§6 | v2 の同等学習/探索資源・8 arm の記録要求に対し、v4 は「同じ Space だが同じ評価件数は主張しない」。これは直ちに論理否定ではないが、同一 b と別費用ベクトルの許容差が未定義。主張できるのは原始呼出軸に条件付く比較であり、CPU/候補評価の因果帰属を過大主張しない。 |

**種別**: R6-1 は具体的反証。R6-2 は F/H の定義衝突。R6-3〜7 は inferential contract・情報境界・能力の未規定で、すべてを同種の「形式的矛盾」とは呼ばない。-01〜-03 の旧条文は再輸入しない。

### R6-1: K0-a の open-loop 反例（コード実行・CAL ではない）

v4 §1 の L の instance 1: `ABAB` target `ABABA`、instance 2: `ADAD` target `ADADC`。付表A は `reset` で cursor=0、`MOVE_RIGHT` は一歩右、`INSERT` は cursor に挿入し、**verifier が成功した時点で試行を自動終了**すると定める。

**同一固定列**: `MOVE_RIGHT × 4 ; INSERT(A) ; DELETE_BACK ; INSERT(C)`（合計7原始操作、H≥7 の場合に適法）。

| 時点 | instance1 | instance2 |
|---|---|---|
| reset | ABAB, cursor 0 | ADAD, cursor 0 |
| MOVE_RIGHT ×4 | ABAB, cursor 4 | ADAD, cursor 4 |
| INSERT(A) | **ABABA = target**、成功終了 | ADADA、未達 |
| DELETE_BACK | 終了後は実行されない | ADAD、cursor 4 |
| INSERT(C) | 終了後は実行されない | **ADADC = target**、成功終了 |

この列の行動選択は**初期 buffer も途中観測も見ず固定**である。成功時に片方が自動終了するだけで両方成功する。「共通 open-loop がない」は **H≥7 で偽**。BFS がこの prefix 成功を含む意味論なら当該候補は失格となる。反例が存在することは K0-a の全 family で証人が不可能という一般命題を含意しないが、**現候補を PASS 証人として採用することはできない**。

## 4. 設計合意／Muse への最終申請

**現行第4版のままでは設計合意は未成立**。「残る判断は Owner の CAL プロトコル承認のみ」という断言はしない。

一方、これ以上「監督者が全文改訂→Lead が同じ論点を再発見する」反復にしないため、Research Lead 側で **[RQ6: 一括閉鎖仕様案と受入試験](WORLD-PREREG-RQ6-20261110-06-final-closure-proposal-to-muse.md)** を起草した。Muse への依頼は自由形式の追加質問ではなく、**一括案を ACCEPT / ACCEPT_WITH_EXPLICIT_EDITS / REJECT のいずれかで最終判断**すること。受け入れ後に Owner が採否を判断し、必要な修正文を第5版の最小差分として反映し、その exact head で設計合意を改めて確認する。Owner の権限移譲・自動承認ではない。

**目標状態**は「B1/B2/B3/B4/B5 の論理的阻害が修復され、B6 の明示手続きを保ったまま、残る意思決定が Owner の CAL プロトコル承認可否となる」ことである。CAL プロトコルの作成/承認、実施 GO、凍結、実装 GO、実験 GO は相互に独立。
