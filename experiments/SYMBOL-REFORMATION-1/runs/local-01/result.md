# SYMBOL-REFORMATION-1 結果票

id: SYMBOL-REFORMATION-1-RESULT
status: local_engineering_complete_muse_pending
updated: 2026-11-18
tags: training, engineering, reformation

旧試験・予測器・学習再実行を使わない、訓練側の一巡診断。候補はcandidateのまま。

|方式|前AST|後AST|新規|新規支持≧2|新規反例あり|新規の不適用行数|
|---|---:|---:|---:|---:|---:|---:|
|FULL|184|184|0|0|0|0|
|NO-CHUNK|180|180|0|0|0|0|

両方式の前集合・NO-CHUNK後集合・FULL文字形成を除いたchunk固有の新規AST: **0件**。そのうち異なる生文字列2件以上の支持: **0件**。
これは候補形成の結果であり、有効な未見予測・ブートストラップ能力の証拠にはしない。

|方式|行ペア|形成試行|既存AST再発見イベント|再形成内重複イベント|両経路AST|
|---|---:|---:|---:|---:|---:|
|FULL|153|4284|334|154|0|
|NO-CHUNK|153|2142|334|154|0|

再発見と再形成内重複は重なり得る独立カウンタ。全不成立試行・出力0件もtrials.jsonに保持。
候補別AST・形成元位置・chunk獲得episode・支持match・反例・不適用はdiagnostic.jsonとevents.jsonで照合する。
支持の分母は18種類であり、54観測や再形成回数を追加支持にしない。適用範囲もこの18行に限る。

状態digest（前後一致）: `046268747906ca787d7d9a79dad4dd5b8ea5cc3f01b3c64f111598aed8969c56`。
固定計画SHA256: `0a5d3bb4f3e43f474c6d293ce2c11e8e91dbc949b855a4f87f991922c07f75a8`。実行source: `6f0084906ea167b7362bab143f6f3555cefc9fb2`。

CPU/wall・全操作と内訳・ファイルbyteはcost.json。COMPLETE.jsonとSHA256SUMS.jsonの読戻しを要する。
Muse独立確認は未実施。旧負の所見を維持し、条件を変えて成功例を探さずこの診断を閉じる。
