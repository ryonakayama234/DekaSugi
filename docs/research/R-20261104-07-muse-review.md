# R2-M方法v2案へのClaude精査 — 合格（未解決条件なし）、Owner採用判断へ

id: R-20261104-07-MUSE-REVIEW
status: review_passed / owner_adoption_pending / no_implementation / no_scoring
updated: 2026-11-04
tags: gate-r2-m-paper, claude-review, method-v2, causal-identification, m-use

> 本書は外部監督者Claude（ごま）による独立精査である。対象は [R2-M-20261104-SINGLE-METHOD-V2-PROPOSAL](R2-M-20261104-single-method-v2-proposal.md)（PR #174、head `0d7389457d53f57e2eba62b67bfd3758c35422cc`）。本書は方法v2の採用でも、R2-M-ENG・実験・採点の許可でもない。方法v2の採用はOwnerの別途決定を要し、それまでは[凍結された単一R0方法文書v1](https://github.com/ryonakayama234/DekaSugi/blob/docs/q-20261104-01-external-diagnosis/docs/research/GATE-R0-20261104-single-method.md)が唯一の有効な方法正本である。

## 1. 独立確認

- PR #174の差分は方法v2案の新規文書1件とINDEX登録のみ（INDEX側は日付更新と登録行）。main・凍結方法v1・既存コード・過去資産への変更はない。基点は現行main（PR #171マージ `67f5764`）。
- head `0d73894` のGitHub Actions run `41841665568` は **Success**。監督者環境で `python scripts/check_docs.py` もPASS。
- 数値の検算: コンパイル規則による木ASTは、係数1変数が1個で最大2ノード、2個で10ノード、3変数parity＋出力反転で **26ノード**となり、上限32の内側にある。STUMP-1の候補数は定数2＋3変数×4出力対＝**14**で文書と一致。識別証明（rank 4・一意復号）と非識別反例は前回精査 R-20261104-06 で検算済みの内容と同一で、改変されていない。

## 2. 指示項目との照合（Owner指示7項目＋精査条件2件）

| 項目 | 判定 | 根拠 |
|---|---|---|
| 1. 後継方法の全文（Domain/Hypothesis/Identification/Arms/Claims/Execution） | 合格 | §1〜§6に統合。3bit・公開4/8・private 4/8、F_aff 16法則、H0 8述語、記録契約、費用、STOP/INVALIDの継承を明記 |
| 2. 閉包マニフェスト／UNKNOWN宣言の様式 | 合格 | §4に様式 R2-M-CLOSURE-v2.0（YAML）。初期状態はUNKNOWNで理由も正直に記載され、COMPLETEの必要条件5点と「結果後の上書き救済禁止」まで固定 |
| 3. 族の事前仮定を開示する主張文の定型 | 合格 | §6に変更不可の定型として収録。「識別＋外部化＋因果的使用」までの限定と、STATIC同成績時の併記義務を含む |
| 4. 表現修復は別軸ポインタのみ | 合格 | §8に非起動のポインタとして分離。本方法では評価しないと明記 |
| 5. 合成器契約の二者択一の固定（精査条件1） | 合格 | §2.1で (a) 係数復号を唯一の契約として選択し、(b) を不採用と明示。コンパイル規則（変数順・左結合・d=1での最終NOT・木として展開・上限32）まで決定的に固定され、暗黙の候補選択の余地がない |
| 6. 対照マニフェストの版凍結（精査条件2） | 合格 | §3に R2-M-CONTROLS-v2.0 として arm集合・容量・tie規則・費用計数を固定。結果後の変更はINVALID。episodic容量は人工削減なし（最大8点＝世界全域） |
| 7. R1-ENG P2注記の前方契約 | 合格 | §5に `ast_nodes_static`／`node_visits_runtime`／`primitive_ops_runtime` の分離（短絡評価を実測で数える）と、Snapshot pathの絶対正規化を明記。過去のR1実測値は変更しない |

## 3. 評価する点

1. **「知識の開示」と「実行時接続」の区別**（§2.2）。F_aff/decoderの仕様を全armに開示することと、OFFのdispatchにdecoder経路が接続済みかどうかは別だ、という切り分けが、RQ2への監督者回答を正確に実装している。OFFに最初からdecoder経路があるなら保持し、切断した比較はINVALID、という行が特に重要。
2. **F01/F11（学習policy arm）の扱いの正直さ**。仕様をこの版で完全固定できない場合は両armをNOT_EVALUATEDとし、結果後に有利な方策を混ぜない、と先に宣言している。
3. **FIXED-MACRO armの設計**。16法則全部を事前登録し、個別targetに応じた選別注入を禁止しているため、「人間が用意したライブラリからの選択」との区別が検査可能になっている。
4. 閉包マニフェストの初期値がUNKNOWNのまま提出されている。埋められる欄だけ埋めて完全と称する、という前例の失敗を繰り返していない。

## 4. P1注記（合格を妨げない、実装scope検討時に扱う事項）

1. §2.1の `candidate_budget=16` は族サイズ由来の上限であり、decoderが実際に生成する候補は1個である。文書自身が「候補生成0/1個と16法則の事前開示を別記」と定めているので矛盾ではないが、将来の費用台帳ではこの区別どおりに記録すること。
2. §3のF00固定dispatch連鎖（episodic → H0_object走査 → その他経路 → ABSTAIN）は**提案版の契約**である。将来の実装では§4の閉包監査が実在の初期系を記述するものでなければならず、実在しない経路をOFFへ足すことも、実在する経路を落とすこともしない。文書も「隠れ経路が見つかれば§4へ戻す」と定めており整合している。
3. 最初のM_use証拠は F10−F00（固定policy同士）に絞られる設計でよい。policy学習armは後継版と別許可に委ねられている。

## 5. 監督者の判定と勧告

**判定: 合格。未解決の条件はない。**

勧告: **方法v2を後継方法として採用すること。** ただし採用の効力は「将来のR2-M-ENGをこの方法の下で設計・審査できる」ことまでで、実装GO・実験・採点は依然として別のOwner許可を要する。採用後も、凍結方法v1とR1-ENGの結果（M_use未認定、他はNOT_EVALUATED）はそのまま残る。

| 項目 | 状態 |
|---|---|
| 方法v2案（PR #174） | 提出済み・Claude精査合格 |
| 方法v2の採用 | Owner未決定（監督者勧告: 採用） |
| R2-M-ENGのscope提案 | 未着手（v2採用後にLeadへ依頼するかどうかをOwnerが判断） |
| 実装・実験・採点 | 未許可 |
| 現在の認定 | M_use NOT_CERTIFIED、M_gap UNKNOWN、N_rep/U/T NOT_EVALUATED |
| PR #174のマージ | 未実施・未承認（他のDraft PRと同様、別途判断） |
