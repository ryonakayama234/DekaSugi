# WORLD-PREREG-R4-20261110-04 — Research Lead 改訂仕様パックの exact-head 再判定

id: WORLD-PREREG-R4-20261110-04
status: research_lead_revision_review / REVISE_BEFORE_DESIGN_CONSENSUS / NOT_FROZEN / NO_CAL_APPROVAL / NO_CAL_GO / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration, research-lead, exact-head-review, docs-only, no-execution
author_role: Research Lead (ChatGPT)
review_target: [PR #194, exact head 64b3f9e744d5a2efae9178f738ff2b0bfd8740ab](https://github.com/ryonakayama234/DekaSugi/pull/194)
questions: [WORLD-PREREG-RQ4-20261110-04](WORLD-PREREG-RQ4-20261110-04-revision-blockers.md)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **権限境界**: 本書は設計の文書査読であり、CAL プロトコル承認、CAL 実施、事前登録凍結、実装、学習、正式評価、結果認定、main マージのいずれでもなく、その許可も与えない。数値は未凍結の確定候補。Owner の [採用記録 6768813086](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6768813086) は監督者による修正案の設計採用であって、本審査での B1〜B6 PASS を先取りしない。PR #194 は Draft 維持。

## 0. 固定対象・判定基準・結論

- **正本**: [改訂版 WORLD-PREREG-SPEC-20261110-02 §0〜§7](https://github.com/ryonakayama234/DekaSugi/blob/64b3f9e744d5a2efae9178f738ff2b0bfd8740ab/docs/research/WORLD-PREREG-SPEC-20261110-02-specification-pack-revised.md)、Git blob `2cb17636472c4422926c90ffdff79c377ba2946c`。初版 -01 は履歴扱いであって有効な規則として混用しない。
- **併読**: 同一 head の [ドラフト v2](https://github.com/ryonakayama234/DekaSugi/blob/64b3f9e744d5a2efae9178f738ff2b0bfd8740ab/docs/research/WORLD-PREREG-DRAFT-20261110-01-minimal-experiment.md)、[R3/RQ3（PR #198）](https://github.com/ryonakayama234/DekaSugi/pull/198)、[監督者回答 6768694529](https://github.com/ryonakayama234/DekaSugi/pull/198#issuecomment-6768694529)、[Owner 採用 6768813086](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6768813086)。
- **判定規則**: PASS = CAL 値・コードが未作成でも、仕様同士が矛盾せず検査/判定を第三者が一意に定義できる。PARTIAL = 基本方針は成立するが、目的や計算・遷移条件に必要な補完が残る。FAIL = 項目の中心的な実験同定または推論について、現行規則が成立しない/互いに相反する。将来の CAL で決める数値候補の未凍結**だけ**は減点しない。
- **総合: REVISE／設計合意は未成立。B1 PARTIAL、B2 FAIL、B3 PARTIAL、B4 FAIL、B5 PARTIAL、B6 PARTIAL（PASS 0/6）。** 完全な候補仕様が不十分なので「残るのは Owner の CAL プロトコル承認判断のみ」という状態にはまだ到達していない。

## 1. B1〜B6 の節別再判定（§0.2 の自己申告でなく本文から評価）

| ID | 判定 | 対応する改訂版本文 | 改善を認める根拠／未充足の根拠 |
|---|---|---|---|
| **B1: goal contract と識別可能性** | **PARTIAL** | **§1**, §4 分母, §6 K0 | §1 は `π(H)` による tag α-renaming で前回の「law 固有 tag が H0 を強制的に不一致にする」矛盾を**解消**。デモ3対・共通 digest・予算外・TRAIN/EVAL feedback を明示。しかし §1 のアンカー例は、同じ初期観測・同じ行動から law 別の公開観測がいつ分岐するかを示していない。決定的 Editor の遷移が law 非依存で、EVAL feedback が監査専用なら、同一 `π(H0)` から同じ行動を取る限り観測も一致し、条件付き方策が law を識別するという証明にはならない。TRAIN の試行後 feedback での識別と EVAL の識別を別々に定義すべき。また「v2 §1 の（11操作）列挙」は実際には**凍結前に全列挙するとの TODO**で、現存する機械可読行動契約ではない。デモ生成法・合法行動・終了規則・ID-only 検査の統計量/閾値が未充足。 |
| **B2: seed grammar と全 arm の到達可能空間** | **FAIL** | **§2**, **§3**, §6 アクセス | BRANCH-dispatch と初期インスタンスの区別、COMPARE alias、評価順・型、E の順序の明文化は前進。ただし `branch-construct` は「経験由来の記号でのみ3スロットを充填」する一方、E は**空 snapshot** の constructor 閉包、H+ は**構築・永続化なし**で E を探索する。経験がない H+ の E に経験由来の述語・枝が存在する根拠がなく、FULL と同一候補空間を宣言するには情報源または純構文 placeholder の許可を規定する必要がある。さらに §3 FIXED-IF は「構築なし」で「FULL と同じ述語発見」を認めており、述語 constructor をどう使用するかが相反・不明。束縛変数の α 正規化、観測特徴語彙、predicate-slot 規則、型付き引数/合法性、E の必ず有限な列挙順序、prior、REC の `k` と第一階方策形式、贈与 AST の完全形、shared read paths も未確定。 |
| **B3: K0-a/b/c と UNKNOWN** | **PARTIAL** | **§1**, **§6 K0**, §4 | v2 §7 の停止文を §0.1 で明示置換し、主張B/二階帰属/family/GO の遷移表、`δ_AULC=0.15`、H≤64、UNKNOWN 優先を記したことを評価。ただし H 内の状態ペア BFS は**共通 open-loop の有無**を検査するだけで、合法な**条件付き方策が存在する**ことと「必要情報が意思決定前に公開された」ことを証明する手続きにはならない。§1 の TRAIN/EVAL feedback 差と上記 B1 の証人例が未解決。K0-c の oracle AULC を「生成器 support 全件列挙で厳密」と書くが、同予算・同ホライズン・goal の先渡し条件と有限 support/列挙 timeout の判定が残る。 |
| **B4: AULC、母集団、評価 n、route** | **FAIL** | **§4**, **§5**, §6 集約 | AULC の台形積分/B、G2 の OOD 長13〜16、分母の生成前除外/生成後不能、PPS 無復元という新規方針は前回の問題を部分修復。しかし `π_l∝p_l` は固定 n の包含確率として `n p_l>1` となり得るのに、certainty units と抽出算法/2次包含確率がない。`p_l/π_l` を**正規化**する推定量は厳密な HT 合計と異なる（通常 Hájek 比率型）。非復元・不等確率デザインに通常の law cluster bootstrap と iid ベース paired SD/discordance power を直接適用できるという根拠もない。決定的には §5 の「AND 同時検出力の下限=各部検出力の積」が**一般には偽**（下記反例）で、保証する 80% power と route 選択が成立しない。有限 grid、`cost_cap`、実際に holdout に割当可能な `N_eligible`、7対照 max-T の power 法も一意でない。 |
| **B5: 機構帰属・等価性・null** | **PARTIAL** | **§3**, **§5 ゲート**, **§6 K1〜K4/outcome** | K2 を性能等価性の証拠に限り因果帰属を主張しないのは適切。K3 は「負→INCONCLUSIVE→小さい→正」を並べて排他性に近付いた。しかし**網羅性がない**。たとえば AULC 同時区間 `[-0.02, +0.07]` は負でなく、±0.15を跨がず、±0.05に全包含もされず、§5 主ゲートを満たさない。この場合の outcome label がない。§3 の PRED-ONLY は v2 §3 の「獲得述語・第一階技能」より USE を狭めたが、比較階層への影響は説明されない。また §2 の型失敗 `INVALID action = no-op+課金` と、§6 の K4 `INVALID family = 隔離・run STOP` は同名で発生条件・分母上の意味が異なるため、イベント種別を区別する必要がある。 |
| **B6: CAL と EVAL の分離・封印・改訂履歴** | **PARTIAL** | **§6 ログ/manifest/アクセス**, **§7** | SHA-256、role_read_paths、generator/distribution/split/analysis digest、family INVALID + run STOP、および Owner の4段階決定表は明確化した。一方、§7 は数値候補の改訂を **CAL プロトコル承認まで** に限定するが、**存続する v2 §5 の「校正で一度だけ閾値改訂」および v2 §7 の「校正による文書改訂1回」**との整合が取れない（§0.1 は v2 §5 の AULC 定義と §7 の K0 停止条項のみを置換）。CAL 後に SD/discordance から算出する `n_required` と route を「新たな数値確定」とみなすかも未整理。CAL 用の `support 全件 oracle` の読み取り範囲と holdout 封印、manifest の必須型・具体的 read path は未完成。 |

### B4: 「積が同時検出力の下限」の数学的反例（論証用であり実験ではない）

3つのゲートがそれぞれ確率0.9で成功するとする。3つの失敗イベントが互いに排反で各確率0.1なら、3ゲート同時成功の確率は `1−3×0.1=0.7`。各成功確率の積 `0.9³=0.729` **より小さい**。従って `P(A∩B∩C) ≥ P(A)P(B)P(C)` は独立性等を仮定しなければ成立しない。一般の安全な下界は `P(∩ A_i) ≥ max(0, 1−Σ_i(1−P(A_i)))`（union bound）。設計依存の joint simulation/再抽出等で同時検出力を直接評価する方法もあるが、独立性のない「積」を保証として使ったまま STATISTICAL route を認めることはできない。

### B2: E と FULL の閉包を分けて監査すべき条件

`R_E` を経験なしで E が構築/列挙できる AST、`R_FULL(h)` を経験履歴 `h` から FULL が構築/USE できる AST とする。現行の「経験由来の記号でのみスロット充填」は `R_FULL(h)` を履歴に依存させる。他方 `E` は空 snapshot と宣言する。`R_E=R_FULL(h)` をすべての `h` で主張するなら、(a) E が経験なしで **同じ型付き候補の純構文列挙**を行うか、(b) 比較を履歴固定の共有候補空間へ再定義するかを選び、隠れた正解/経験情報の先渡しにならないことを明記しなければならない。同じ constructor 名だけでは集合の同値性は証明できない。

## 2. §0.1 を除外したときの新規/残存不整合

ここでは **§0.1 が明示置換した v2 §1 初期長、§2 デモ課金/tag/分母、§4 node 4種、§5 AULC 定義、§6 iid 単位、§7 K0 停止、§10 手続き**を意図的改訂として再列挙しない。下記は改訂版**内部**または**非置換** v2 条項との不一致である。

| 指摘 | 位置 | 不整合・残る判断 |
|---|---|---|
| **N1（内部・中心的）** | 改訂 §2 E / §3 H+, FULL, PRED-ONLY | 空 snapshot の E と「経験由来記号でのみ BRANCH 充填」は候補集合同値を保証しない。H+ の能力と経験制約を文法の**構文能力/学習後の実用能力**に分ける。 |
| **N2（内部）** | 改訂 §3 FIXED-IF | `構築なし` と「FULL と同じ述語発見」を一つの権限・constructor 許容表に落とせない。完成スキーマの供与と別途述語の発見を明示的に区別する。 |
| **N3（内部・数学）** | 改訂 §5 | AND 同時検出力の積下界は数学的に不正確。PPS 包含確率/加重推定/分散法の不整合も解消要。 |
| **N4（内部）** | 改訂 §6 outcome / §5 gate | 「負でも INCONCLUSIVE でも小でもないが主ゲート不達」という結果のラベルが未定義。正/非達成/不確精の網羅的分割を要する。 |
| **N5（内部）** | 改訂 §2 INVALID action / §4 分母 / §6 K4 INVALID | 型失敗の課金 no-op と、汚染による family invalid/run STOP が同じ `INVALID` 名で異なる結果遷移を持つ。混同すると分母、再実行禁止、STOP が変わる。 |
| **N6（v2 非置換・明示衝突）** | v2 **§5 閾値改訂** / v2 **§7 校正後文書改訂** 対 改訂 **§7** | v2 は CAL での1回改訂を許し、改訂版は CAL 前の承認段階までに候補を固定する。§0.1 の置換列挙が狭すぎる。どちらが正なのか本文に明記する。 |
| **N7（v2 非置換・規定不足）** | v2 **§1 行動全列挙要求** / 改訂 **§1** | 「v2 §1 の列挙を存続」は既存列挙表の参照ではなく、実際には全列挙**する予定**という文である。境界・停止・INVALID no-op の機械可読定義が未完成。 |
| **N8（v2 非置換・帰属衝突）** | v2 **§3 PRED-ONLY** / 改訂 **§3** | v2 は獲得述語/第一階技能・マクロまでを許容、改訂版は COMPARE を順位特徴に限定して制御流への使用を禁ずる。述語使用と第一階スキルへの影響を明示するか置換を宣言する。 |
| **N9（運用上の不一致）** | 改訂 §4 長さ表 / v2 **§5 G2 校正** | 改訂表の CAL は初期長4〜12だけだが、存続 v2 §5 は CAL で長13〜16 の G2 類型を列挙する。CAL 中の工学的 G2 容量診断が例外であることを明記する。 |
| **N10（内部・結果流）** | 改訂 §4 分母 / §6 K0-b・K4 | 生成後に識別不能と判定した family を「失敗または K4 INVALID」で主分母へ残す一方、K0-b の識別不能は「family 不採用・本実験 GO 不可」。CAL 診断と EVAL 結果の境界、識別不能を K4 汚染と呼べる条件を分ける。 |
| **N11（封印条件）** | 改訂 §6 K0-c / §6 manifest・access / §7 | K0 は CAL 限定だが oracle AULC は生成器 support「全件」列挙。評価 split/holdout の実体に触れない抽象 support 列挙なのか、sealed law/target を読むことになるのかを特定する。 |

N7〜N11 は一部が明文矛盾ではなく、第三者判定が分岐する**未定義・運用上の不整合**である。明示的な置換済み C1〜C6 を二重計上しない。

## 3. 設計合意の可否・次のゲート

**判定: 設計合意未成立／「Owner の CAL プロトコル承認だけが残る状態」には未達。** 改訂版 §0.2 の全項目を網羅したという対応表は、本文の正しさと完全性を保証しない。Owner が監督者回答を採用したことや、数値が候補であることを再審議しているのではない。

残作業は **(i)** §1 の law 依存情報が EVAL の行動選択前に公開される条件を確定、**(ii)** §2/§3 E/H+/FULL/贈与の到達集合・権限を同一文法で定義、**(iii)** §5 PPS 推定・誤差/同時検出力・route を数学的に修復、**(iv)** §6 結果ラベルの網羅性と INVALID 種別を定義、**(v)** §0.1 と非置換 v2 の改訂時点などを整合させること。その後の exact-head Lead 再判定が必要であり、**CAL プロトコルの承認可否は Owner が改めて判断する**。実施 GO、凍結、実装、評価はそれぞれ別の段階である。

逆質問は [WORLD-PREREG-RQ4-20261110-04](WORLD-PREREG-RQ4-20261110-04-revision-blockers.md) に分離した。数値の未凍結、標本データ未収集、CI/実験未実施それ自体を研究結果の否定に流用しない。

## 4. 確認と不実施

参照した GitHub 版の docs・コメントを読み、定義と数式の論理的一貫性を査読した。反例は紙上の確率計算であり、CAL/模擬実験/採点・コード実行ではない。文書の「機械可読」という名称だけでは serializer、状態機械、全 AST、生成表が存在することを意味しない。本文は正式な結果・追加権限を一切主張しない。
