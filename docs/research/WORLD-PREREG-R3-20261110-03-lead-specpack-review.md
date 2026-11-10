# WORLD-PREREG-R3-20261110-03 — Research Lead 仕様パック審査（B1〜B6）

id: WORLD-PREREG-R3-20261110-03  
status: research_lead_specpack_review / REVISE_BEFORE_DESIGN_CONSENSUS / NOT_FROZEN / NO_CAL_GO / NOT_IMPLEMENTED / NOT_RUN  
updated: 2026-11-10  
author_role: Research Lead (ChatGPT)  
review_target: [PR #194 head a01662cc](https://github.com/ryonakayama234/DekaSugi/pull/194)  
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)  
questions: [WORLD-PREREG-RQ3-20261110-03](WORLD-PREREG-RQ3-20261110-03-specpack-blockers.md)

> **審査の位置づけ**: 2026-11-10 の [Owner 採用記録 6768253225](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6768253225) は RQ2 Q1〜Q8 の**設計案**の採用であり、数値凍結・CAL 承認・CAL GO・実装 GO・実験 GO ではない。本書は docs-only の独立審査であり、上記の実施・認定・main merge を許可しない。PR #194 は Draft のまま保持する。

## 0. 対象・判定規則・結論

照合対象を以下の正確な版に固定した。

