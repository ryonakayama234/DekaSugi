# EXP-0002B — PROPOSED experiment plan (not preregistered yet)

id: EXP-0002B-PLAN
status: planned; NOT preregistered; NOT executed
updated: 2026-10-24
tags: experiment, policy, contextual-kernel, design, holdout

> **研究設計案であり事前登録済み評価ではない。** 既存のEXP-0002最終評価データを学習・採用判断に再利用しない。実装前に、この計画の仕様を別commitでfreezeし、以降は結果に合わせて編集しない。

## Hypothesis / 仮説
H1: 入出力例から抽出した課題特徴に基づき、新技能を使用するか否かを訓練エピソードから予測できる。
H2: 選択方策の学習により、技能を常に有効化する条件よりも無駄な探索と原始演算を抑制できる。
H3: 分布が変わると選択方策の利点は消失し得る。未知文脈で安全にOFFへ戻せることが重要。

## Scope / 対象
- 最初の行動空間: `OFF` / `ON(skill_8fe1361cb5014f85)`。ただしPR #6のレビューと安全境界の確定後にのみ技能を使用。
- 課題は `String → String` の型付きDSL。新しいプリミティブは導入せず、同一探索上限で比較。
- 入力情報は**解答前**に与えられるTaskSpec（例のinput/outputを含む）と承認済み技能メタデータのみ。
- 特徴候補は入出力例の個数、文字列長・変化量、境界空白、大/小文字の比率、identity比率等。確定次第vector schemaを別commitに固定する。
- 訓練課題では両armを実行し、verified correctness, candidate evaluations, **primitive invocations**, wall timeの対比較を学習信号とする。
- 近傍型または表形式の小モデルを先行候補とする。アルゴリズム、正規化、近傍数、閾値、fallback閾値を**実装前に固定**。

## Dataset / データ分割（現時点は案）
- train / development / final_holdoutをfamilyとseed、文字列テンプレートで分離。恒等、trim、lower、upper、合成、不可解問題、混合ノイズを最低限含める。
- 訓練で成果が出たfamilyだけを最終評価へ持ち込まない。未出現family/新種のノイズなどのOOD課題を別に用意する。
- 例題を増やす際、入力文字列を変えただけの同一関数の複製を独立試行として過大計上しない。
- データ生成器が正解programを持っていても、Kernelが利用できる入力には混入させない。
- 課題数・seed・dataset hash・例外処理を実装前に確定する。

## Conditions / 比較
1. Always-OFF = fixed primitive baseline.
2. Always-ON = all current candidate skills enabled.
3. LEARNED = Kernel policy, with abstention-to-OFF.
4. ORACLE = hindsight best arm; upper-bound diagnosis only.

## Metrics / 指標
- 各課題・全体・family別の正答率、候補評価数、原始演算呼出数、wall timeの中央値・p90・悪化例数。
- 選択方策の真の推論/特徴抽出コスト、学習オーバーヘッド、技能body展開後ノード数。
- ONを選ぶべきでなかった課題でONと判定した率、技能を使う方が良い課題でOFFと判定した率。
- 既知familyとOODの成績を別々に報告。平均だけでなくworst-case cost、budget exhaustion、分割ごとのnを示す。
- メトリクスを測りづらい場合は不明と報告し、wall timeの揺らぎを主成果にしない。

## Acceptance / 事前登録前の受入方針
- Correctness/safety/regression must be non-inferior to the fixed-baseline within measurement uncertainty.
- Learningを主張するには、全ての方策の設計や閾値を固定した上で新しい最終課題を評価し、**Always-ONに対する実コスト低減**とAlways-OFFに対する影響を報告する。
- Always-ONだけに勝ってAlways-OFFに勝てない場合、「選択方策による安全な抑制」はあり得るが「全体能力の向上」は主張しない。
- 意思決定の確信度が不足する場合にはOFFへ戻り、取り返しのつかない外部操作は禁止。
- 数値採用閾値、サンプル数、初期方策と学習方式、既存課題との漏洩監査を実装前に確定するまでこのplanを `preregistered` と呼ばない。
- 実験runには失敗も保存し、独立コードレビュー・資料更新まで採用しない。

## Reproduction / 現時点
**未実装、コマンド・実験runなし。** 後続の実装PRで具体的なCLIコマンド、版管理とGitHub Actions artifactを確定する。

[Specification](../../docs/specs/EXP-0002B.md) / [Data contracts](../../docs/architecture/contracts.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7)。
