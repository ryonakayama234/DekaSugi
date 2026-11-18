# SYMBOL-REFORMATION-1 — 訓練側再形成診断の実行前固定

id: SYMBOL-REFORMATION-1-PLAN
status: frozen_before_implementation_and_execution
updated: 2026-11-18
tags: engineering, training, reformation

## 授権・問い・境界

Issue #227 [提案6969127228](https://github.com/ryonakayama234/DekaSugi/issues/227#issuecomment-6969127228) と [Owner GO6969285381](https://github.com/ryonakayama234/DekaSugi/issues/227#issuecomment-6969285381) の制作。旧結果「未見予測は観測されたが、自作したまとまりの寄与は未確認」は変更しない。

問いは、終了辞書で再訪すると、両方式の再形成前にもNO-CHUNK再形成後にもなく、FULL文字経路でも形成されないcanonical ASTを、先に獲得したchunkから形成するか。その支持が異なる生文字列2件以上か。代替は新規0件、既存再発見のみ、文字側と重複、反例付き候補のみ。どの結果でも一巡で閉じる。能力採用・未見予測評価ではない。

## 入力と固定状態

基点 `f27ca585aa9006e48a17cbe8e40f12d7ea231a05` の `experiments/SYMBOL-BOOTSTRAP-1/runs/local-02/evidence.zip` (SHA256 `d050df3d1caa06203036b15c20e2a6881581133f1ad51d9ed5756666ee1d54e5`) から **states.jsonだけ** (SHA256 `b28875765b21e0b3603fb750a4fa8e7283d9322efd2b3b286de708aba4cdb7fd`) を読む。report/history/cost/result/旧lockは開かず、予測・得点を渡さない。学習を再実行しない。

FULL/NO-CHUNKの54観測から、最初の出現順の18種類を取り出す。両方式の観測台帳の完全一致、3巡反復を検証。各行の最初のepisodeと生文字列を来歴にする。辞書、旧規則、観測、支持履歴は読取り専用。診断後に状態digestが一致すること。診断の新候補は別のcandidate表に隔離し、旧stateへ登録しない。

## 順序・文法・前後比較

方式はFULL、NO-CHUNKの順。異なる行の無順序ペア153組を、後の行index i=1..17、先のj=0..i-1の順で一度だけ訪問する。prefixの共通文字split=1..min(length)-1の昇順。FULLはsymbol→character、NO-CHUNKはcharacterのみ。旧 `_pattern` / `_outputs` / `_fit` の文字・束縛・照合・連結文法をそのまま用いる。symbol分割は終了辞書の最長一致、Unicode同率順。出力ASTはcanonical JSONの昇順。変数最大2、各1..6文字、input/output literal各8、copy参照4、output atom16、展開32文字。chunk長2..8、4096件まで。順位付け・予測は呼ばない。

AST同一性はpattern/outputのcanonical JSON（文字literalへ展開した構文上の同一性）。R-IDだけでなく完全ASTを比較し、衝突はINVALID。各方式で前集合を保ち、新規/既存再発見を分離。全形成イベントにはrow pair、split、変数位置、chunk ID・獲得episode・prefix内半開位置、再形成イベントIDを持たせる。同じASTの全形成経路を保持する。新たな観測episodeは作らない。

前後の全ASTに、18種類それぞれのsupport/failure/inapplicableを検査。支持は既知行をprefixとして照合した全束縛のうち1つでもsuffixに完全一致、failureは適用可能で一致なし、不適用は束縛なし。件数はunique生文字列単位。54件や再訪回数で水増ししない。支持matchのsplit/bindingsと、反例・不適用の行IDを保存する。適用範囲はこの18行に限り、一般的な適用可能領域とは主張しない。

## 全保持上限・計数（結果前に固定）

|対象|単一runの上限・規則|
|---|---|
|CPU / wall|各120秒。入力検証から集計・保存まで、両方式を含む。定期checkとプロセスの時間制限を併用|
|総操作|20,000,000。既存文法のformation_attempt/token_scan/output_search_node/match_node/expand_atom等のtickに加え、入力byte・JSON値/文字、ペア、文字token構成、候補/イベント保持、差集合/支持集計、出力JSON値/文字・書込byteを計数。byteは1024byteを1単位に切上げ、JSONは各値とkey/stringの各文字を1単位。CPU命令数ではない|
|状態入力|archive 50,000,000 byte、states展開20,000,000 byte、JSON深度64、値/文字の総操作上限。FULL/NO-CHUNK各54行・18種類・行32文字以内|
|候補|各方式、既存を含む4096 AST。片方式だけ枠を増やさない|
|形成|各方式16384試行、各patternのoutput探索4096 node。全試行（不成立・出力0含む）を保持|
|形成イベント|両方式合計65536出力AST出現。重複・別経路も含み、切捨てなし|
|支持cache|両方式計147456件 (=2×4096×18)。18行の状態を全保持|
|chunk位置|各形成イベントは2prefix各32 token以下。終了辞書の獲得時点と一致を検証|
|成果物|全生成ファイルの非圧縮byte合計50,000,000、結果票・hash目録・費用記録も含む。旧入力は含めない。保存後読戻し・digest照合も計数|

各保持/出力で先に上限を検査し、超過はRESOURCE_STOP。部分記録は未完と明記し、summary/主問いの結論を出さない。停止用小票だけは予約した16KB以内で書き、上記50MBに含める（操作/時間超過後の緊急停止記録は別計数で、完走には使わない）。延長・剪定・条件変更は禁止。入力/来歴/状態破損はINVALIDとして停止する。

## 提出と独立確認

この固定文書を実装・人工確認より先の別commitに置く。短いresult.md、全AST/18行判定、全試行・形成来歴、前後集合、入力/実行ソース/固定計画SHA、費用と保存読戻しhashを提出する。新規0件・重複・反例も表へ明記。MuseはVMで固定状態、順序、支持/反例、形成依存、費用を独立確認する。

新予測、実入力収集、E1統合/完了、symbol優先への順位変更、旧試験調整、領域/seed追加、3D、モデル採用、mainマージは含まない。
