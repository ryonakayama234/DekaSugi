# EXP-0001 — Pre-registered plan: deterministic typed enumerator

id: EXP-0001-PLAN
status: planned
updated: 2026-10-24
tags: experiment, baseline, synthesis, preregistration

**これは実験計画であり、実測結果ではない。** 実行前に合否を固定する。

## Hypothesis / 仮説
H1: 文字列→文字列の型付きDSLで、`trim` / `lower` / `upper` の合成をノード数昇順に列挙すると、少数の入出力例から対応プログラムを探索できる。
H0: 与えた探索上限内に適合プログラムが見つからない。
**主張対象は合成器の正常動作のみ**。抽象能力・汎化・継続学習の実証は後続実験で行う。

## Scope / 設定
- 入力: String、出力: String。AST: `input`, `call(allowed_operation, child)`。
- 許可演算: `trim`, `lower`, `upper`。その他のコード生成・ネットワーク・任意Python実行は禁止。
- 全探索: ASTノード数最大4、評価する候補最大5000。決定的な走査順。
- 純粋な例照合で判定。すべての例を満たす最初のプログラムを返す。

## Dataset design / ケース
機能確認用の公開タスク（これらは**汎化ベンチマークではない**）。
1. `"abc"→"abc"`, `"z"→"z"` — identity
2. `" x "→"x"`, `"  y"→"y"` — trim
3. `"HI"→"hi"`, `"Z"→"z"` — lower
4. `" RED "→"red"`, `" Blue "→"blue"` — trim + lower
5. `"ab"→"ba"` — 解答に必要なreverse演算がないため `not_found` を期待
6. case 4を `max_candidates=1` で実行 — `budget_exhausted` を期待
7. 事前に壊した型/未知opを与える — 評価前に拒否を期待

## Conditions & baseline / 比較条件
- baseline A: 制限付きDSL全列挙（技能ライブラリなし）。
- EXP-0001はbaseline Aの機能検証のみ。学習あり条件との比較は**EXP-0002以降**。
- 各タスクで候補数・ASTノード数・wall time・成功/失敗/打切り理由を記録する。
- 速度の絶対値は環境依存。探索候補数と決定性を主な再現性指標にする。

## Metrics / 指標
- 全例に適合した正答ASTの割合（cases 1–4）。
- 不可能/予算制限条件での期待終了理由（cases 5–7）。
- `tested_candidates`, `max_nodes`, `elapsed_ms`, 返却ASTの正規化JSON。
- 同一条件の2回実行で探索順、候補数、ASTが同一か。

## Acceptance / EXP-0001の合否判定
**PASS:** case 1–4がすべて適合し、case 5–7が正しく拒否/終了し、候補上限を守り、同一条件の2回実行で探索候補数とASTが一致。関連するユニットテストとドキュメント検査が成功する。
**FAIL:** 上記のいずれかを満たさない。
**INCONCLUSIVE:** 実行不能、環境情報や出力ログの欠損などにより判定不能。

これは設計上の機能検査であり、未知課題での能力向上を示すものではない。

## Protocol / 実行手順（実装後に固定）
実装PRで、再現可能なCLIコマンドとタスクファイル、Python/OS/CPUの記録方法を確定する。今は**未実装・未実行**。手順変更の際は理由と版を記載する。

## Expected confounders / 既知の制約
- 与えられた例だけでは本来意図した関数と別の式が同じ出力を返す可能性がある。
- 公開した少数課題だけでは統計的な一般化を主張できない。
- `trim` のUnicode空白の扱い、`lower` のUnicode変換に依存する。実装で仕様とPython版を固定する。
- 構造的重複を除いても、意味的に同値な式の重複は残る。

## Outputs / 記録の保管
新規runごとに `runs/YYYYMMDD-HHMM-<commit>.md` と機械可読の結果（小容量のみ）を置く。
[runの説明](runs/README.md) / [仕様](../../docs/specs/EXP-0001.md) / [記録テンプレート](../../docs/templates/experiment.md)。
