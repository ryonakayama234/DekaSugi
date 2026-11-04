# R2-M-PAPER — 後継方法v2・単一方法文書案（W-A3-AFF）

id: R2-M-20261104-SINGLE-METHOD-V2-PROPOSAL
status: proposed_successor_method / pending_independent_claude_review / pending_owner_adoption / docs_only / no_implementation / no_experiment / no_scoring
updated: 2026-11-04
tags: gate-r2-m-paper, method-v2, successor, affine-identification, effective-h0, causal-use, comparator-manifest, stop

> **権限・正本:** [PR #173 のOwner決定コメント](https://github.com/ryonakayama234/DekaSugi/pull/173#issuecomment-6632141518)を本起草の正本とする。Ownerが採用したのは**R2-M-PAPERという紙上設計ゲート**だけであり、**本方法v2案は未採用**。Claudeの独立精査およびOwnerの別途「方法v2採用」決定が出るまで、[PR #170の凍結単一R0方法v1](https://github.com/ryonakayama234/DekaSugi/blob/docs/q-20261104-01-external-diagnosis/docs/research/GATE-R0-20261104-single-method.md)が唯一の有効な方法正本である。本書はv1を上書き・遡及改訂しない。R2-M-ENG、実験、学習、科学採点、sealed/heldout再実行、過去の成果再分類、mainや旧PRの変更は禁止。

**由来（優先順位順）:** 上記Owner決定 → [Research Lead QR1〜QR8回答・`9方法改訂項目](https://github.com/ryonakayama234/DekaSugi/pull/173) → [Claude独立精査（条件2件）](https://github.com/ryonakayama234/DekaSugi/blob/docs/diag-r-20261104-05-nextgate-response/docs/research/R-20261104-06-muse-review.md) → 凍結v1の定義・STOP。矛盾するときOwner決定を優先し、本案の独断で既存の研究結果を更新しない。

## 0. Scope / 研究対象と採用境界

- **唯一の主ルート:** W-A（入力域拡大＋合法照会予算）の`1〜`8に定める3bit・有限affine族。W-B（容量・圧縮）、W-C（後続合成再利用・独立family転移）はHOLD、W-D（費用差のみ）はU系列の別課題。いずれも本ゲートで起動しない。
- **問い:** 人間が**事前に与えた**識別可能な族の中で、公開証拠から作った型付きbodyを外部化し、freshな未公開入力に使用した際、同一Snapshot・全合法fallback保持のbody ON/OFF介入が予測または合法行動を変えるか。主張の第一上限は`6の`M_useである。
- **継承:** v1の公開/私的境界、独立validator、Sleep-liteの意味保存、immutable Snapshot、予測事前commit、N/S/R/E診断、M_use/M_gap/N_rep/U/T分離、費用台帳、INVALID/STOP、Owner許可の分離を継承する。3bitへ移す内容はすべて**新たな後継方法候補**であり、v1の範囲内だと扱わない。
- **R1-ENGの既知結果:** [PR #171](https://github.com/ryonakayama234/DekaSugi/pull/171)は2bitのRケースで全4点を公開し、合法episodic lookupが全点再現、ON/OFF予測・合法行動差0で`M_use未認定。M_gap/N_rep/U/TはNOT_EVALUATED。本書はこの陰性を否定しない。[#166](https://github.com/ryonakayama234/DekaSugi/issues/166)のSTOPも維持。
- **提案版の拘束:** 本文の`3「R2-M-CONTROLS-v2.0」および`4「R2-M-CLOSURE-v2.0」は**方法そのものの固定された候補契約**であり、law/結果を見た後に実験単位で差し替えない。査読中の改訂は差分を可視化し、Ownerによる方法版・scopeの再承認が必要。提出・CI合格・紙上説明はいずれも方法採用を意味しない。

## 1. Domain/v2 — 3bit世界、公開4/8・private 4/8

| 項目 | 固定する後継契約 |
|---|---|
| 世界 | X={0,1}³、入力順(x,y,z)、Y={0,1}、決定的f:X→Y。公開点・私的答えの出所は別に保管 |
| 法則族 | `F_aff = { f_(a,b,c,d)(x,y,z) = (a∧x) XOR (b∧y) XOR (c∧z) XOR d : a,b,c,d∈{0,1} }、16法則。係数はEvaluatorが選び学習者には非公開 |
| 初期公開P | 000,100,010 に対する3個のラベル、学習者へ提示。各入力・出力は合法な公開観測として記録 |
| 追加合法照会 | Q001の1種類のみ、paid inquiry budget B_Q=1、**照会前commit**、応答はUSE最終決定前に到着。方策は固定であり学習済みActive Learningと呼ばない |
| 公開後のsplit | public P∪{001}={000,100,010,001}（4/8）。private USE inputs={011,101,110,111}（4/8）、**ラベルはEvaluatorのみ**が保持。過去に回答が公開された点をprivate未見点に再分類しない |
| 資格/順序 | source family、split、law抽選規則、法則のprior、合法Qと回答期限、arm/予算/記録schemaを**対象結果前**に版・digest・保管者つきで固定。個別law/seed/非公開正答/heldout成果はpublic APIへ渡さない |
| 本稿の例 | PR #173で既に公開したparity3真理値表は**紙上説明専用**。この既知targetを後日の独立sealed確認として再利用禁止。confirmatory sourceは将来別許可による新しいsource-first custodyを要する |

公開APIが返すのは合法行動集合とdigest、初期公開点、支払済みQ応答、到着時刻・費用だけ。source→public gateway→learner→public-only validatorを片方向にする。Evaluator-onlyの法則・private labels・family drawをlearner、合成器、Snapshot、対照、公開validatorへ注入したら`7のINVALID。splitの**入力集合**の固定と、そこに対応する**答え**の秘匿は別事項である。

## 2. Hypothesis/v2 & Identification/v2 — 族制限の構成を明示選択

### 2.1. 合成器の二者択一 — 本v2の選択は「(a) 族制限の係数復号」

Claude条件1に従い、本案では**(a) F_affに制限した構成＝公開4回答からの係数復号**を**唯一の合成器契約**として選ぶ。(b)「署名pruningつき列挙＋明示的選択規則」は本版では**不採用**。一致した最初のASTを暗黙に採用する実装は禁止。

- 識別に使うhypothesis familyはF_affの16関数**のみ**。`r000,r100,r010,r001 が取得されたら、`d=r000, a=r100 XOR r000, b=r010 XOR r000, c=r001 XOR r000 を一度計算し、**この一意な係数組**からbodyを構成する。収束しない/合法Q未完了時にはbodyを構成しない。
- F_affという帰納バイアス、係数復号アルゴリズム、実行時選択/compile規則は**実験者が与えた体系の一部**であり全armに同じように開示する。事前に学習した係数やtarget bodyを与えてはならない。
- bodyを表す型付き木ASTの構成子は定数0/1、変数x/y/z、純粋なNOT/AND/ORのみ。XORを新規に発明したことにはしない。`XOR(A,B)=OR(AND(A,NOT(B)),AND(NOT(A),B)) は**人間が提供する決定的なコンパイル規則**。係数1の変数をx→y→z順に左結合してこの規則で展開し、空列なら0、係数d=1なら最後にNOTする。候補の並び替えや秘密のtieはない。
- ASTは**木（共有DAGではない）**として展開し、`max_ast_nodes_static=32`を固定する。3変数parityは最大25ノード、出力反転のNOT込みでも26ノードなので上限内。構成関数の意味・型・サイズは公開データだけを使う独立interpreterが再検査する。public4点不一致または上限超過なら`VALIDATION_FAILED`、別候補に恣意的に切り替えない。
- 探索契約は`decoder_invocations=1`、`family_size=16`、`candidate_budget=16`（停止しても残りを隠さない）。候補列挙方式に置換せず、候補生成0/1個と16法則の事前開示を別記する。STATIC-H+にも**同じdecoder・構築規則・候補容量**を認める。

### 2.2. 初期H0と実効H0は異なる

`H0_object/v2={0,1,x,NOT x,y,NOT y,z,NOT z}`の8述語を紙上診断の限定ライブラリとする。各述語は3bit全8点の単項/定数関数。これは`H0_effective(B)`の証明**ではない**。

`H0_effective(B)`は当該評価時点の**固定dispatchから、評価時に新しい永続bodyを構成せずに合法に到達できる**初期システム全体の方策閉包。初期macro、全合法episodic lookup、既存Kernel分岐、rank/policy、学習・検索・状態更新・履歴依存、既存の近傍・一般化・テンプレート・affine推定、時間/メモリ/候補予算と合法Qの組合せを、**利用可能ならすべて**含める。既存dispatchが評価時合成を内包するなら、その経路も隠さず実効閉包監査に記載し、`M_gap`判定を再審査する。STATIC-H+の評価時非永続合成は別armとして必須だが、OFFで実際に到達可能な経路を「別armだから」と削ることは不可。

**重要な差:** F_aff/decoderの仕様を全armへ**知識として開示**することと、個々のarmにそのdecoderが**実行時に接続済み**であることは別。最初からOFFの固定dispatchにもdecoder経路があるならOFFに保持する。body差を製造する目的でその経路を切断した比較はINVALID。同時にSTATIC-H+は同能力の非永続化による参照上限として別記録する。

### 2.3. 条件付き識別証明・非識別反例

公開4点の応答ベクトルを`(r000,r100,r010,r001)`とする。`(d,a,b,c)`への変換はGF(2)上で可逆（設計行列rank=4）なので、**F_aff内の16法則はいずれも4点から一意に識別**され、private4点を未公開に保てる。非affineを含む全Boolean関数なら2^8=256通り、公開4点固定後も残り4点に`2^4=16`通りの完成があるため**無制限H+には一意性なし**。F_affという仮定の効果を「探索器が構造を発明した」と言い換えない。

- **N/UNIDENTIFIABLE:** Q001が禁止、期限超過、予算不足、F_aff前提が不成立、または公開version-spaceが複数残る場合。例えばQ001なしではcの二値が合法P上で一致しz=1で割れる。
- **S/SUFFICIENT_H0:** 公開履歴に既存の8述語が整合していれば表現修復の必要性を主張しない。作ったbodyが既存macroと同義ならN_repは再発見候補。
- **R/MISMATCH_CANDIDATE:** 8述語が公開4点に不整合で、F_aff内で一意な構成bodyがpublic validatorを通る場合。ただし`H0_object`の限定下界であり`M_gap`の証明ではない。
- **E/SEARCH_INCOMPLETE:** 予め固定した合法な探索/構築の予算上限に達して完全性がない場合。探索不足を表現不足へ偽装しない。

紙上例`f=x XOR y XOR z`は公開応答`(0,1,1,1)`、privateの`011→0,101→0,110→0,111→1`。8個の`H0_object`の全域誤りは各4/8であり限定的な`G_object`の証人である。**例そのものは既知・公開済みで科学的未知入力試験には使用しない。**

## 3. Arms/v2 — 固定対照マニフェスト R2-M-CONTROLS-v2.0

**本節のarm集合・容量・tie・費用の計数規則は方法版の一部として凍結候補にする。結果や想定差を見た後の除外、容量削減、順序/tie変更、費用再定義は`INVALID`。** この表は許可された実行一覧ではなく、後に必要となる比較設計の**仕様**である。

| Arm ID | body / policy | 入力情報と許容量 | 目的と認定境界 |
|---|---|---|---|
| F00 (BODY OFF / FIXED) | learned bodyだけOFF、固定policy | **同一immutable Snapshot**、同じpublic4、全合法nonbody fallback、同じB。既存entryは削除しない | F10との差でM_useを調べる。人為ABSTAINは禁止 |
| F10 (BODY ON / FIXED) | 同じ固定policyでlearned bodyのみ有効 | F00と同じSnapshot・public・B。取得bodyの実dispatchを証明 | `D_use=F10−F00`の機構介入。経路差のみは不合格 |
| F01 (BODY OFF / LEARNED POLICY) | body OFF、学習policy/rankのみを別管理 | F00と同じ情報/総学習予算。policyの事前由来を記録 | rank/policyだけで差を説明できるか。未起動ならNOT_EVALUATED |
| F11 (BODY ON / LEARNED POLICY) | body ON、F01と同じ学習policy | F01と同じ情報/予算・body以外同条件 | F11−F01とF10−F00の混同禁止。未起動ならNOT_EVALUATED |
| STATIC-H+ | persistent learned bodyなし、USE時に同じF_aff decoderで構成 | 公開4点、16法則、同型AST最大32、候補予算16、同一合法Q/資源 | 保存せず同能力を実現する強対照。等成績でもM_useは理論上可能、能力新規性/Uは別 |
| FIXED-MACRO | **事前**に16法則すべての同型bodyを固定ライブラリ登録 | **sourceの個別targetに応じた選別注入なし**。公開4点でindex選択。同じ資源を記帳 | 人間提供済みの同機能・再発見/由来効果を検査。初期ライブラリ比較でN_rep判断 |
| EPISODIC-EXACT | 同じ公開履歴のキー完全一致照会 | public全件保持、容量上限は8点（世界全域）。現段階では4件、**人工的な削減なし**。未公開点はnext fallback/ABSTAIN | 単純暗記の能力。未見キーの不在だけをM_use以外の成功根拠にしない |
| NEAREST-1NN | learned bodyなし、Hamming最近傍 | 公開全件（現時点4、最大8）、等距離多数決、同数ならABSTAIN | 最低限の合法な一般化対照。初期dispatch実装済みならOFFにも必ず含む |
| STUMP-1 | learned bodyなし、1変数の2分岐または定数 | 候補は`[0,1]`＋各変数x,y,zの出力対`(00,01,10,11)`＝14列挙枠。公開誤り最小を選択 | 条件付き初歩一般化の対照。初期dispatch実装済みならOFFにも必ず含む |
| ORACLE-REF | evaluator-only、学習者呼出不可 | 真のlaw/private labelsで計算する理論上限 | 勝敗条件・public fallbackではない。非公開情報を漏らしたらINVALID |

**固定dispatch/tie規則（提案版）:** F00/F10の基底fixed policyは、ONの有効で検証済みbodyを優先し、該当bodyがない/許可されないとき`exact-key episodic → 公開履歴全点に整合するH0_object（順序0,1,x,!x,y,!y,z,!z） → 事前に存在するその他の全合法Kernel/メモリ/一般化経路（`4マニフェスト列挙順） → ABSTAIN`。OFFは**learned body呼出だけ**を無効にし、他経路の権限/記憶/容量/予算を減らさない。宣言外の隠れ経路が見つかったらこの単純な図を優先させず`4へ戻す。

NEAREST-1NNはHamming距離の**全ての最短距離同点**を投票し、賛否同数はABSTAIN（入力順で私的targetを選別しない）。STUMP-1は公開点0-1誤り最小、同点は列挙順`constant0,constant1,x:(00,01,10,11),y:(00,01,10,11),z:(00,01,10,11)`を選ぶ。fixed macroは常に16個全部を持ち、公開係数のindexで選ぶ。各tie規則は全armで事前固定。F01/F11でpolicy学習の仕様・容量をこの版に完全固定できない場合、両armを`NOT_EVALUATED`とし、結果後に有利な学習方策を追加してM_useの証拠に混ぜない。別Owner許可と後継版が必要。

**予算・容量（同種の操作には同一会計）:** `B_Q=1 paid Q(001)`、`B_public=4 observations`、`B_lookup_capacity=8 exact records`、`B_family=16`、`B_ast_static=32 nodes`、`B_candidate=16`、`B_H0_scan=8 predicates`、STATICとlearnerのdecoder起動は各最大1回の独立したコスト計上（ON側の学習時とSTATIC側のUSE時で**時点を明記**）。同じ源泉から学んでいないpolicy armは学習予算と容量の適合証拠が無い限り比較対象として陽性採点しない。CPU/wall/RSSは`5の固定単位で**実測記帳**し、timeoutを事後変更しない。後日の科学比較の実行上限・閾値・sourceは別の事前凍結とOwner許可が必要で、本提案だけでは確定済みの実験設計と称さない。

## 4. Closure/v2 — H0_effective(B)完全列挙またはUNKNOWN様式

**様式ID: R2-M-CLOSURE-v2.0（対象の結果前に固定すること）。** 以下は空欄を秘匿してよいという意味ではない。全合法経路が照合できるまで`M_gap=UNKNOWN`である。`H0_object=8`だけを`H0_effective`の証明と偽らない。

~~~yaml
closure_manifest_version: R2-M-CLOSURE-v2.0
method_version: R2-M-20261104-SINGLE-METHOD-V2-PROPOSAL
status: UNKNOWN  # COMPLETE または UNKNOWN; 初期値はUNKNOWN
freeze_before: source_target_and_use_outcomes
source_family_public: F_aff_3bit_16
split_public_inputs: [000, 100, 010, 001]
split_private_inputs: [011, 101, 110, 111]
public_access: "P=3 free; Q001=1 paid; response before USE"
budget: {paid_q: 1, lookup_entries_max: 8, h0_predicates: 8, ast_nodes_static: 32, candidate_max: 16}
inventory:
  - {route: episodic_exact, version: TBD, capacity: 8, include_in_body_off: true}
  - {route: h0_eight_predicates, version: TBD, capacity: 8, include_in_body_off: true}
  - {route: kernel_dispatch_and_conditionals, version: TBD, capacity: UNKNOWN, include_in_body_off: true}
  - {route: ranking_policy_history_learning, version: TBD, capacity: UNKNOWN, include_in_body_off: true}
  - {route: existing_generalizers_and_templates, version: TBD, capacity: UNKNOWN, include_in_body_off: true}
  - {route: initial_macro_library, version: TBD, capacity: UNKNOWN, include_in_body_off: true}
  - {route: runtime_compilation_if_routable, version: TBD, capacity: UNKNOWN, include_in_body_off: true}
enumeration:
  public_history_equivalence_classes: UNKNOWN
  allowed_transition_rules_digest: UNKNOWN
  all_legal_policies_or_complete_proof_digest: UNKNOWN
  best_off_fallback_loss_bound: UNKNOWN
  closure_complete: false
  unknown_reason: "3bit初期コード/dispatchは未実装・未監査; 実効閉包は未列挙"
custody:
  pre_target_commit_sha256: TBD
  frozen_registry_and_dispatch_sha256: TBD
  reviewer: TBD
  owner_acceptance: PENDING
claim: {m_use: NOT_CERTIFIED, m_gap: UNKNOWN, n_rep: NOT_EVALUATED, u: NOT_EVALUATED, t: NOT_EVALUATED}
~~~

**COMPLETEの必要条件:** 対象のprivate law/USE outcomeを見ないで、(1) 初期資産とhash・版、(2) 全合法historyと各route/dispatch/学習遷移、(3) 最大容量・同点・有限資源B、(4) 到達可能な予測/合法行動方策の完全列挙または等価な網羅証明、(5) best OFF fallbackとH+の同条件損失/非実現証人を独立監査し、source-firstの不変記録へcommitする。**不明なフィールドを空欄でCOMPLETEにしない。** 任意コード・未列挙Kernel・隠れたfallback・入出力依存の外部データ取得があるなら`UNKNOWN`とし、`M_gap`および実効表現修復の主張を停止。結果後に`COMPLETE`へ上書きして救済せず新たな方法審査へ戻す。

この`UNKNOWN`は**現時点での正直な宣言**であり、新実装・列挙・実験を実施したという意味ではない。`M_use`の介入設計を`M_gap`の未完成で不当に中止する必要はないが、OFFの合法性・同一性が監査不能なら`M_use`も保留する。

## 5. Execution/v2 — 時系列、記録契約、費用とR1-P2の扱い

**将来別承認されたときの手続案（現時点では一切実行しない）:**

1. **source-first:** 独立Evaluatorがpublic family、law選出方法、split、law/seed/private answersの隔離、全armの方法digest・識別条件・STOP・評価式をsealする。Learnerへ非公開情報を渡さない。PR #173のparity既知例は独立sealの材料にしない。
2. **公開照会:** Pを配布し、`Q001`の前に合法集合digest（集合・予算・有効時刻を含む）・照会選択・公開時点での予測をappend-onlyでprecommit／fsync。答えが来た後にpublic recordと支払費用を追記。非合法Q・遅延回答の先取りは禁止。
3. **構成・検証:** `2の係数復号を1回だけ実行して型付きASTを構成。別のpublic-only interpreterが型・32ノード以内・構成子・public4整合を確認。Sleep-liteはAND/ORの可換正規化など**意味保存のみ**。候補の実質的なlaw変更やprivate label利用禁止。
4. **immutable Snapshot:** parent digest、公開観測とprecommit、family/decoder/AST/compiler版、H0 registry・dispatch・policy・arm manifest/closure manifest hash、body・validator receipt・canonical digestを完全記録。排他的作成で上書き拒否、復元時schema/型/public consistency/hashを再照合。ローカルSHAは独立custodyや第三者時刻証明ではない。
5. **fresh USEとOFF:** source/heldout非依存の新プロセスで同じSnapshotから各armを復元。learned bodyのavailable/selected/executed/finishedと各fallbackの活動を**別字段**で記録。F10とF00はbodyだけ異なり、public history、fixed rank/policy、合法Q、残りB、entry容量、既存dispatchすべて同じ。private labelsの開示**前**に各armの`(prediction, legal_action)`とABSTAIN・trace digestを不可変commit。
6. **独立検査:** 全armのcommitを受理した後でのみEvaluatorが非公開正答と照合し、不可変receiptを独立custodyに記録する。無承認の実際の実行・スコア表生成は行わない。古い封印評価は再実行しない。

| Versioned record | 公開/私的情報・最小フィールド |
|---|---|
| PublicStep/v2 | episode,seq,point, legal_actions/`legal_digest`（現在の合法集合・残り予算・有効時刻のcanonical digest）、precommit/answer受領の順序・時刻、paid Q cost、public outcome。hidden law/target/seed/USE labelsなし |
| HypothesisCertificate/v2 | F_aff版・design rank、公開4点・識別結果、H0_object8個の限定列挙、`H0_effective(B)` COMPLETE/UNKNOWN・全経路証明、失敗/棄権の理由 |
| ConceptBody/v2 | 係数は公開からのみ計算、typed AST、32ノード境界、compiler版、候補数、public-only validator、依存/来歴、初期macro同値候補 |
| Snapshot/v2 | parent/grammar/H0/policy/decoder/manifest digest、canonical body、public journal digest、validator receipt、hash、immutable保存と復元検証 |
| UseTrace/v2 | fresh process、arm/ON-OFF、個別body/fallbackのavailable/selected/executed/finished、route、`prediction`、`legal_action`、`ABSTAIN`、事前commit、`ast_nodes_static`、`node_visits_runtime`、`primitive_ops_runtime`、cost |
| ScoreReceipt/v2 | **Evaluator-only** source/split/arm、outcome照合、使用した独立原本、計数費用、invalid/stop、全体digest chain。publicへ逆流させない |

**R1-ENG P2-1（メータ）の前方契約:** `ast_nodes_static`は木ASTに含まれる構文ノード総数で実行前に一度数える。`node_visits_runtime`は実際のinterpreterで評価・訪問したノードの累積値であり、AND/ORの短絡により静的数より小さくなり得る。`primitive_ops_runtime`は実際に実行したNOT/AND/ORの数とし、入力葉・literalは含めない。各USE invocationで記録する。静的3ノードORを実行時3訪問とみなす過大計上を禁止。AST生成費、validator回数、政策推論、復元は別に課金する。既存R1-ENGの過去実測値は変更しない。

**R1-ENG P2-2（パス）の前方契約:** Snapshotの`path`は作成時に`Path.resolve()`相当で絶対パスに正規化し、その同じ絶対パスだけをfresh子プロセスへ受け渡す。呼出元cwdと子プロセスcwdが異なっても同じバイト列を参照する。相対パス基準の曖昧さ、リポジトリ外の出力先での別ファイル誤読を許さず、復元直前のcanonical path・snapshot digestを独立照合。ここでは既存コードを修正しない。

**生涯費用と固定会計:** `C_life(n)=C_train+C_synthesis+C_sleep_lite+C_store+Σ(i=1..n)(C_inquiry_i+C_policy_i+C_use_i+C_verify_i+C_restore_i)`。STATIC-H+も使用時の再構成・validator費、FIXED-MACROも事前構築/保存費、EPISODIC/1NN/STUMPも記憶・検索・推論費を隠さず別台帳に計上する。Qは`1 paid action`、candidate数は**実際に生成・検証へ回した候補**、AST静的ノードは上記、実行訪問数とprimitiveは実測、CPUはprocess CPU秒、wallは単調時計秒、peak RSSはbytes、保存/復元量はbytes、validator呼出は回数と各CPU費。これら**異種単位の事後加重和は禁止**。n・換算式・成功/ABSTAIN効用・CPU/メモリ実行上限・事前の許容閾値は独立科学評価のsource-first lock/Owner許可がない限り決めた/測ったと主張しない。

## 6. Claims/v2 — 認定上限と必須開示定型

**`D_use(u)=1[(prediction,legal_action)_ON ≠ (prediction,legal_action)_OFF]`** をfresh private USE点`u`ごとに、同一Snapshot・公開履歴・固定policy・全合法fallback保持・同予算・結果前commitの下で定義する。経路名が違うだけで`D_use=1`と数えない。

| ラベル | この方法案が将来要求する証拠 | 現時点の状態 |
|---|---|---|
| `M_use` | target注入のないpublic-only構成→独立検証→immutable外部化→fresh dispatchと`D_use`非ゼロ。OFFの全合法fallbackを保証。漏洩監査と同一性を要求 | **NOT_CERTIFIED**（紙上案であり未実施） |
| `M_gap` | `M_use`に加え、対象前に完全に凍結した`H0_effective(B)`の非実現証明、合法な最良OFFと同情報・同資源H+の実効差。閉包不明ならUNKNOWN | **UNKNOWN / NOT_CERTIFIED** |
| `N_rep` | 初期Library/macroに実在する全bodyとcanonical・8点外延・事前固定の記述長/生成能力を照合。意味同値なら再発見 | **NOT_EVALUATED** |
| `U` | STATIC-H+/FIXED-MACRO/EPISODIC/1NN/STUMP/方策のみ等の同情報・同容量対照、事前指定nと生涯総費用・性能/ABSTAINの独立比較 | **NOT_EVALUATED** |
| `T` | **上流生成機構で独立した**familyのgroup split、事前登録、未知familyでの再利用差。3bitのrole/seed変更は独立familyではない | **NOT_EVALUATED** |

**主張文の必須定型（将来、結果が成立した場合も変更不可）:**

> 「本結果は、実験者が事前に提供して全armに開示した`F_aff`（3bit affine Booleanの16法則）・係数復号・ASTコンパイル/選択規則という帰納バイアスの**範囲内**で、合法公開4/8点から関数を識別し、型付きbodyを外部化・保存し、同一Snapshotの全合法fallback保持BODY OFF介入と比較してそのbodyの**因果的使用**を検査したものである。事前に与えた族の内部での**識別＋外部化＋因果的使用**（成立する場合に限り`M_use`）より強いことは示さない。未知の概念/新しいXOR意味論/族そのものの発明、一般的な新能力、`M_gap`、`N_rep`、`U`、`T`または独立family転移は、各々の別の証拠なしには主張しない。STATIC-H+や既存fallbackが同成績ならその事実を併記する。」

**推論禁止:** STATIC-H+がONと同成績でも、合法OFFとの差が検証されれば`M_use`だけは成立し得るが、実用的新能力や総費用改善の証明にはならない。合法OFFが同一予測/合法行動を返せば`M_use`不成立。初期macroとbodyが同義なら`N_rep`は再発見。単純H0_objectの負例だけで`M_gap`陽性化しない。

## 7. STOP / INVALID / REDESIGN — 診断順と無許可行為

判定は**INVALID優先**。漏洩、結果後のsource・family・split・body・対照manifest・容量・tie・費用変更、違法Q、事前commit欠落、Snapshot上書き、非独立validator、private答え逆流、独立custody破綻は影響比較を直ちに`INVALID`隔離し、陽性・陰性・NULLの分母に混ぜず、Owner新承認なしの再試行禁止。

次に`UNIDENTIFIABLE`（合法証拠/期限でF_aff version-spaceが一意にならない）、`SEARCH_INCOMPLETE`（所定Bの構築・列挙が完了していない）、`SUFFICIENT_H0`（初期法則で説明できる）、`MISMATCH_CANDIDATE`（限定H0不整合で候補生成可能、実効gapは別）、`VALIDATION_FAILED`（型/公開整合の不合格）を区別。`M_use`のON/OFF差が全private USEで0なら`NOT_CERTIFIED`、route差のみやOFF強制ABSTAINも不合格。単純/強い合法fallbackが全private点を再現したら**そのまま陰性・不認定として記録し弱体化しない**。`H0_effective(B)`閉包UNKNOWNなら`M_gap=UNKNOWN`、完全証明で`G_effective(B)=0`ならその対象の`M_gap STOP`。実行予算不足は能力の非表現可能性と読み替えない。

R2-M-PAPERで閉包・識別・公平性の前提が成立しないと判明すれば、独立査読は**REDESIGN/STOP**をOwnerへ勧告し、許可範囲を広げずに方法案を戻す。W-B/W-C/U、表現修復、独立family転移へ**この不成立を陽性として転換しない**。過去の[#166](https://github.com/ryonakayama234/DekaSugi/issues/166) STOP、v1の結果・凍結、旧sealed資産を保全。

## 8. Gate出口・Owner決定と別研究ポインタ

**R2-M-PAPER（このDraft PRでの提出範囲）は** (1) Domain/Hypothesis/Identification/Arms/Claims/Executionの単一後継方法全文、(2) `4の閉包マニフェスト/UNKNOWN様式、(3) `6の族事前仮定・認定上限定型、(4) **別研究軸へのポインタのみ**、(5) `2.1の合成器二者択一固定、(6) `3の対照版凍結、(7) `5のR1-P2記録契約、が**文書内に存在すること**まで。内容の採否はClaude精査→Ownerによる明示方法v2採用/REDESIGN/STOPに委ねる。

**表現修復（別研究軸、非起動）:** 「族の不十分さを検出する→予測誤差から新たな述語/操作表現を提案する→独立に検証する」は、[PR #173回答`9/`10](https://github.com/ryonakayama234/DekaSugi/pull/173)の将来研究ポインタにのみ置く。本方法では`F_aff`自体の獲得や修正を評価しない。W-B（圧縮）・W-C（合成転移）とともに、並行研究や新Issue起動は許可しない。

| 決定項目 | 本提出時の扱い |
|---|---|
| R2-M-PAPERの採用 | **Owner承認済み** — [PR #173の正本コメント](https://github.com/ryonakayama234/DekaSugi/pull/173#issuecomment-6632141518) |
| 後継方法v2の科学的方法としての採用 | **PENDING** — Claude独立精査→Owner別決定 |
| R2-M-ENGの実装scope/GO | **NOT_AUTHORIZED** — v2採用と別のOwner許可が必要 |
| 新しいsource-first実験・採点 | **NOT_AUTHORIZED** — 別途独立前登録・custody・Owner許可が必要 |
| PR #170/#172/#173・mainや過去資産の変更 | **対象外、禁止**。この新Draftはmergeしない |

**独立査読に求めるP0:** ①F_aff内rank=4と無制限H+非識別、②全armへの先験的バイアスの同等開示と固定dispatchの合法OFF、③`4のUNKNOWNを含む実効閉包の真正性、④`3対照manifestの容量・tie・費用の事前固定、⑤`M_useと`M_gap`の非混同、⑥`5のR1-P2を含む公開/私的境界と不変記録。P1はAST上限32、候補上限16、将来の実行上限・科学前登録・独立custodyの可行性。査読に合格してもOwnerの別採用・R2-M-ENG許可は自動的に発生しない。
