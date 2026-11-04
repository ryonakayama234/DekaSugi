# GATE-R0 — D案・単一R0方法文書（条件付き採用、紙上・未凍結）

id: GATE-R0-20261104-SINGLE-METHOD
status: proposed_method / pending_muse_rereview / pending_owner_r0e / no_implementation / no_scoring
updated: 2026-11-04
tags: gate-r0, method, causal-identification, effective-h0, finite-proof, claim-certificate, no-go

> **権限・優先順位:** [PR #170 のOwner決定コメント](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6624928067)を正本とする。主ルートD「因果識別を優先した最小概念獲得ループ」は**条件付き採用済み**。Bは将来の統合像、Aは必要十分な紙上証明のみ、CはN/S/R/E診断対照のみ。本書は既存資料を統合した**唯一のR0方法書候補**であって、R0-EのGO、方法凍結、R1-ENG許可、PRマージ承認ではない。新規実装・実験・TRAIN/DEV/FINAL・採点・滞留物整理は行わない。

**適用範囲:** [GATE-R0 #168](https://github.com/ryonakayama234/DekaSugi/issues/168) のR0-A〜Eに限る。[#146](https://github.com/ryonakayama234/DekaSugi/issues/146)のWIP=1とHOLDを保持。既存の[精密ドシエ](GATE-R0-20261104-design-precision.md)、[DV回答](R-20261104-03-development-direction.md)、[因果アーキテクチャ案](R0-D-20261104-causal-architecture-note.md)、[Muse査読](R-20261104-04-muse-review.md)は由来・討議履歴として残すが、当該R0の将来の方法参照先は本書とする。過去文書の未決定欄は、その記述時点の状態であり、Ownerの後続決定を上書きしない。

## 1. R0-A — 現状・証拠と科学的主張の制限

| 既存証拠 | 確定済みの範囲 | 持ち込まない推論 |
|---|---|---|
| [#166](https://github.com/ryonakayama234/DekaSugi/issues/166) / [Draft #167](https://github.com/ryonakayama234/DekaSugi/pull/167) | EXT448の公開混合でadaptive=best fixed=1040/5376、利得0。旧系列のSTOPは維持 | 「world-aware陽性25/448」を学習者の公開適応機会・family独立転移に読み替えない |
| [#139](https://github.com/ryonakayama234/DekaSugi/issues/139) | 修正後の学習質問切替は0件、learned bodyとSTATIC-MACROの区別がつかない事例 | マクロ名・rank変化を新しいbodyによる能力成長としない |
| [EXP-0002B FINAL112](../../experiments/EXP-0002B/runs/20261025-final112.md) | 各arm正解80/112、primitive calls LEARNED 6880 vs OFF 6944、総CPU利得未立証 | primitive差を生涯総費用の正味利得としない |
| [#168](https://github.com/ryonakayama234/DekaSugi/issues/168) / [#146](https://github.com/ryonakayama234/DekaSugi/issues/146) | R0のみ活動中の意思決定、実装・新評価・close/merge禁止 | 過去の未判定・NULLを新しい陽性証拠にしない |

R0-Aは既存の証拠の索引・境界確認に限定する。mainとDraft、実測と計画、NULL（評価済みで効果を識別できない）とNOT_EVALUATED（未実施）を区別し、source SHAと独立custodyが確認できないものは新たな確定証拠に昇格させない。

## 2. R0-B — 仮説空間、実効閉包、機会の定義

**対象診断世界（紙上仮定）:** 入力集合 X={0,1}×{0,1}、出力 Y={0,1}、未知の決定的関数 f:X→Y。学習者には合法公開履歴 h_t だけを渡す。完全真理値表、target law、hidden seed、family private label、heldout answerは独立Evaluatorだけが知る。2bitは意図的な工学診断装置であり、陽性率の母集団や独立familyの定義ではない。

- `H0_object`：初期の単一出力DSLが直接表現できる6関数 `{0,1,x,!x,z,!z}`。一つの述語を入力全域で固定選択する**限定装置**。本セットを越える実装済みKernelの能力を勝手に除外してはならない。
- `H0_effective(B)`：**対象の結果を観測する前に固定した**初期システム全体の、合法履歴hに対する予測方策の集合。初期primitive・macro、Kernel内外の条件分岐、入力別dispatch、rank/policy、計算ループ、初期Library、episode memory、**episodic retrievalとlookup**、履歴による選択、学習・質問・推論の資源予算Bを閉包に含む。動作可能なfallbackを除去してH0を弱くしない。構成要素の版・初期内容・状態更新規則・費用・許可情報・完全列挙の証明対象を事前に固定する。閉包を網羅できないときは `UNKNOWN`。
- `Hplus_effective(B)`：同じ外側Kernel/メモリ/照会権限に、事前固定した型付き `Bool×Bool→Bool` のメタ構文（変数x,zとAND/OR/NOT、AST深さ・ノード制限）を加えた方策集合。XOR/ORのtarget bodyを初期Libraryに与えない。構成子の意味は実験者が与えるため、primitive意味論そのものの自律発明を主張しない。
- `G_object = min_{h∈H0_object} L(h) − min_{h∈Hplus_object} L(h)`、`G_effective(B) = min_{h∈H0_effective(B)} L(h) − min_{h∈Hplus_effective(B)} L(h)`。Lは事前指定の有限入力分布における0-1損失。`G_object>0`は`G_effective(B)>0`を含意しない。Bによる差は`resource-bounded gap`と呼び、意味的な非表現可能性と区別する。
- **公開識別可能性**：決定前に到着する合法な公開回答列で競合する候補を識別できること。**時間的actionability**は、照会の完了が終端決定に間に合うこと。**適応問い合わせ利得** `G_inq` は、同じ公開情報とBで adaptive と最良合法fixed open-loopの終端効用差。R0の対象は表現不足候補の診断とbody由来の機構であり、`G_inq>0`を要件にも成果にも置かない。

**公平性規則:** (a) H0とH+双方に同じ事前公開情報・照会集合・回答到着時刻・ソース分布・容量・実行環境を与える。(b) H0にだけ分岐・lookup・episodic・推論資源を禁じない。(c) H+構成子・サイズと探索予算はSTATIC-H+にも同様に開放する。(d) body ON/OFF比較では同じSnapshot・公開履歴・policy/rank・予算を固定し、OFFでも**最良の全合法fallbackを残す**。(e) targetを見て閉包・費用・文法・対照を改変したら当該主張はINVALID。(f) 等情報・等能力の**厳密最適**STATIC-H+を厳密に超えることを成功条件にしない（上限参照のみ）。

**必須反例:** `if z=0 then x else !x` を外側Kernelが実行できれば、`H0_object`はXORを表せなくても`H0_effective(B)`は表せる。公開4入力を記憶・検索できても同様。ゆえにRの限定DSLの下界だけで実効能力差を宣言しない。

## 3. R0-C — 有限N/S/R/E紙上ケースと証明上限

共通設定：公開照会は `Q(x,z)` という合法な一回の観測で、選択時に1 paid actionを消費、返答は終端決定より前に受領する（例外は明記）。sourceのfはEvaluator-private、学習者はpublic入出力のみ。以下の有限計算は**紙上の数学的証明**であり、学習器の実行・採点・成功の報告ではない。人手で選んだ4ケースは独立familyサンプルではない。

| ケース | law・公開アクセス・予算 | 紙上の証明・正しい診断 | 認定上限 |
|---|---|---|---|
| **N: 情報なし** | 等事前 `f_A=x`、`f_B=x AND !z`。合法Qは `(0,0),(0,1),(1,0)` のみ。Q予算1、終端で`(1,1)`を予測 | 合法点上の出力は両者同じ`0,0,1`、終端だけ`1`対`0`。どんな合法履歴でも世界を識別できず等事前Bayes最良正答率`1/2`。`UNIDENTIFIABLE`。表現拡張は情報不足を直さない | 正対照なし。獲得主張は不可、学習器の「失敗」としない |
| **S: 初期H0十分** | 等事前 `f_A=x`、`f_B=!x`。`Q(0,0)` を1回、終端前に取得 | Aは0、Bは1で識別可能。両lawは`H0_object`の6候補に既存。`SUFFICIENT_H0`。H+で書き直しても新規表現修復ではない | 情報取得・既存関数選択まで |
| **R: 限定H0不整合→H+候補** | `f_A=XOR(x,z)`、`f_B=OR(x,z)`。事前公開`P={(0,0)→0,(0,1)→1,(1,0)→1}`、追加合法`Q(1,1)`にB_query=1、終端前受領 | 6個の`H0_object`候補はPの全3点を同時に満たせない（完全列挙）。追加QはXORで0、ORで1。H+の`OR(AND(x,NOT(z)),AND(NOT(x),z))`と`OR(x,z)`はそれぞれ真理値全域で一致。`MISMATCH_CANDIDATE`→公開由来の候補検証可能。ただし対象前に定義した**実効H0**の不整合は別途証明を要する | `G_object>0`の有限証人と公開識別可能性。`M_gap`・`U`・`T`は未証明 |
| **E: 探索不足** | 真の`f=x`、公開`(0,0)→0,(1,0)→1`。H0列挙順`[0,1,!x,!z,z,x]`、列挙許容量5個 | 最初の5個は不整合、6番目の`x`が整合。探索中断からは`H0全体の矛盾`を証明できない。`SEARCH_INCOMPLETE`、資源を増やせばSと判明 | 表現不足・修復の陽性認定は禁止 |

**Rの限定H0全表証明:** 入力順を`00,01,10,11`とすると、XORは`0,1,1,0`、ORは`0,1,1,1`。初期6候補`0,1,x,!x,z,!z`それぞれの全域誤り最小値はXORに`2/4`、ORに`1/4`。H+上記2式はどちらも`0/4`。これは限定DSLでの`G_object>0`を示すが、外側のif/lookup等があれば`G_effective(B)`は0になり得る。実効閉包を証明できなければRも`M_gap`に格上げしない。

**診断の決定順:** 漏洩・契約違反は`INVALID`で最優先停止。公開情報が決定前に区別不能なら`UNIDENTIFIABLE`。探索完全性未達なら`SEARCH_INCOMPLETE`。全候補照合済みで整合候補ありなら`SUFFICIENT_H0`、空なら`MISMATCH_CANDIDATE`（不十分な実効閉包には`UNKNOWN`）。後続の独立検証後だけ`REPAIR_VALIDATED`。未証明は`NOT_CERTIFIED`に留める。これらは**提案する将来の状態語彙**であり、実装済み判定ではない。

**全4点の証拠上限（Muse P1-1）:** Rでは識別的Q後に2bit全4入力が公開済みとなる。再提示・順序変更・役割置換の公開検証は**整合性チェック**に過ぎず未見入力の検証ではない。fresh process／新IDで同じ2bit関係を使うことも、永続化・読み出し・dispatchの確認であり、未見組合せ・独立family転移・未知環境への汎化ではない。

## 4. 公開アクセス境界・合法行動・費用・漏洩

`source (private law) → public API (legal_actions/observe/step) → learner → independent validator` の一方向境界を守る。Evaluatorは先にsource・候補family・split・法則・終端効用と版/ハッシュを確定し、公開APIが**合法行動集合、事前公開サンプル、支払済み照会応答と時刻・費用のみ**を渡す。learnerは予測・問いを**結果受領前**にcommitして追記専用記録へ残す。validatorは型・構成子意味論・公開反例との整合性を独立に確認し、将来のprivate scored receiptは学習後に限りEvaluator custodyで別保管する。

| 記録契約（設計案） | 必須フィールド・禁止情報 |
|---|---|
| `PublicStep/v1` | episode/seq、合法行動集合のdigest、選択・回答時刻、public input/output、paid inquiry cost、予測commit digest。**禁止:** hidden law/family/seed/target body/heldout |
| `HypothesisCertificate/v1` | H0_objectとH0_effective(B)の版、closed-world全候補/予算/完全性証明、反例、候補と不整合reason。未完を完了と偽らない |
| `ConceptBody/v1` | 型付きAST、H+構成子版、公開出典・依存、validator receipt、canonical digest、初期macroとの同値ラベル。任意Python callback禁止 |
| `Snapshot/v1` | 不変のparent/body/registry/policy digests、承認または保留、生成手続と時系列。post-hoc上書き禁止 |
| `UseTrace/v1` | fresh process ID、ON/OFF条件、available/selected/executed/finishedの別記、実dispatch、予測/ABSTAIN、最良fallbackとcost |
| `ScoreReceipt/v1` | Evaluator保管のsource/split/arm/estimand/合計費用・digest chain。public入力へ私的答えを逆流させない |

**合法行動:** 宣言された公開Qのみ（Nは`(1,1)`禁止、Sは`Q(0,0)`、Rは`Q(1,1)`、Eは予め与えた2点のみ）。固定非学習query policyを初段に許すが、「Active Learningを学習した」と呼ばない。未承認の直接Oracle照会、private law/family IDの読み取り、評価用答えへのアクセス、無断の情報取得は禁止。照会予算・回答が有効になる時点・終端前後・同点規則・未回答ABSTAIN費用も先に定義する。

**費用の記帳:** 各paid Q=1を最小単位とし、加えて候補列挙数・展開後原始操作数・ASTノード数・CPU・wall・最大RSS・永続化/復元bytes・validator呼出/費用・policy推論費を別台帳にする。異なる単位を後付け単一スコアへ混ぜない。独立科学比較時は前登録した換算・目的・成功率／ABSTAINとのPareto取扱いが必要。source公開前後のSHAと記録者、出典別custodyも残す。

**INVALID規則:** target AST・非公開正答・family/seed・未来の回答がpublic/learnerへ流入、結果を見てgrammar/H0/費用/世界集合を選別、非合法Q、予測の事後上書き、学習器のprivate validator読取り、評価結果の学習再投入、独立原本custodyの破綻を確認したら、そのepisode/比較主張を`INVALID`として隔離し**陽性・陰性・NULLの分母に算入しない**。漏洩をただの性能低下に置き換えず、原因・影響範囲を記録し、別のOwner承認なしに再試行しない。旧sealed評価を再実行しない。

## 5. R0-D — Claim Certificate Matrix / 主張・対照・生涯費用

**P0-1の定義（無印Mは禁止）:**

- `M_use`：公開証拠からtarget bodyの人手注入なく型付きbodyを構成し、独立validator合格→immutable保存→fresh実dispatchし、同じSnapshot/公開履歴/policy・全合法fallback有効のbody OFF介入で**予測または合法行動の差**を確認した使用機構の実証。dispatchログだけ／fallbackを全停止したOFF差だけなら**未認定**。学習能力上限・実効ギャップ・経済性を証明しない。
- `M_gap`：事前固定の`H0_effective(B)`の網羅的な非実現証明、**OFF時の最良合法fallback**を明示したうえで、同じ公開情報・policy・予算でbody ONだけが対象の振る舞いを実現。`M_use`の上位であるが、実効差が消えるなら認定不可。資源限定ならresource-boundedと注記。
- `N_rep`：初期Libraryに**実在した**再利用可能macro/bodyと、新bodyのcanonical AST・有限外延・事前固定の記述長・合成可能性を比較した**表現上の新規性**。初期bodyと同値なら0（再発見）。仮想lookupが予測を模倣可能というだけではN_repを消さないが、M_gapを消し得る。新しい物理的意味論の発明を意味しない。
- `U`：同等H+容量・公開情報・学習/照会/保存/USE資源を許す強いSTATIC、episodic、fixed macro、policy/rank-only、body OFFに対して、別に前登録されたfresh評価で正確性・棄権と**生涯総費用**の実利が示されること。無制限の最適STATIC-H+は上限参照だけ。`U=NOT_EVALUATED`を`NULL`にしない。
- `T`：上流生成機構が異なる**独立family**で、学習前にgroup splitと評価契約を固定し、未見familyで再利用効果を示すこと。役割名変更やseedの増加はTではない。`T=NOT_EVALUATED`が初期値。

### Claim Certificate Matrix（紙上R0時点の上限）

| 対象 | H0_object | H0_effective(B)の内訳・閉包条件 | body OFF時の最良合法fallback | R0で認定できる最大ラベル／将来の必要条件 | 禁止する推論 |
|---|---|---|---|---|---|
| **N** | `x` は存在。`x AND !z` は不在 | Kernel分岐・lookup・episodic・履歴を含めても、合法Qで両lawは識別不能（等事前） | 合法履歴上同等の候補から終端を推測／ABSTAIN | `UNIDENTIFIABLE`のみ。`M_use`・`M_gap`不可 | H+による不可視情報の発明・学習失敗 |
| **S** | `x,!x` が存在 | 全Kernel/検索/dispatchと予算込みでもH0内に完全正解あり | `Q(0,0)`で識別し既存`x`または`!x` | `SUFFICIENT_H0`のみ。bodyを後付けしても表現修復なし | 新規性・能力上限向上 |
| **R** | 限定6述語はXOR/OR両方で不完全 | 分岐・lookup・episodic・memory・rank・dispatch・Bを**対象より前に**固定して列挙する必要あり。4点lookupが合法で使えるなら`G_effective=0`もあり得る | H0全候補＋4点episodic lookup＋分岐/固定H+（比較段階に応じ合法なもの全て）から最良を選び、費用を開示 | **現R0は`G_object>0`と公開識別可能性まで**。将来`M_use`は独立生成/保存/fresh/OFF予測差、`M_gap`は公平な実効閉包下界がさらに必要。`N_rep`は初期Library照合後のみ | toyを`M_gap`、`U`、`T`または未見汎化と呼ぶこと |
| **E** | 真の`x`が6番目に存在 | enumerate=5上限・kernel/lookupを含む探索の未完を明示 | 既存`x`へ到達できれば正解。未完ならABSTAIN | `SEARCH_INCOMPLETE`のみ | 探索停止をモデル表現不足や修復成功へ置換 |

**行列の読み方:** この表はR0の**紙上認定可能性**を示す。R行でも`M_use`の実行証拠は今存在しない。`M_gap`の不足を弱いH0へ差し替えて補完しない。OFFの最良経路を無効化して差を創る自己成就的な実装は禁止。最強STATIC-H+と同じ予測なら新たな意味的能力は示されず、再発見はN_repに0として残す。

**主張段階ごとの必須対照:** `M_use`＝public provenance、target非注入、独立validator、全fallback有効のbody OFF、漏洩監査。`M_gap`＝H0_effective(B)全候補網羅・最良fallback同予算比較。`N_rep`＝初期Library/macroとのcanonical・外延・コード長照合。`U`＝同容量STATIC-H+、episodic retrieval、意味同値fixed macro、policy/rank-only、body OFF、生涯費用・事前償却回数。`T`＝独立family group splitとrole/seed非独立性監査。後段の要件をM_useの前提に混ぜない。

| Arm | body利用 | rank/policy | 目的・識別可能性 |
|---|---|---|---|
| **F00** | OFF | 固定 | 同じH+候補容量・照会/計算Bでの最良STATIC-H+／合法fallback |
| **F01** | OFF | 学習 | 選択・rankingだけで説明できるか |
| **F10** | ON | 固定 | policyを固定したbody介入`F10−F00`（固定body/episodicとの比較も必要） |
| **F11** | ON | 学習 | 本体＋方策の結合`F11−F01`、交互作用を見る。単独のbody因果効果と混同しない |
| **Episodic** | 既観測履歴検索 | 同情報・容量・費用 | 暗記と検索が同じ結果を出せるか |
| **Fixed macro** | 意味同値macroを最初から持つ | 同容量・費用 | learnedという由来以外に独自利益があるか |
| **Oracle** | evaluator-only | 理想上限 | **対照の勝敗条件ではない**。学習者には公開しない |

**生涯費用（事前固定する式）:** `C_life(n)=C_train+C_synthesis+C_sleep_lite+C_store+Σ_{i=1..n}(C_inquiry_i+C_policy_i+C_use_i+C_verify_i+C_restore_i)`。STATIC/episodic/fixed macroも同じ費目と許可済み情報・資源で計上し、準備費を0と仮定しない。`d=C_static_per_use−C_learned_per_use`が正なら償却目安は`ceil(C_setup/d)`（`C_setup`はlearned側の純増準備費、比較側準備費を控除）；`d≤0`なら費用だけでは償却不能。n、評価分布、失敗・棄権の損失、コード長、予算上限、重み、欠測扱いを**結果前**に固定し、事後都合のよいnへ変更しない。R0では費用式の定義のみで実測値や優位を報告しない。

**成果ラベル規律:** 各軸は`POSITIVE / NEGATIVE / NULL / NOT_EVALUATED`を区別し、証拠違反は別扱いの`INVALID`。N_repでは再発見を0/NEGATIVEとして記録できるが、未検査を0と断言しない。現時点で`M_use=NOT_EVALUATED; M_gap=NOT_EVALUATED; N_rep=NOT_EVALUATED; U=NOT_EVALUATED; T=NOT_EVALUATED`。Museの`M_use-positive / N_rep-null / U-not-evaluated / T-not-evaluated`は**条件が揃った将来の記載例**であって今回の結果ではない。

## 6. 紙上エピソード1件（旧R0-Tを本節へ統合、未実行）

対象はRのXOR world。固定query policy・許可された型付き合成のみを仮定し、**時系列と異なる権限者**を分離する。ここに新たな世界／実装／学習結果を追加しない。

| 時刻 | source / public / learner / validator に起きる**仮定上の**出来事 | 適切な証拠・認定の限界 |
|---|---|---|
| t0 | Evaluatorがprivate`XOR`と契約を保管。LearnerはH0閉包仕様とpublic合法Q一覧を受け、結果前に予測をcommit | target AST非注入、prequential digest。Oracle知識をlearnerに渡さない |
| t1 | public`(0,0)→0,(0,1)→1,(1,0)→1`を順次受領 | 限定H0_objectの全6不整合。ただしH0_effective(B)閉包未証明なら`MISMATCH_CANDIDATE`止まり |
| t2 | 固定の合法`Q(1,1)`を1 paid actionで選び、結果前commit | 質問学習の成果とはしない。入力別の適応利得は主張しない |
| t3 | publicが`(1,1)→0`を返す | XOR/ORを識別。ただし2bit全4点公開済み |
| t4 | Learnerが事前許可AND/OR/NOTから型付きAST候補を合成し、public evidenceに照合（対象式の人手注入なし） | 検索順・上限・失敗候補も追記。既存macroとの外延同値と公開来歴を確認 |
| t5 | independent validatorが型/純粋演算/公開全4点との一致とdigestを照合 | **既知点での整合性検証のみ**。新しい公開検証例・未見汎化と呼ばない |
| t6 | Sleep-liteが**意味を変えないcanonical化**、validator合否記録、版付immutable保存を行う | 意味の違う候補の選択はWake側の合成・検証に帰属。高度Sleep/圧縮学習の成果なし |
| t7 | 新プロセスがSnapshotを復元し、同じ2bit表の合法入力でbodyを実dispatch | 保存・復元・dispatchの工学確認。新ID/role renameは独立family転移でない |
| t8 | policyと同一public履歴を固定して当該bodyのみOFF。H0候補・lookup・episodic等**全合法fallbackを残す** | 予測・行動差と費用を記録。4点lookupが同じ正答なら`M_use`も未認定となり得る。OFF強制ABSTAINは不合格 |

紙上表で`t4〜t8`の動作を**実行済みとはしない**。このエピソードはR0のmethod/trace条件を確認するための思考実験である。R1以降の実装・freshスコア・新familyを承認するものではない。

## 7. R0-E — STOP／転換／Owner決定欄

**主張単位のSTOP**（主張が成立する証拠の欠如を陽性に改名しない）:

1. 予め固定したH0_effective(B)を対象の結果なしに定義・列挙できなければ、`M_gap`／実効表現修復を`STOP or NOT_CERTIFIED`。Rの限定H0だけが証明された状態は`M_use`の設計可能性へ留める。
2. 合法publicでは識別不能ならNの`UNIDENTIFIABLE`とし獲得主張停止。探索未完ならEの`SEARCH_INCOMPLETE`とし表現不足主張停止。
3. `G_effective(B)=0`が公正な網羅比較で確定した対象familyでは`M_gap`をSTOPし、弱いH0へ差し戻さない。`M_use`の配線依存だけで能力成長を宣言しない。
4. target注入・リーク・private評価へのアクセス・事後のgrammar/世界選別・独立custody違反なら`INVALID`として直ちに停止。過去のSTOP/NULLを覆さない。
5. 将来の別承認下で`M_use`のパイプラインを再現できなければDの継続をOwnerが再判断。最初に事前宣言したN_repとUの科学評価がともにNULL/NEGATIVEなら「能力成長」系列のSTOPをOwnerが判断する（企画全体の自動STOPではない）。

**圧縮・Uへの転換:** `G_effective(B)=0`なら、表現修復を同じ名前で救済せず**新しい科学的主張としてOwner再承認**を要する。転換が可能なのは、対象データを見る前に固定した記述言語・コード長・episodic/lookup比較・再利用回数n・生涯費用・判定閾値があり、同容量のSTATIC対照で比較可能な場合だけ。固定基準で費用利得がなければ圧縮/UもSTOP。事後に新たな世界を設計して同じ結果を陽性化しない。

**R0レビュー出入口（本書の5項目+付録を単一査読）:** (1) 実効H0閉包と公平性、(2) N/S/R/E有限証明と証拠上限、(3) source→public→learner→validatorと費用/INVALID、(4) Claim Certificate Matrix・分離したM_use/M_gap/N_rep/U/T・強対照/総費用、(5) STOPとOwner決定、**紙上エピソードは本書`6**。本書を提出→Muse/Claude再査読→Ownerが`R0-E: GO / REDESIGN / STOP`を決定する。**提出・check_docs成功・査読依頼だけではR0終了としない。**

**Owner決定欄（未決定、記入権限はOwner）:**

| 決定 | 現在の状態 |
|---|---|
| 開発主ルート | **D 条件付き採用済み** — [Ownerコメント](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6624928067) |
| Muse/Claudeの**本方法書**再査読 | **PENDING** |
| R0-E最終判定 | **PENDING — GO / REDESIGN / STOP 未決定** |
| 方法の凍結／改訂・未解決P0/P1 | **PENDING** |
| R1-ENGの実装許可と対象範囲 | **PENDING** |

**R0-E決定文にOwnerが記す必須行（未決定のまま保持）:**

> `R1-ENG authorization: granted / not granted — scope: ...`

この行がない、または`not granted`なら、R0-EでGOと評価されてもコード実装は禁止。将来`granted`の場合でも、この行に明記されたworld/package/testだけの隔離された工学診断を許可し、正式M実験・U評価・独立family転移・既存封印済み評価・旧PR整理を自動許可しない。新しい評価はさらに別の承認とsource-first凍結を要する。

**長期研究仮説はR0範囲外:** 参照先のみ [因果アーキテクチャ案`9](R0-D-20261104-causal-architecture-note.md)。B統合像・Active Learning方策学習・本格Sleep・NN・多世界転移はここで起動・展開しない。

## 由来と査読条件

- 最上位決定：[PR #170 Owner決定](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6624928067) ／ [R0 #168](https://github.com/ryonakayama234/DekaSugi/issues/168) ／ [運用 #146](https://github.com/ryonakayama234/DekaSugi/issues/146)。
- 入力：[GATE-R0精密ドシエ](GATE-R0-20261104-design-precision.md)、[DV1〜DV10回答](R-20261104-03-development-direction.md)、[D因果アーキテクチャ案](R0-D-20261104-causal-architecture-note.md)、[Muse独立査読 P0-1/P1-1〜6](R-20261104-04-muse-review.md)。R0-PとR0-Tを二文書に分けず統合した。
- 審査要求：[Muse/Claudeによる新規方法書の独立再査読](https://github.com/ryonakayama234/DekaSugi/pull/170)。本書の提出者による自己判定は独立査読に代わらない。