- [仕様パック WORLD-PREREG-SPEC-20261110-01 §0〜§7（PR #194 / a01662cc）](https://github.com/ryonakayama234/DekaSugi/blob/a01662cc65190ab54ffab4b4daeb6b1429005701/docs/research/WORLD-PREREG-SPEC-20261110-01-specification-pack.md)、blob `140a686866bcbc71b98f8dd9ccb3d06cc14c9e11`。
- [ドラフト v2 WORLD-PREREG-DRAFT-20261110-01（同 head）](https://github.com/ryonakayama234/DekaSugi/blob/a01662cc65190ab54ffab4b4daeb6b1429005701/docs/research/WORLD-PREREG-DRAFT-20261110-01-minimal-experiment.md)、blob `f0218f9454a92eb9512463be444f69e3c6fc7530`。
- [Lead R2 再審査 / B1〜B6](https://github.com/ryonakayama234/DekaSugi/pull/197)、[RQ2 Q1〜Q8](https://github.com/ryonakayama234/DekaSugi/blob/bb404739f675f7726ff79ffbc48298f049d95363/docs/research/WORLD-PREREG-RQ2-20261110-02-freeze-questions.md)、[監督者回答 6768141971](https://github.com/ryonakayama234/DekaSugi/pull/197#issuecomment-6768141971)、[Owner 採用 6768253225](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6768253225)。

**PASS** は、必要な設計上の定義・相互整合・決定規則が揃い、CAL 前に第三者が同じ判定を導ける状態（数値実測や実装完了は要求しない）。**PARTIAL** は主要な方針は成立するが、定義・権限・判定順序に補完が必要な状態。**FAIL** は、現行規定の同時成立が不可能、または主たる識別・推定ロジックが破綻し、その項目の PASS を阻む状態。

**総合: REVISE。B1 FAIL／B2 PARTIAL／B3 FAIL／B4 FAIL／B5 PARTIAL／B6 PARTIAL。PASS 0/6。設計合意未成立。** 数値が未凍結であること自体を不合格理由にしない。以下は仕様の論理的充足の評価であり、コード・CAL・実測の検証結果ではない。

## 1. B1〜B6 判定（項目別、対応節と根拠）

| blocking | 判定 | 仕様パックの根拠節 | 判定根拠・残る阻害 |
|---|---|---|---|
| **B1 goal contract・識別可能性** | **FAIL** | **§1**, §6 K0-a/b | デモ3対・事前一括・追加不可・別枠費用、TRAIN と評価の feedback 分離、公開履歴 `H_t` は前進。ただし §1 は「異なる law は同一 task_tag を共有しない」とし、`H_t` の第1成分に task_tag を含める。§6 K0-a は異なる必要行動の法則ペアで `H_0` の一致を要求する。異なる law の `H_0` は必ず異なり、証人集合が空になる。ID-only の CAL 統計検査ではこの定義矛盾を修復できない。デモ生成規則・11操作の合法性/終了契約も未列挙（v2 §1 の要求が存続）。 |
| **B2 grammar 全量・arm 到達可能空間** | **PARTIAL** | **§2**, **§3**, §6 アクセス表 | 5 node、型・arity、基本 constructor、深さ/ノード上限、8 arm の構築/USE 禁止が明示された。他方、評価器 BRANCH の v2 §4 との整合、観測特徴・束縛と評価順序・変数束縛の型域、predicate-slot の生成規則、prior/探索列挙順序、共有 read path の具体一覧がない。§2 の H+「空 snapshot から constructor 閉包」と §3 の H+「構築なし・探索のみ」を同じ候補空間として成立させる列挙規則が欠ける。FIXED-IF の贈与スキーマ、LOOKUP の距離・容量・abstain、REC の feature map/第一階 policy も未確定。 |
| **B3 K0-a/b/c・UNKNOWN** | **FAIL** | **§1**, **§6 K0**, §7 | K0 三段と STOP/UNKNOWN を表にしたことは改善。しかし B1 の tag/H0 矛盾により K0-a の PASS 証人を原理的に作れない。§6 の K0-a 不在時は「二階スキーマ必要性の主張のみ停止」とする記述が、存続する v2 §7 の「課題設計を STOP/REDESIGN」と衝突する。K0-c の `δ` は 0.15 AULC か 0.10 成功率差か不明。H≤64 手・列挙完全性・統計的上界と oracle 上界の組合せの定義も再現可能な算法になっていない。 |
| **B4 AULC・評価 n/route** | **FAIL** | **§4**, **§5** | 台形積分 /B、9 checkpoint、分母への ABSTAIN/INVALID 残存は PASS 相当の改善。ただし §5 は「復元 iid 抽出」と「同一 law 再出現は n に数えない」を同時に規定する。重複を除いた unique law 標本は一般に元の抽出分布の iid 標本でなく、再抽出数・重み付け・推定量が未定義のまま登録分布への推論は成立しない。さらに power 計算は主に「2ゲート」の Bonferroni のみで、7対照の最強事後選択、G1/G2、関連 cluster、AND ゲート全体の80% power を保証しない。4族内のテンプレート/パラメータ分布、`cost_cap`、`N_unique` 計算法が未確定で route 判定を完遂できない。 |
| **B5 帰属階層・等価性/null** | **PARTIAL** | **§3**, **§4**, **§6 キル条件** | FULL/OFF/REC/PRED-ONLY/RANK-ONLY 等の比較階層、K1 の実使用差、K2 の ±0.05 等価性域、K3 の陰性・小効果・不精確、K4 隔離の方向を規定。K2 の区間内包含は FULL と REC の**測定上の等価性**を支持し得るが「再符号化が機構を説明した」との因果帰属までは含まない。K3 の「小さい」は点推定のみで wide CI の INCONCLUSIVE と同時成立し得る。決定順序・比較集合・family 集約・多重性、K1 の診断集合選択と使用効果の結び付けが未確定。 |
| **B6 CAL/holdout 隔離・封印・改訂来歴** | **PARTIAL** | **§6 ログ/アクセス/receipt**, **§7** | CAL プロトコル承認→別 CAL GO→CAL→別事前登録凍結→実装/学習/評価に別 GO、を正しく分離。学習側/評価側アクセスと source-first digest、Issue #195 正本を規定。一方、生成器・分布・分割・分析・乱数源・権限・改訂可能フィールドの版/manifest schema、決定ログの形式、封印前後のアクセスと失敗時 fail-closed 基準は未指定。§5 に残る「仕様確定時に固定」「cost_cap は後日」等も CAL 前の裁量を残す。現行パックは Markdown の契約表・自然文であって、機械的に一意に再生できる完全 schema ではない。 |

### 論理的な停止点（最優先）

仕様パック §1 により `law_i ≠ law_j ⇒ tag_i ≠ tag_j`。同じ節により `tag` は `H_0` の構成要素。よって `law_i ≠ law_j ⇒ H_0(i) ≠ H_0(j)`。§6 K0-a にある「異なる必要行動の law ペアで H0 が同一」は不可能。これは予測力の検定ではなく、**同値関係と ID 発行規則の定義矛盾**である。たとえば law 非依存の不透明 ID の α-renaming を許して同値類を比較する、あるいは ID 付与を law 非一意に改訂する等、同値関係と漏洩検査を一体で再規定する必要がある（ここでは新方式を採用・凍結しない）。

また、元の分布で law A の抽出確率0.9、law B が0.1のとき、「2 unique law が揃うまで復元抽出し重複を除外」すれば評価集合は必ず A・B 各1になる。単純平均0.5は登録分布における平均0.9/0.1加重値を推定しない。**distinct law 数**を保証する方式と**iid 母集団推定**を同一視してはならない。重複 draw を保持して law-cluster として解析するか、unique 無復元抽出に対応した estimand と inclusion weight を事前固定する必要がある。

## 2. パック §0 の置換対象を除いた、ドラフト v2 との不整合

§0 が明示的に置換する **v2 §2 の「デモ経験予算への課金」／§5 の AULC 正規化／§10 の順序**は意図した改訂として数えない。以下は **置換範囲外** に残る不整合である。

| ID | v2 に存続する条項 | 仕様パックの条項 | 不整合と必要な調整 |
|---|---|---|---|
| C1（明示矛盾） | **v2 §4**: evaluator が提供する node を ATOM/SEQ/BIND/COMPARE「のみ」とする | **§2**: evaluator に第5の BRANCH を追加 | 評価器の seed grammar/branch semantics の境界が変わる。BRANCH は初期に利用可能な evaluator 機構なのか、学習後に登録される AST node なのかを一つの文法表に統合する。COMPARE/CMP の表記差も明示的に alias 化する。 |
| C2（明示矛盾） | **v2 §1**: buffer の「初期長 4〜12」 | **§4**: G2「初期 buffer 長 13〜16」 | G2 を OOD の明示的な例外として定義するか、v2 §1 の初期長制約を訓練時専用へ改訂する。中間 buffer 上限16自体とは別の問題。 |
| C3（明示矛盾） | **v2 §7 K0-a**: 証人が皆無なら「当該課題設計を STOP/REDESIGN」 | **§6 K0-a 注記**: 不在は「二階スキーマ必要性の主張のみを止め」、他の経験効率の問いを自動否定しない | 停止するのが課題生成設計全体か、二階帰属だけかが衝突。主張ごとの gate/STOP の遷移を一本化する。 |
| C4（明示矛盾） | **v2 §6**: iid draw を「各 draw 1 family」と数える | **§5**: 同じ law の再出現を独立 family と数えず「n は unique law 数」 | n の標本単位と推定対象が変更されている。duplicate draw の保存、cluster、重みと route を整合させる。 |
| C5（運用上の衝突） | **v2 §2**: tag は「法則を符号化しない」不透明な安定 ID | **§1**: law ごとに一意で同一 law では再使用 | 暗号的符号化はしなくても、同一フェーズで law を完全に指示する識別子になる。CAL ID-only の対象と H0 の同値関係が設計目的に合致するか明示する。 |
| C6（分母の読み分け不足） | **v2 §2**: 陰性・不可能・識別不能 family を分母に残す | **§4**: G2 容量到達不能類型は生成規則から事前除外し、元分母/除外数を報告 | 「生成前に除外した母集団」と「生成後に検出した不可能例」の区分、主分母/報告分母を固定しないと同じ数が二通りに計上される。 |

C5/C6 は明文の論理否定とまでは断定せず、**整合性を監査できない実質的な不一致**として別格にした。なお、パック**内部**にも §2 H+ の constructor 閉包と §3 H+ の「構築なし」という権限解釈の不整合があり、B2 で扱う。

## 3. 設計合意・次の意思決定

**結論: 設計合意は未成立。** Owner による Q1〜Q8 の採用は尊重し、その決定を再投票しない。しかし現行の実体化には、B1/B3 の証人不可能、B4 の標本・推定不整合、C1〜C4 の存続本文との衝突がある。**「残るのは Owner の CAL プロトコル承認のみ」には達していない。**

必要な順序は、(1) 監督者による B1/B3 の同値性と停止範囲の修正、B4 の標本/検定規則の修正、および C1〜C6 の整合化、(2) 対応表・生成分布・権限/計測 schema の完全化、(3) Lead による修正版 exact-head B1〜B6 再判定、(4) **その後初めて** Owner の CAL プロトコル承認判断へ進む、である。CAL GO はさらに別途必要で、CAL後の事前登録凍結、実装・学習・正式評価はその先の独立判断とする。

未解決の具体質問は別紙 [WORLD-PREREG-RQ3-20261110-03](WORLD-PREREG-RQ3-20261110-03-specpack-blockers.md) に分離した。結果の有利不利を確認するための事後改訂、対照の弱体化、holdout 参照、実装・校正の先行実行は認めない。

## 4. 検証と不実施

この審査で読んだのは GitHub 上の文書・採用コメントである。世界の動作、grammar 閉包、数式の経験的妥当性、CI の成功、デモ/法則分布の生成器、隔離機構の実装や CAL 観測結果を検証・実行したものではない。論理式と簡単な分布例は審査の説明であって正式シミュレーションではない。状態は **NOT_FROZEN / NOT_CALIBRATED / NOT_IMPLEMENTED / NOT_RUN** のまま。
