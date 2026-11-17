# SYMBOL-BOOTSTRAP-1 結果票

id: SYMBOL-BOOTSTRAP-1-RUN
status: COMPLETE
updated: 2026-11-17
tags: artificial, engineering, bootstrap

固定上限・選択順は先行の別commit。人工工学確認のみ。Museの独立確認は未実施。

実行ソース: `ab77a851347a90fce870f0149952458e663b17ff`。固定JSON SHA256: `cc9c4f5275a6d9e6af972caa98eb2d8a24464dc1ee8395d73fd128ca446a4457`。

|分類|件数|FULL|NO-LEARN|NO-CHUNK|MEMORY|
|---|---:|---:|---:|---:|---:|
|a|4|4|0|4|4|
|b1|4|4|0|4|0|
|b2|2|2|0|2|0|
|b|6|6|0|6|0|
|c|4|4|0|4|0|

解釈: `unseen_prediction_observed_chunk_contribution_unconfirmed`。分類別の勝ち／負け／同点・棄権はJSONに収録。
NO-CHUNKやMEMORYと同程度なら、自作したまとまりの寄与は未確認。一般能力・意味理解の認定はしない。

|分類/ID|方式|prefix|期待|予測|正誤|経路|
|---|---|---|---|---|---|---|
|a-1|FULL|dax\|mip>|daxmip;|daxmip;|True|rule|
|a-1|NO-LEARN|dax\|mip>|daxmip;|;;;;;;;|False|ngram|
|a-1|NO-CHUNK|dax\|mip>|daxmip;|daxmip;|True|rule|
|a-1|MEMORY|dax\|mip>|daxmip;|daxmip;|True|memory|
|a-2|FULL|dax\|mip<|mipdax;|mipdax;|True|rule|
|a-2|NO-LEARN|dax\|mip<|mipdax;|;;;;;;;|False|ngram|
|a-2|NO-CHUNK|dax\|mip<|mipdax;|mipdax;|True|rule|
|a-2|MEMORY|dax\|mip<|mipdax;|mipdax;|True|memory|
|a-3|FULL|mip\|nuv>|mipnuv;|mipnuv;|True|rule|
|a-3|NO-LEARN|mip\|nuv>|mipnuv;|;;;;;;;|False|ngram|
|a-3|NO-CHUNK|mip\|nuv>|mipnuv;|mipnuv;|True|rule|
|a-3|MEMORY|mip\|nuv>|mipnuv;|mipnuv;|True|memory|
|a-4|FULL|zok\|nuv<|nuvzok;|nuvzok;|True|rule|
|a-4|NO-LEARN|zok\|nuv<|nuvzok;|;;;;;;;|False|ngram|
|a-4|NO-CHUNK|zok\|nuv<|nuvzok;|nuvzok;|True|rule|
|a-4|MEMORY|zok\|nuv<|nuvzok;|nuvzok;|True|memory|
|b1-1|FULL|dax\|nuv>|daxnuv;|daxnuv;|True|rule|
|b1-1|NO-LEARN|dax\|nuv>|daxnuv;|;;;;;;;|False|ngram|
|b1-1|NO-CHUNK|dax\|nuv>|daxnuv;|daxnuv;|True|rule|
|b1-1|MEMORY|dax\|nuv>|daxnuv;|mipdax;|False|ngram|
|b1-2|FULL|dax\|nuv<|nuvdax;|nuvdax;|True|rule|
|b1-2|NO-LEARN|dax\|nuv<|nuvdax;|;;;;;;;|False|ngram|
|b1-2|NO-CHUNK|dax\|nuv<|nuvdax;|nuvdax;|True|rule|
|b1-2|MEMORY|dax\|nuv<|nuvdax;|nuvmip;|False|ngram|
|b1-3|FULL|nuv\|dax>|nuvdax;|nuvdax;|True|rule|
|b1-3|NO-LEARN|nuv\|dax>|nuvdax;|;;;;;;;|False|ngram|
|b1-3|NO-CHUNK|nuv\|dax>|nuvdax;|nuvdax;|True|rule|
|b1-3|MEMORY|nuv\|dax>|nuvdax;|mipdax;|False|ngram|
|b1-4|FULL|nuv\|dax<|daxnuv;|daxnuv;|True|rule|
|b1-4|NO-LEARN|nuv\|dax<|daxnuv;|;;;;;;;|False|ngram|
|b1-4|NO-CHUNK|nuv\|dax<|daxnuv;|daxnuv;|True|rule|
|b1-4|MEMORY|nuv\|dax<|daxnuv;|daxmip;|False|ngram|
|b2-1|FULL|mip\|zok<|zokmip;|zokmip;|True|rule|
|b2-1|NO-LEARN|mip\|zok<|zokmip;|;;;;;;;|False|ngram|
|b2-1|NO-CHUNK|mip\|zok<|zokmip;|zokmip;|True|rule|
|b2-1|MEMORY|mip\|zok<|zokmip;|zokdax;|False|ngram|
|b2-2|FULL|zok\|mip<|mipzok;|mipzok;|True|rule|
|b2-2|NO-LEARN|zok\|mip<|mipzok;|;;;;;;;|False|ngram|
|b2-2|NO-CHUNK|zok\|mip<|mipzok;|mipzok;|True|rule|
|b2-2|MEMORY|zok\|mip<|mipzok;|mipdax;|False|ngram|
|c-1|FULL|qef\|wyg>|qefwyg;|qefwyg;|True|rule|
|c-1|NO-LEARN|qef\|wyg>|qefwyg;|;;;;;;;|False|ngram|
|c-1|NO-CHUNK|qef\|wyg>|qefwyg;|qefwyg;|True|rule|
|c-1|MEMORY|qef\|wyg>|qefwyg;|mipdax;|False|ngram|
|c-2|FULL|qef\|wyg<|wygqef;|wygqef;|True|rule|
|c-2|NO-LEARN|qef\|wyg<|wygqef;|;;;;;;;|False|ngram|
|c-2|NO-CHUNK|qef\|wyg<|wygqef;|wygqef;|True|rule|
|c-2|MEMORY|qef\|wyg<|wygqef;|daxmip;|False|ngram|
|c-3|FULL|wyg\|qef>|wygqef;|wygqef;|True|rule|
|c-3|NO-LEARN|wyg\|qef>|wygqef;|;;;;;;;|False|ngram|
|c-3|NO-CHUNK|wyg\|qef>|wygqef;|wygqef;|True|rule|
|c-3|MEMORY|wyg\|qef>|wygqef;|mipdax;|False|ngram|
|c-4|FULL|wyg\|qef<|qefwyg;|qefwyg;|True|rule|
|c-4|NO-LEARN|wyg\|qef<|qefwyg;|;;;;;;;|False|ngram|
|c-4|NO-CHUNK|wyg\|qef<|qefwyg;|qefwyg;|True|rule|
|c-4|MEMORY|wyg\|qef<|qefwyg;|daxmip;|False|ngram|

生の記録: `report.json`（全56予測・来歴参照・候補競合・prefix/期待/予測）。
`states.json` は全候補・元episode/文字位置・chunkの依存DAG・支持/反例、`history.json` は入力順の増減と事前予測。
処理費用は `cost.json`。CPU/wallは実測値、candidate/primitive countersとは別。
結果を見て条件を延長・調整しない。E1・既存研究・マージは範囲外。
