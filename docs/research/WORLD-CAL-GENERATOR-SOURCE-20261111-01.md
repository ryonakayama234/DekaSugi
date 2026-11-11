# WORLD CAL 生成器 source-first 定義パック — Research Lead 提出

id: WORLD-CAL-GENERATOR-SOURCE-20261111-01
status: source_first_draft / SUPERVISOR_REVIEW_PENDING / NOT_CAL_AUTHORIZED / NOT_FROZEN
updated: 2026-11-11
tags: world-expansion, cal-preparation, generator, source-first, research-lead, design-only, no-holdout

> **権限境界**: [Issue #195 の PROTOCOL_APPROVED](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6784655532) は成立済み。本書は生成器の `source-first` 定義候補を、監督者が独立再計算できるようデータ化したもの。Owner による CAL_AUTHORIZED／実装 GO／事前登録 FROZEN／実験 GO は**全て未成立**。law の抽象 support と分布表を登録しただけで、**holdout の実 instance／target／score／seed／split 割当を一切生成・実体化していない**。この PR の digest 固定は版識別であり、Owner の科学的凍結ではない。

## 1. 正本、構成物、byte digest

- 規範: [仕様パック第6版 §4／§5／§6／付表A](https://github.com/ryonakayama234/DekaSugi/blob/351016fe0e2d468c80736a477133a274cfb713b8/docs/research/WORLD-PREREG-SPEC-20261110-06-specification-pack-v6.md)（Git blob `9362065507791ced44e2a3cc218c93a0b3cef395`）と [CAL プロトコル §5／§7.3](https://github.com/ryonakayama234/DekaSugi/blob/156491a5e710b2ef8b7ea38d9fa92f83439aa9f5/docs/research/WORLD-CAL-PROTOCOL-20261111-01-lead-draft.md)（Git blob `f01471d448da42c1458b4eb38203b71dc517a663`）。プロトコルの旧本文ヘッダが「未承認」のままでも、Owner 承認は Issue の記録で成立している。
- 法則の**全384行と厳密な p_l**: [WORLD-CAL-GENERATOR-DISTRIBUTION-20261111-01.json](WORLD-CAL-GENERATOR-DISTRIBUTION-20261111-01.json)。`distribution_table_digest = sha256:bdc841181fe370d940df95d12150e9216b110e065c89c4bfced031dc89339576`。
- 有限グリッド、法則意味論、全量構造除外、parent split、runtime manifest の待機欄: [WORLD-CAL-GENERATOR-MANIFEST-20261111-01.json](WORLD-CAL-GENERATOR-MANIFEST-20261111-01.json)。`generator_version = WORLD-GEN-SRC-1.0.0`; source file digest = `sha256:3b0e500890a0836cb2711422b54d55412e6d07654e1dabe5aeaeab18b8b85f3a`。
- これらの SHA-256 は**保存された UTF-8/LF のファイル全 bytes（末尾 LF を含む）**の値。JSON の key 再整列・空白調整・改行変換では digest が変わる。manifest 自身には self-referential digest 欄を設けず、外部のこの説明と PR に登録する。Git blob SHA-1 は SHA-256 に代用しない。

## 2. 法則の文法・分布と全量の数え上げ

4族（`TRANSCRIBE,REPEAT_COPY,OBS_EDIT,TWO_STAGE_JOIN`）を等確率 `1/4`、各族の2 template を `1/2`、2つの異なる順序付き role `(signal,payload)` を12通りから `1/12`、述語 `COUNT_EQ／COUNT_LT` を `1/2`、`k` は転写・観測編集で単一の `0`、反復コピー・2段連結で `1,2,3` の一様分布とする。正規形は仕様 §5 の5要素 `(template_id, predicate_AST, branch_operation, target_role, normalized_parameters)` に一致させる。COUNT は §2 の公開記号別カウント特徴、比較は既存 COMPARE（EQ/LT）。法則の非公開目標で条件分岐を評価することは、学習 arm に二階 BRANCH を供与することではない。

| 族 | template | 生グリッド | role 重複を除いた unique law | 1 law あたり p_l | 親数／親あたり law |
|---|---|---:|---:|---:|---:|
| 転写 | T_HEAD / T_TAIL | 64 | 48 | 1/192 | 24／2 |
| 反復コピー | R_HEAD / R_TAIL | 192 | 144 | 1/576 | 24／6 |
| 観測依存編集 | O_HEAD / O_TAIL | 64 | 48 | 1/192 | 24／2 |
| 2段連結 | C_PREFIX / C_SUFFIX | 192 | 144 | 1/576 | 24／6 |
| **合計** | 8種 | **512** | **384** | **合計質量1** | **96親** |

生グリッドの `signal=payload` 128通りは最初から登録文法の無効パラメータであり、law support に入れない。law ID は正規5タプルのコンパクト JSON を定義されたバージョン文字列でドメイン分離して SHA-256 化する。全384行を実体データ表に列挙したので重複 draw による n 増殖は不可能。**出力の意味による事後的な law 同一視は行わない**。template の完全な true/false 目標式は manifest `template_semantics` の8式が規範（x の置換、k回反復、連接、回転を明示）。

## 3. 初期 instance 抽象グリッドと構造除外 F

- 初期長: TRAIN/CAL/G1 は `L=4..12`、G2 は `L=13..16`（仕様第6版 §4）。中間／target buffer 上限16。phase ごとの4 live Sym には24置換を均等に適用し、入力 x は manifest の8つの**数式指定** word pattern のいずれかを均等に選ぶ。初期カーソル0、selection none、clipboard empty。各 law/phase は、その law に**容量上合法な L**の一様選択→置換24通り→word pattern8通り、の階層分布。分布は score に応じて変更しない。
- 生成**前**の容量除外は `template∈{R_HEAD,R_TAIL} AND L+k>16` のみ。6種の他 template は target 長が L であり除外なし。全 law×phase×L セルに**必ず適用**してから vocabulary/word pattern を展開する。G2 の REPEAT_COPY は k=1/2/3 ごとに不適格 L が1/2/3個、各 k に48 law → `48×(1+2+3)=288` 個の law×L セルを除外する。
- 全量算術: TRAIN/CAL/G1 はそれぞれ `384×9=3456` law×L セルが有効（除外0）。G2 は `384×4=1536` セル中、除外288、有効1248。1セル当たり24×8=192の抽象初期候補 → G2 は raw294,912／除外55,296／有効239,616セル、TRAIN/CAL/G1 は各663,552セル。**これは直積サイズの算術であり、文字列・実 instance・target は生成していない。**
- `F_laws` は登録 law support から、許された TRAIN/G1 長に対し容量上合法な instance が1個もない law を除く。今回のグリッドでは全 law に合法な長4..12があるため、law 単位の容量除外は0、`|F_laws|=N_unique=384`。長16の反復コピーを禁止する**instance セル除外**を、G2 全体や当該 law 全体の事後除外に拡張しない。K0 の判定不能、未到達、識別不能は §4 の主分母を変更しない（§6 の STOP/INVALID 規則を適用）。
- 3デモ対は同じ law の admissible instance 格子から別 domain で重複なしに後日選ぶ。trial と demo は同一セルにならない。EVAL 成功/失敗は学習へ戻さない。現段階ではセルを選ばない。

## 4. parent cluster の境界と sealed split 規則

親は `(family_id,template_id,signal_role,payload_role)` の SHA-256 ID。predicate 2通りと k の派生は**常に同一親**に属する。親は各族24、計96。後日 Owner escrow の独立した split key で、族ごとに `HMAC-SHA256(key,'WORLD-PARENT-SPLIT-v1\\n'+parent_id)` を unsigned256bit 昇順に整列し、parent ID で tie-break。転写／観測依存編集は先頭3親が TRAIN、次3親 CAL、残り18親 holdout。反復コピー／2段連結は先頭1親 TRAIN、次1親 CAL、残り22親 holdout。親の部分割当は禁止する。

したがって**設計上の必然的な個数**は TRAIN=24 law（各族6）、CAL=24 law（各族6）、holdout `N_eligible=336` law（36／132／36／132）、holdout 親80。条件付き質量 `Σ_H p_l=5/6`、`q_l` は転写・観測編集で `1/160`、反復コピー・2段連結で `1/480`。この数量は **抽象的な定義からの計算**であり、holdout 法則一覧・seed・割当結果・instance を確定/公開したことを意味しない。実 `parent_cluster_allocation_digest` と `H_laws_digest` は null のままとし、別途許可された sealed 割当のあとに source-first で検証・固定する。

## 5. 再現性・アクセス・審査関門

- **監査可能性**: 第三者は2 JSON の raw byte SHA-256 を独立計算し、384件の法則 ID を正規5タプルから再構成、96 parent の全集合、族ごとの総質量各1/4、除外算術（G2の288セル）と 24/24/336 の split quota を**抽象グリッドの算術だけで**再確認できる。出力と照合して不一致なら FAIL、変更ではなく逆質問に戻す。
- **アクセス**: manifest は source 定義。CAL_ORACLE には抽象 generator law と instance/demo 分布、feedback・予算規則のみ。BLIND_DESIGN_CALCULATOR は別途 CAL_AUTHORIZED 後に署名済み `N_eligible,q,parent_cluster` の設計メタデータのみを読み、law ID↔重みの外部出力を禁止。学習側には源法則・私的配分、target、score、seed、評価 manifest を読ませない。PROTOCOL_APPROVED の [E2 ACL digest](https://github.com/ryonakayama234/DekaSugi/pull/204) は変更しない。
- **実行不能条件**: 署名済み割当値、モデル・ACL digest、seed escrow、承認済み実装 `algorithm_digest`、後続 runtime 参照欄が未完成なら `CAL_AUTHORIZED` の前提を満たしたと**主張しない**。許可前には K0／simulation／CAL の実行、holdout instance のサンプリング、receipt 発行を行わない。
- **意義と限界**: 第6版 §4/§5 は4族・一様有限グリッド・容量除外の原則を定めるが、8 template の具体意味・word pattern・親 root key はまだ既承認本文で指定されていない。本稿はそれらを**Research Lead の提案**として明示的に実体化した。合意が得られなければ既承認仕様を黙って上書きせず、generator の新しい版／監督者再審査へ戻す。下記逆質問を参照。

## 6. 監督者への逆質問（未承認事項）

**RQ-PREP-G01（定義委任の範囲）**: 仕様第6版 §5 の「生成器仕様の付表にグリッドを列挙する」との委任範囲に、本稿の8 template の目標意味論、8 word pattern、96 parent の構造を収めてよいか。いずれかが既承認設計の意味を変えると判断される場合は、**仕様を無断変更せず**当該差分と新設計版を別途要求する。

**RQ-PREP-G02（G2 容量の扱い）**: 反復コピーで `L+k>16` のセルを全量事前除外しつつ、law 自身を `F_laws` に保持することは §4／§5 の「容量の構造的除外」を忠実に満たすと判断できるか。もし「全4族に長16の G2 実 instance が必要」と解釈するなら本グリッドと矛盾するため、黙った回避ではなく仕様改版が必要。

**RQ-PREP-G03（split digest の時点）**: CAL_AUTHORIZED 記録へ固定すべきものを、この2 source JSON の digest／公開 parent 割当**規則**までとし、秘密鍵・実割当 digest は別途 Owner escrow 後、CAL 開始前の sealed 入力 receipt へ記録する扱いでよいか。必要な場合、実割当 digest を Owner の承認時点で非公開添付する手順を明示してほしい。秘密を作ったことにはしない。

**判定提案**: まず manifest のバイト同一性と §4／§5 の適合を監督者が AGREE／REVISE／DISAGREE で審査。合意と Owner の CAL_AUTHORIZED は別。未解決回答を「実装で適当に埋める」ことは認めない。
