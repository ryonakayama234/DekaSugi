# R1-ENG-2BIT — M_use 工学診断fixture（科学採点ではない）

id: R1-ENG-2BIT
status: implemented_engineering_pending_independent_review / no_scientific_scoring
updated: 2026-11-04
tags: r1-eng, m-use, engineering-only, finite-fixtures, public-boundary

> **最初に固定するOFF介入契約:** body OFF時も、**同一のimmutable Snapshotに含まれる非学習body経路**（6個のH0_object候補・固定Kernel dispatch規則・episodic retrieval / lookupなど、この診断に実装したもの）はすべて維持する。ここでは初期policyは lookup-first → H0一致候補 → ABSTAIN、入力別の特別な学習済み分岐は持たない。**STATIC-H+ / fixed macroは別armの科学的対照**であり、同じSnapshotのbody OFFに混入させない。本仕様は科学的なH0_effective(B)の網羅証明を提供しない。

**正本:** [PR #170 Owner R0-E/R1-ENG決定](https://github.com/ryonakayama234/DekaSugi/pull/170#issuecomment-6629702043)。[凍結された単一R0方法書](https://github.com/ryonakayama234/DekaSugi/blob/docs/q-20261104-01-external-diagnosis/docs/research/GATE-R0-20261104-single-method.md) §2〜§7。#170はDraft・未マージであり、その本文・方法を本PRで複製・改訂しない。ここでは許可された2bit N/S/R/Eの工学fixtureのみ扱う。

## 実装境界

~~~mermaid
flowchart LR
  Source["source: private finite law"] --> Public["public gateway: initial P / legal Q / precommit / paid answer"]
  Public --> Learner["learner: H0 scan / typed AND OR NOT synthesis"]
  Learner --> Validator["independent public-only validator"]
  Validator --> Sleep["Sleep-lite: semantic-preserving canonical order + receipt"]
  Sleep --> Snapshot["Snapshot/v1: immutable persisted digest"]
  Snapshot --> Fresh["new Python process: real dispatch ON"]
  Snapshot --> Off["new Python process: same snapshot OFF"]
  Off --> Fallback["episodic lookup / all H0 / ABSTAIN"]
  Fresh --> Compare["prediction / legal action comparison"]
  Fallback --> Compare
~~~

- packages/r1_eng/fixture.py: source-private finite law and legal paid-Q gateway. PrivateSource never enters synthesize_public, validate_public, Snapshot or fresh process. The role boundary is explicit Python call discipline, **not a hostile in-process sandbox**.
- packages/r1_eng/core.py: exact 2-bit public observations, deterministic H0 enumeration, bounded typed Bool AST synthesis from observed (input, output) pairs only, purely semantically preserving Sleep-lite ordering, exclusive-create Snapshot, verified restoration and dispatch.
- packages/r1_eng/validator.py: interpreter distinct from synthesis interpreter; checks typed operators, node bound, already-public observations and receipts, no private law input.
- packages/r1_eng/runner.py: fixed nonlearned query selection, operator-only finite paper proof, immutable snapshot, separate Python processes for ON and OFF over the 4 publicly disclosed R inputs.
- packages/r1_eng/__main__.py: read-only process that loads Snapshot and dispatches only; imports no source/heldout evaluator.
- tests/test_r1_eng_2bit.py: isolated artificial fixture tests, no historical scorer/dataset/generator/heldout import or reexecution.

## 有限fixtureと診断上限

| Case | source-private alternatives / public contract | public-only action | engineering status and limit |
|---|---|---|---|
| N | A=x、B=x AND !z。legal Q=00,01,10。budget=1。terminal 11は禁止 | 固定Q00、予測事前commit | evaluator-side finite proof: all legal Q indistinguishable、terminal 11 differs。UNIDENTIFIABLE。獲得失敗扱いしない |
| S | A=x、B=!x。legal Q00、budget=1 | 固定Q00、予測事前commit | evaluator-side proof: Q separates two H0 laws。SUFFICIENT_H0。1点公開だけでlearnerが未知全域で正解したとの主張ではない |
| R | A=XOR、B=OR。initial public P=00→0,01→1,10→1。legal Q11、budget=1 | 6個のH0全不整合→commit→Q11→public-only AST synthesis→independent validation→Sleep-lite→Snapshot→fresh USE/ OFF | MISMATCH_CANDIDATE（**H0_objectのみ**）。全4点公開済みで未見汎化ではない。実効閉包の不足・M_gap・N_rep・U・Tは認定しない |
| E | source=x。initial public 00→0,10→1。H0 enum順=0,1,!x,!z,z,x。budget=5 candidates（Qはなし） | 最初の5候補を照合してSTOP | SEARCH_INCOMPLETE。6番目のxは適合。探索不足を表現不足と誤診しない |

N/Sのlaw候補とRの真理値表は**operator/evaluator側の有限証明fixture**。それらをlearnerに注入せず、test結果を独立family・科学的positiveと呼ばない。Rの初期P・Q回答以外は合成器に渡さない。

## 型・API・不変条件

- Public observation: seq, point [x,z], answer 0|1, paid 0|1, legal_digest, precommit。初期公開分はpaid=0、照会は事前commit・予算・合法集合・一意性必須。禁止Q、未来回答、未commit照会はINVALID停止。target AST・seed・private law・variant・hidden familyは公開recordに置かない。
- Bool AST: type=Bool, op∈{x,z,NOT,AND,OR}、NOT単項、AND/OR二項、最大9 nodes、候補最大10,000。pure operationsのみ、任意Python実行なし。合成は公開recordの一致による候補探索であり、XOR/ORのtarget ASTや事前macroを注入しない。
- Independent validator: 別実装の純粋Boolean interpreterが公開点への一致・型・node boundsを検査。Sleep-liteはAND/OR引数の可換順序正規化のみ。意味の異なる候補の採否は行わず、receipt/digestを保存する。
- Snapshot/v1: parent、grammar、H0 registry、policyの版・digest、公開観測、canonical AST、validator receipt、内容SHA-256。ファイルはexclusive-createで上書き拒否、復元時hash・schema・型・public validation再照合。ハッシュはローカル整合性を保証するが独立custodyやtrusted timestampではない。
- USE: 同じSnapshotをfresh Python processでON/OFF読込。available/selected/executed/finishedを区別。ONが登録bodyを実行、OFFは**同じrecordsのepisodic lookupを優先**し、次に全H0一致候補を維持、最後にABSTAIN。両条件ともactionとprediction、routeを記録。route差だけではM_use陽性にしない。
- M_use_engineeringは予測・合法行動の差がなければ not_certified_no_prediction_or_action_delta と記載。**Rでは全4点のepisodic lookupが利用可能であり、ONとOFFの予測差は発生しない想定**。これを隠したりfallbackを削ったりしない。科学的M_useの合格宣言ではなく工学動作診断である。
- paid Qは各1。候補列挙数、validatorの公開一致、Snapshot SHAを個別記録。CPU/生涯総費用、STATIC-H+、fixed macro、独立family対照などは本PRでは**NOT_EVALUATED**。固定queryは学習型Active Learningではない。
- Rのfresh USEは同じ2bit入力全4点の再提示。永続化とdispatchの工学確認に過ぎず、heldout、fresh generalization、独立family転移、科学的採点ではない。過去の封印評価・TRAIN/DEV/FINALと旧評価器を一切用いない。

## 工学テスト（科学採点ではない）

~~~bash
python -m unittest tests.test_r1_eng_2bit -v
python scripts/check_docs.py
~~~

工学証拠は別PRのactual CI/テスト結果とlatest-head独立受入レビューで確認する。テスト成功だけで M_use / M_gap / N_rep / U / T の正式判定、科学的採用、#170マージ、R1範囲拡張を行わない。
