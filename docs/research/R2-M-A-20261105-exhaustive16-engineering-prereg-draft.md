# R2-M-A-20261105 — 全16法則・事前登録つき工学費用測定（A / 起草稿）

id: R2-M-A-20261105-EXHAUSTIVE16-ENGINEERING-PREREG
status: draft_for_independent_review / docs_only / not_frozen / no_execution / no_implementation / no_scoring
updated: 2026-11-05
tags: r2-m, preregistration-a, exhaustive-16, engineering-cost, route-audit, closure-unknown, owner-gate

> **権限状態:** [PR #180 のOwner決定](https://github.com/ryonakayama234/DekaSugi/pull/180#issuecomment-6658438738) が許可したのは、**Aの前登録文書の起草だけ**である。本文の数値、監査手順、閾値はすべて**凍結前の提案**。本Draftの作成・査読・CI通過は実行GO、科学実行GO、runner実装許可、source選定、順序seal、真のUSE採点、方法v2変更のいずれでもない。旧sealed/heldout、過去の陰性結果、凍結v1/R1には触れない。

## 1. Authority、研究質問、主張上限、原本の同定

### 1.1 根拠・決定の優先順位
- 設計根拠: [DIAG-R-20261105-06 / PR #180](https://github.com/ryonakayama234/DekaSugi/pull/180) のQS1–QS8（特にQS7の10章形式）。
- 独立精査: 同PRの **R-20261105-08**。修正1件（**12抽選を16法則網羅へ**）、注記2件（**監査対象commitを固定**、秘密を扱う将来登録では**payload/nonce二重保管**）を採用。
- 正本のOwner決定: [PR #180 Ownerコメント](https://github.com/ryonakayama234/DekaSugi/pull/180#issuecomment-6658438738)、OD1–OD9。
- 方法: [Owner採用済みR2-M method-v2（採用時commit）](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md) および [Stage 2](../specs/R2-M-ENG-STAGE2.md) / [Stage 3](../specs/R2-M-ENG-STAGE3.md)。**本書は方法・policyを改訂しない。**
- 本起草ブランチの基点: main commit \`b553658e098065f787d7ef2d24db14300ccaa9e9\`（**起草時のbase**であり、凍結された事前登録のSHAではない）。凍結原本のmain SHA、最終文書bytes SHA-256、外部登録IDは **TBD / NOT_FROZEN**。

### 1.2 事前登録する問い
**人間が定義した既知の有限F_aff（3-bit affine Boolean全16法則）において、現行の合法ON/OFF配線、復元、固定5対照とfresh-processを保持した場合、保存bodyの利用が経路・実行・保存/復元・生涯費用の各単位へどのような工学コストを生むか。16/16件を欠落なく記録できるか。**

機構整合性の事前予測は \`K=0\`（§7）であり、これは**配線/完全性の検査**、統計的な有意差検定でも新しい能力の発見でもない。F00には合法runtime affine decoderがあり、Snapshot復元自体も公開履歴から復号・検証を再実行する。公開4bitは係数の十分統計で、全16固定macroでも表現できる。AではM_use陽性を追わない。

**主張上限:** L0（既知族の識別）、L1（公開データによる構成）、L2（保存/復元の機械的再現）、L3（予測/合法行動の差がないことの当該配線検査）、L4（当該ハードウェア/実装での多次元費用）の**記述**まで。M_use \`NOT_CERTIFIED\`、M_gap \`UNKNOWN\`、N_rep/U/T \`NOT_EVALUATED\`を維持。新しい概念、未知familyへの転移、実効表現拡張、汎用知能、すべての合法OFF方策の非実現可能性は主張しない。

**Bは別のmethod版・別前登録・非恣意的USE制約の証人・別Owner許可が整うまでNO-GO。** Aの結果後にBの条件を後付け変更しない。F01/F11はNOT_EVALUATED、ORACLE-REFはevaluator-onlyであり子processのarmにしない。

## 2. Provenance・過去の陰性と除外の扱い

- 参照可能な工学証拠: R2-M-ENG [Stage 1（PR #176）](https://github.com/ryonakayama234/DekaSugi/pull/176)、[Stage 2（#177）](https://github.com/ryonakayama234/DekaSugi/pull/177)、[Stage 3（#178）](https://github.com/ryonakayama234/DekaSugi/pull/178)。これらは**人工fixture**であり、Aの費用実測や独立した科学USE結果ではない。
- 方法的な負例: R1-ENGの公開全点lookupによる因果差なし、OPPORTUNITY-001の64ペアで片側のみ正解0/UNDERIDENTIFIED、[#166](https://github.com/ryonakayama234/DekaSugi/issues/166)の機会ゼロSTOPを継承し、後から成功例として再分類しない。
- 既公開parity3等の既知lawは**工学的な全16網羅から除外しない**。ただしそれらを未見の独立source、秘密heldout、N_rep/T証拠と称しない。全法則の各結果を公開する。
- 歴史的sealed/heldoutは閲覧・再実行・再採点・転用しない。本書と新規工学ラン以外のデータを混ぜない。source結果を見て規則や閾値を変更する場合は§8の逸脱と再登録を要する。

## 3. Inventory・固定dispatch/restore・closure UNKNOWN

### 3.1 同一情報の可用性
各lawを \`f(x,y,z) = (a AND x) XOR (b AND y) XOR (c AND z) XOR d\`、係数 \`(a,b,c,d) ∈ {0,1}^4\` とする。law IDは \`abcd\` 4bit、**0000–1111を辞書順に全数網羅**する（これは実際の実行順序とは別）。

公開点 \`P=(000,100,010)\`（無償3件）と、事前commit後の有料 \`Q001\`（1件）を使用する。公開回答 \`r000,r100,r010,r001\` から \`d=r000, a=r100 XOR r000, b=r010 XOR r000, c=r001 XOR r000\`。USE対象は \`(011,101,110,111)\` の4点固定。公開4点のみでlawを一意に定められる。

### 3.2 残す経路・禁止改変
- \`F10\`: 検証済みpersistent body優先 → \`episodic_exact\` → \`h0_consistent\` → \`runtime_affine_decoder\` → ABSTAIN。
- \`F00\`: **同じSnapshotから同じ公開情報を復元**し、persistent bodyの呼出だけOFF。残りの全合法nonbody fallback（\`episodic_exact\` → \`h0_consistent\` → \`runtime_affine_decoder\`）をそのまま保持する。
- **重要:** 復元処理がpublic historyから係数復号/validatorを再実行することを**両armの費用に課金**する。dispatch上のdecoder削除・復元復号の隠蔽・片側の容量/履歴/予算削減は禁止。
- 5対照はF00/F10の新しいfallbackではなく**別arm**。学習資産の後付け追加、target別macro注入、私的正答の渡し込みは禁止。
- 両armで同じcanonical absolute Snapshot path・独立に固定したexpected bytes SHA256、同じmethod/policy/法則毎の公開記録・USE点・容量・tie規則・対象commitを使う。各子は別cwd、別fresh process、排他的trace出力。

### 3.3 監査契約（実行ゲートと認定ゲートを分離）
実行前の**必須**監査（P0）: 実行対象**exact commit SHA**に固定したimport graph、Snapshot生成/復元の再decoder/validator、全ての**実接続**route、fallback到達可能性、公開/私的境界、7arm同一入力/同一コスト規約、保管・事前commit・negative tests・記録schemaをResearch Leadが読み取り専用dossierにし、Museが同一commitを独立検査。単なる過去のENG受入で代用しない。未監査経路やOFF改変を発見したらSTOP（結果を見てから補修して続行しない）。

既存closure文書の \`UNKNOWN\` と、全合法history・最良OFF方策・同予算非実現証明（\`M_gap\`のための証明）の未完成を残す。実経路監査完了を \`H0_effective(B)=COMPLETE\` と読み替えない。

状態固定:
\`\`\`yaml
closure_status: UNKNOWN
closure_complete: false
effective_h0_reachability: UNKNOWN
best_off_fallback: NOT_CERTIFIED
m_gap: UNKNOWN
m_use: NOT_CERTIFIED
n_rep: NOT_EVALUATED
u: NOT_EVALUATED
t: NOT_EVALUATED
\`\`\`

## 4. Sourceの全数取り扱い、実行順序、custody、脅威モデル

**本Aに「秘密law抽選」は存在しない。** 有限16 lawを全件採用し、公開済み係数と真理値表の中で測る。既公開lawを除外しない。16-law全数であることと、独立な生成familyであることは異なる。選択の不確実性はないが、CPU/wall等の測定変動は残る。

**順序の提案（未実施）:** 実行の順序効果対策として、16法則の順序だけをsource/score結果を見る前にOwnerが一度決定・固定する（例えば16項の一様な順列）。使用する抽選器、seed生成方法、順列、manifest canonicalization、commit形式を**別Owner凍結時**に確定する。固定した全順列には16個が1回ずつ現れ、重複・欠落がないことを独立照合する。必要ならnonce付きcommitで順序だけ事前sealし、終了後revealする。**この起草では順列もseedもnonceも生成せず、sealもしない。** 順序を秘密法則の独立保管と混同しない。ランダム化が不可能なら先に辞書順を宣言し、方法変更として審査を受ける。

Ownerは順序manifest/実行receiptのcustodian候補、Museは方法・実経路・費用監査、Leadは公開側記録の用意を担当。実行者と監査者が同一証拠を自己認定しない。GitHubのcommit・SHA単体は外部timestamp・独立原本性の保証ではない。

**脅威モデル:** 後からlaw/順序/失敗試行を除外する選択、private USEの先見、snapshot/trace上書き、digest不一致、子へのsource注入、無制限の再試行、片側だけのdecoder禁止、計測コストの恣意的配賦、結果後の閾値変更を防ぐ。一方、既知16 lawである以上**秘密の意味論・独立未知sourceは保証しない**。Aで秘密payload/nonceの二重保管を要求する研究上の実益はないが、将来B等で秘密を扱う場合にはOwner管理の**2か所複製保管**を別登録に必須とする。

## 5. 公開/評価側分離、precommit、traceの時系列

提案する手順（**ここでは実施しない**）:
1. 固定済みmethod、順序manifest、runner exact head、7arm manifest、資源閾値、契約SHA、USE 4点を照合。各lawの公開3点だけを配布。
2. \`Q001\`を実行する**前**に、許可照会集合・残予算1・期限・public-history digest・問い合わせ点 \`001\` を書いた順序付きPublicStep precommitを排他的に記録し、その後に回答を受け取る。法則あたりQは1、再照会不可。
3. public4から法則係数とtyped ASTを構築し、公開情報だけを使う独立validatorに通す。Sleep-liteは意味保存のみ。canonical Snapshot/v2を一つ生成し、独立にexpected bytes SHAを固定する。書換禁止。
4. 各law×USE4点×7armについてfresh child（別cwd）を起動。子は唯一のcanonical Snapshot絶対パス・expected SHA・arm・入力点・排他的trace出力だけを受け取り、law係数、seed、USE真値、採点結果は受け取らない。採点対象の4点の**入力自体**は全armへ同じく渡す。
5. 全armの \`prediction\`（0/1/null）、\`legal_action\`（PREDICT/ABSTAIN）、route、activity \`available/selected/executed/finished\`、AST/CPU/wall/RSS/cost/receipt digestを検証。**評価側で正答と照合する前に**各出力のdigest/欠測/失敗をappend-only原本へcommitする。
6. 継続可否を§8で判定したうえで、評価側が既知lawの真値を計算・照合する。全件・失敗・INVALIDも消さずに公開。これは工学的なfixture照合であり、科学的なsealed heldout採点ではない。

学習側に渡す公開情報と、評価側に残す真値・正答照合・集計receiptをフィールドごとに分離する。対象コードとmanifestのdiffにより「公開LAWは知られている」ことと「子へ真値を注入していない」ことを独立検証する。source-firstの科学的秘密性を本Aに偽装しない。

## 6. Arm、同予算、費用の単位と会計境界

| Arm（計7） | 用途・必須仕様 | 禁止される有利化 |
|---|---|---|
| \`F00\` | learned body呼出のみOFF、全合法nonbody fallbackと復元再decoderを保持 | OFF専用のdecoder/履歴/容量削除 |
| \`F10\` | validated persisted body ON、同じSnapshot/復元/合法fallback | ONのみ情報/予算を追加 |
| \`STATIC-H+\` | public4からUSE時にaffineを再decoderし独立validatorを通す、AST≤32 | 再構築費・restore費を隠す |
| \`FIXED-MACRO\` | 16 entryをsource前に全部構築、public4から選択。module importの事前構築/保存量を記帳 | target-specific 1 entryのみ課金 |
| \`EPISODIC-EXACT\` | public全4件保持（容量上限8）、未見キーABSTAIN | 意図的な履歴削減 |
| \`NEAREST-1NN\` | public4全件、Hamming全最短点多数決、同票ABSTAIN | 最初の近傍を恣意選択 |
| \`STUMP-1\` | 固定14候補（定数2＋各x/y/zに4通り）、公開誤差最小、列挙順tie | 14枠と16 affine候補を混同 |

共通境界: \`B_Q=1\` paid query（Q001）、public observations \`=4\`、exact容量 \`≤8\`、affine family \`=16\`、static AST \`≤32 nodes\`、生成候補 \`≤16\`（**実候補数と上限は別**）、H0_object scan \`≤8\`。STUMPの14候補は別仮説族。合法fallbackをすべて維持し、異なるarm間の前払い負担も明示する。非対称な禁止操作を追加しない。

**費用ベクトル**（混合して一つの「点数」にしない）:
- \`paid_q\`（回）/公開観測数（件）、decoder呼出（回、**learn/restore/use別**）、validator呼出（回・CPU秒）、実際の候補生成・検証数（件）、H0比較/走査（回）、fallback routeとABSTAIN（件）。
- \`ast_nodes_static\`（ノード/木）、\`node_visits_runtime\`（実訪問回数）、\`primitive_ops_runtime\`（実際に実行したNOT/AND/OR回数）。短絡未訪問ノードやleaf/literalをprimitiveに数えない。各USE呼出に対する値を残す。
- process CPU（秒）、単調時計wall（秒）、process peak RSS（bytes）、Snapshot保存・復元・固定macro構築・保持・trace bytes（bytes）、fresh childの起動費（秒）、train/synthesis/Sleep-lite/store/restore/dispatch/verify各費（対応する単位）。

**異種単位の後付け加重和は禁止。** FIXED-MACROの全16カタログ準備のCPU/wall/保持bytesと、STATICのUSE時再decoder、F00/F10の復元時再decoderを漏らさない。processごとのimport課金と一度だけの準備費を二重加算しないため、\`per_fresh_process\` と \`one_off_preparation\` を別列にし、再利用を仮定するモデルならその仮定と配賦を全armに同じ規約で適用する。どれかが独立計測できない場合は \`UNMEASURED\` として当該生涯比較を保留し、零と置かない。

## 7. Episode、全数算術、数値閾値、解析式

### 7.1 全数設計（提案、科学実行ではない）
- Law/episode: **16/16**（同一F_affの16係数組）。各lawにつきpublic P=3、paid Q=1、private-style USE入力4。USE点は同じlaw内の**下位測定**であり独立familyではない。
- 全体: 初期公開P **48件**、paid Q **16件**、公開P+Q **64件**、USE入力 **16×4=64 law-point**、7armで **16×4×7=448 fresh subprocess / trace**。1 lawは **28 child**。F00対F10は **64 paired points**、法則単位 \`N_law=16\`。USE64を独立な法則・独立familyの64サンプルと呼ばない。真の独立familyの \`N_rep_family=NOT_EVALUATED\`。
- 7armの4点版runner、科学用記録/custody、CPU/wall/RSSの確定計測は**現行Stage 3の1点fixtureでは未実装**。別権限の実装・exact-headレビューなしに走らせない。

### 7.2 配線・完全性指標（仮説検定ではない）
\`\`\`text
D_use(e,u) = 1[
  (prediction, legal_action)_{F10,e,u}
  !=
  (prediction, legal_action)_{F00,e,u}
]
D_episode(e) = max_{u in {011,101,110,111}} D_use(e,u)
K = sum_{e in all 16 laws} D_episode(e)
Expected K = 0
Coverage requirement = 16 laws × 4 USE × 7 arms, or explicit STOP/INVALID accounting
\`\`\`
\`K\` の**期待値0は判定用の構造予測**で、p値・有意水準・統計的検出力を設定する対象ではない。差が出ても「新能力」や「M_use陽性」を自動付与しない。まずroute/復元/漏洩/契約逸脱を監査し、原因不明ならINVALID・NOT_CERTIFIED。route名・CPU時間・AST訪問数だけの違いは \`D_use=0\`。

### 7.3 費用比較と生涯償却（記述指標）
事前固定候補の \`n ∈ {1,4,16,64}\` 回利用について、**各費用単位ごと別々に**次を示す。

\`\`\`text
C_life,arm,d(n) =
  C_train,d + C_synthesis,d + C_sleep_lite,d + C_store,d
  + C_initial_catalog_or_other_prep,d
  + Σ_{i=1..n}(
      C_inquiry,i,d + C_policy,i,d + C_use,i,d
      + C_verify,i,d + C_restore,i,d
    )
Δ_d(n) = C_life,F10,d(n) - C_life,F00,d(n)
\`\`\`

\`d\` はCPU秒、wall秒、bytes、呼出回数など**同単位内**の個別次元。RSS peakは単純加算せず最大値/分布として報告。paid Qも回数として別記。各armの開始前準備と再importを計上し、どの時点でcostが発生したかを明記する。対照arm各々の \`C_life\` も報告し、強対照に勝ったと誤認させない。

**重要な反復の境界:** 実測するUSE入力はlawあたり4種類だけであり、\`n=16,64\` はそれだけでは「16/64個の新しい独立正答」を意味しない。事前に固定した4点巡回/同頻度という**反復利用モデルによる投影**として報告し、真の16/64 fresh process実測と明確に区別する。反復を実測するなら追加の工程・子process総数・CPU上限・ノイズ設計を別途Owner凍結/実装許可してから行う。現段階では448 child以外の実測実行数を承認済みとしない。投影に必要な準備/起動費の分離ができなければ \`C_life(n)=UNMEASURED\` とし、都合のよい端点だけを表示しない。

**表示ルール案:** 全16 law×全4点×全7armの行表、route数、K/16、INVALID/STOP/欠測数と分母、費用ベクトルの各law・arm別値およびmin/median/max。CPU/wallなど測定ノイズのある値は同条件での計測分散を明記し、single-runなら誤差未評価と明記する。費用の符号が交差するnは**記述的breakeven**のみとし、普遍的優位性、信頼区間、仮説検定、U認定へ昇格しない。法則は全数なのでlaw抽選に対する標本誤差はないが、実機時間測定ノイズには不確実性が残る。

### 7.4 数値・予算上限（**すべて未承認の提案値**）
| 項目 | 提案値・判定 | 承認・実装前の扱い |
|---|---|---|
| law網羅 | 16/16、各USE4点、全7arm | 欠けた観測を成功として補完しない |
| Kの配線期待 | 0/16 | K>0は監査トリガー、陽性判定ではない |
| paid query | 法則あたりQ001を1回、全16回 | Q前commitが欠落したらINVALID |
| process wall hard cap | **5秒/child（暫定）** | 科学用4点runner完成・無害fixture計測・Muse査読・Owner採用まで未確定 |
| child上限 | 28/law、448/全16 | 試行の再実行/追加分は自動で認めない |
| child wallの単純算術上限 | 140秒/law、**2,240秒（37分20秒）/全16** | 直列のchild時間上限の和であり、準備・監査・queue・I/O・人手・実際の総所要時間**ではない** |
| CPU/RSS hard cap | **TBD（単位と測定方式を先に定義）** | 値を捏造してGOしない。凍結までブロッカー |
| 計測ばらつき/反復 | **TBD（測定回数、ウォームアップ、順序対称化、CPU/OS/Python環境）** | 未凍結なら信頼性あるwall/CPU差の結論を保留 |
| 生涯利用回数 | n={1,4,16,64}（記述的モデル） | 追加の実行許可を意味しない |

**数値決定の規則:** Museが実際の4点runnerに対する無害な計測計画（同CPU、OS、Python、負荷、起動順、単調時計、RSS定義、タイムアウト、重複実行なし）を独立査読し、Ownerが**測定前**に数値を凍結するまでは実行不可。必要なコスト閾値を結果後に都合よく置かない。経済的成功の単一「合格閾値」は置かず、各次元の絶対値と符号を全開示する。

## 8. INVALID → STOP / 診断 → NULL、事後修正禁止

**判定の優先順（提案）:**
1. **INVALIDを最優先・隔離:** private truthの子への注入、source/順序/seed/manifest・tie・容量・閾値の事後変更、未許可Q、Q前commit欠落、Snapshot/trace上書き、expected SHA不一致、law/USE点欠落の隠蔽、独立validator違反、OFF合法fallback削減・復元時decoderの片側隠蔽、custody原本不一致、繰返しの無断リトライ。証拠と全試行数は保存し、Ownerの新決定なしに当該試行を再実行しない。
2. **次にSTOP/診断:** Q001が期限切れ/拒否/不完備なら \`UNIDENTIFIABLE\`、候補/CPU/wall/RSS上限なら \`SEARCH_INCOMPLETE\`/resource STOP、公開validator不一致なら \`VALIDATION_FAILED\`。既存H0の充足は \`SUFFICIENT_H0\`、限定H0での不一致は \`MISMATCH_CANDIDATE\`（M_gapではない）。K>0は説明するまで「想定外経路差」監査で停止。**0件の黙殺・無断除外・結果に合わせた継続は禁止。**
3. **完全に有効な組のみKを算出**し、欠測/INVALIDのため16全法則の判定ができないときは \`K_full=NOT_EVALUATED\` とし、確認済み分母・失敗数だけを記載（欠けたlawを0扱いしない）。全16適格でK=0なら、**「この固定在庫/有限16法則/USE4点では、保存bodyのON/OFFで予測・合法行動は変わらなかった」**と限定NULLを宣言する。M_use認定なし。経路/費用の差があってもNULLは覆らない。
4. **将来分岐:** 費用優位なしなら経済的利益なしをそのまま報告し、現路線STOP/REDESIGNの判断をOwnerへ返す。費用差ありでもBへ自動移行しない。Bの実環境証人がない限りB NO-GO。別のF_aff外law・新概念/表現修復への展開は独立研究ゲートであり、Aの事後救済には使用しない。

事後に方法/閾値/順列/除外/費用配賦を変更したい場合、旧版は残し**新ID・新main SHA・文書digest・逸脱台帳・再査読・新Owner許可**で別研究として起草する。失敗・NULLを消さない。

## 9. 公開、監査署名、再現性と結果テンプレート

### 9.1 凍結・外部原本の提案（現時点未実施）
1. 本起草稿のMuse独立査読→指摘修正→Ownerの**文書採用**判断をPRに署名/日付付きで記録。採用しても実行GOにはならない。
2. mainへ採用稿をmergeした**確定commit SHA**とファイルのSHA-256、方法v2/arm manifest/数値閾値の版、決定コメントURL、変更履歴を別の不変receiptに記録。今のbase SHAやPR headを確定原本と取り違えない。
3. **可能なら**OwnerがOSF Registries等の外部read-only timestamped registryに、原本PDF/Markdown・SHA・方法・公開閾値・各roleを登録し、登録ID/時刻/URL/embargo条件をGitHubの補助receiptに記す。これは**GitHubコネクタで自動登録されたと主張しない**。使えない場合は「外部保全なし・GitHubのみ」という限界を記録し、Ownerが可否を判断。
4. 凍結後、対象runner/route監査は**実際に走らせるexact commit SHA**に固定し、Museがsource/scoreを見ずに独立署名する。方法固定とrunner auditは別物。方法とrunnerの不一致ならRUN BLOCK。
5. 必要な追加runner・保管/検査機構は別の実装許可・コード査読が先。すべて揃った後、さらに**別Owner実行GO**が出て初めて工学測定を開始可能。科学実行GOは本Aの成果物から自動発生しない。

### 9.2 将来の出力様式（**空欄が正しい現状**）
\`\`\`yaml
prereg_id: R2-M-A-20261105-EXHAUSTIVE16-ENGINEERING-PREREG
prereg_status: NOT_FROZEN
prereg_main_sha: TBD
prereg_file_sha256: TBD
external_registry: NOT_REGISTERED
owner_document_adoption: PENDING
owner_implementation_go: NOT_GRANTED
owner_execution_go: NOT_GRANTED
runner_exact_head_sha: TBD
muse_route_audit: NOT_PERFORMED
law_order_commit: NOT_CREATED
n_laws_expected: 16
n_use_points_expected: 64
n_children_expected: 448
n_laws_completed: NOT_RUN
n_valid_pairs: NOT_RUN
k_full: NOT_EVALUATED
invalid_count: NOT_RUN
stop_count: NOT_RUN
cpu_rss_caps: TBD
observed_costs: NOT_MEASURED
claim: {m_use: NOT_CERTIFIED, m_gap: UNKNOWN, n_rep: NOT_EVALUATED, u: NOT_EVALUATED, t: NOT_EVALUATED}
\`\`\`

公開予定は全法則・全arm・全点のtrace索引、費用台帳、前登録/runner version・対象SHA、INVALIDとSTOPの分母、監査とOwner署名、計測環境、全逸脱、NULL/未評価の明示、外部registryの有無。結果CSV/JSON/score receipt**自体は現在存在しない**。全出力のローカルhashとGitHubのcommitは独立custodyの証明に置換しない。

## 10. 手順別Owner GO、未決項目、出口

| Gate | 責任主体・判定素材 | 本稿時点 |
|---|---|---|
| G0 起草 | Owner [PR #180決定](https://github.com/ryonakayama234/DekaSugi/pull/180#issuecomment-6658438738) によるA docs-only起草許可 | **GRANTED（起草のみ）** |
| G1 文書独立精査 | Museが本A文書の10章・数値提案・費用配賦・NULL/INVALID・method-v2整合を確認 | **PENDING** |
| G2 Owner文書採用/凍結 | Muse指摘を踏まえ、Ownerが採否・数値・外部registry方式を決め、main確定SHA/文書digestを登録 | **PENDING / NOT_FROZEN** |
| G3 実装（別許可） | 4点runner/費用計測/receipt等の実装計画→Owner別GO→docs以外の別PR→独立テスト/査読 | **NOT_GRANTED** |
| G4 実経路・再現監査 | exact runner SHA、全合法F00/F10復元/dispatch・7arm・全16law・閾値・データ隔離をMuseが独立監査 | **NOT_PERFORMED** |
| G5 順序manifest/原本保全 | Ownerによる全数順序fix/必要ならseal、receipt原本と事前commit準備（方法凍結後） | **NOT_PERFORMED** |
| G6 工学測定実行 | G2–G5の合格を記録したうえで、**別の明示Owner GO**。実行/採点/公表の権限・範囲を確定 | **NOT_GRANTED** |
| GX B・科学的M_use実験 | 新方法、新事前登録、実環境証人、独立精査とOwner判断 | **NO-GO / OUT OF SCOPE** |

**Owner採用済み決定OD1–OD9とのトレース:** OD1 A先行/B分離、OD2費用/手続のみ、OD3 Owner custodian（Aには秘密law不要）、OD4閉包UNKNOWN＋実経路監査、OD5全16法則・K検査、OD6 F01/F11保留、OD7確定main SHA＋可能なら外部registry、OD8 B NO-GO、OD9起草のみをそれぞれ上記に反映。

**独立査読のP0論点:** (a) 5秒/child・CPU/RSSの未凍結値を実行前に確定できるか、(b) actual runnerでrestore時decoderやFIXED-MACRO importを二重計上/隠蔽していないか、(c) 448 childのうち実測とC_life投影を混同しないか、(d) 16/16網羅の欠測とK=0の報告が一致するか、(e) 外部registryが無い場合の監査手続が十分か、(f) 同一Snapshotと全合法OFFをexact-headで監査したか。**未解決ならG6へ進まない**。

### 変更履歴・決定待ち
- 2026-11-05: QS7 10章に従いAの**起草稿**を新規main基点docs-only Draftとして追加（予定）。法則12抽選ではなく**全16法則網羅**。文書採用・freeze・source順序fix・science/engineering executionは未実施。
- **凍結待ち:** 5秒の妥当性、CPU/RSS hard cap、measurement repetitions/order、C_life投影会計、manifest/order canonicalization、外部registry選定、独立監査対象exact head、G3/G6の別Owner決定。
- **成功・失敗いずれも未観測:** K、費用優位、プロセス実測、論文上の科学的証拠は現段階で存在しない。
