# EXP-0002 — Preregistered skill discovery and search comparison

id: EXP-0002-PLAN
status: preregistered
updated: 2026-10-24
tags: exp0002, preregistration, macro, heldout, learning

> この計画は実装・新実験runより**先に**コミットする。失敗しても変更せず、変更が必要なら別versionを作る。EXP-0001は固定DSLの非学習baseline。

## Hypothesis / 仮説
- H1: 独立した訓練課題の解法ASTから共通部分式を決定的に抽出し、型付きmacroとして安全に再利用できる。
- H2: 得たmacroは、同族だが入力値が未知の評価課題で、同じ候補評価上限内の探索候補数を削減する。
- H3: macroの安易な追加は探索空間を膨張させ、未知の不可能課題で候補数を増やす。
- 帰無仮説: 技能は発見できない、あるいは正例に有用でも全体の探索効率は改善しない。

## Scope / データと介入
- 既存の `String -> String` DSL、`trim/lower/upper` のみを原始演算とする。任意のPythonを合成・実行しない。
- Training (`train`): T1 `"  RED " -> "red", " Blue " -> "blue"`; T2 `"  Open " -> "open", " PENDING  " -> "pending"`。どちらもEXP-0001の既知課題と同型の別エピソード。**訓練データ独立性の強い主張はしない**。
- Development (`dev`): D1 `" Foo " -> "foo", "  BAR " -> "bar"`。コード健全性の確認のみに使い、閾値調整しない。
- Final holdout positive (`holdout`): H1 `"\tMIXED\n" -> "mixed", "  Q  " -> "q"`; H2 `" ÅBC " -> "åbc", " A B " -> "a b"`。
- Negative control (`holdout`): N1 reverse `"ab" -> "ba"`; N2 identity `"abc" -> "abc"`。
- 公開されたholdoutのため、コードや採用閾値を結果に合わせて改変した時点で、次の独立評価セットが必要。
- Train解法の入力例から解答ASTを手入力しない。既存 `synthesize` で発見したものから部分式を抽出する。
- 候補: 2個以上のcallを含み、異なる訓練task_idの成功ASTで2回以上出現する同一構造ハッシュ。名前は `skill_<sha256-prefix>`、来歴付き。ネスト技能は禁止。
- 両条件とも `max_ast_nodes=4`、`max_candidates=100`。primitive registryは同一。learned条件では1個のmacroを末尾に追加。比較時には展開後の原始ASTノード数も4以内に制限。測定用traceは両条件で別に計算。
- 発見したmacroのbodyを実行時に許可済みprimitiveのみで解釈し、各演算版を記録。候補式に任意コードの実行経路を認めない。

## Metrics / 指標
1. 訓練解法と候補: 構造hash、出現task、原始演算依存、型、macro ID。
2. 最終評価4課題における解決状態、一致する独立の出力、候補評価数、探索trace SHA-256、返却AST、展開した原始ASTノード数。
3. 正例2問の候補数差 `baseline - learned`、負例の候補増加率、誤った成功の件数。
4. Python、OS、commit、registryのsemantics_version、実験設定、runコマンドを記録。実行時間は補助指標で、候補数の方を主に解釈する。
5. Macroの抽象的な長さ短縮と、実際の原始操作コストの短縮は別物であることを明記。

## Acceptance / 採否ゲート
- **Function PASS:** 2訓練エピソードから同一macro候補を自動抽出し、bodyの安全な型検査・原始演算のセマンティクス一致・決定性・既存EXP-0001回帰試験を満たす。
- **Search benefit (限定的):** Holdout正例の双方で正答、候補数がbaselineより各1以上減り、負例でfalse positiveなし。これは同型タスク内の効率改善であり、新しい課題クラスの獲得ではない。
- **Promotion gate (厳格):** Search benefitに加え、負例の候補増加が**各2倍以下**、既存課題の回帰なし、独立レビュー完了。満たさなければmacroは `candidate` / `withheld` のまま、default registryには追加しない。
- 結果が不明なら `inconclusive`。コード未実行をPASSとして報告しない。採用前にPR/CIで機械的検査を行う。

## Reproduction / 再現手順
`python -m unittest discover -s tests -v`
`python scripts/check_docs.py`
`python -m packages.evaluation --output .run/EXP-0002-result.json`
JSONはrunに保存し、判定文章とは分離。対応するcode commit SHAを残す。

## Limitations / 反証可能性
- 原始演算が3種類で、同型な小課題群の比較は汎用的概念発明の証明ではない。
- 意味的重複や候補順によって測定値は変化し、macro一個の表面的な節約は計算量一般の改善とは限らない。
- 使用トークン数、実行した原始演算回数、技能学習コストを含む総計算量評価は後続実験で必要。
- 学習済みmacroをデフォルトで有効化しない。いつ、なぜ採用できるかを別に判断する。

Related: [Issue #5](https://github.com/ryonakayama234/DekaSugi/issues/5), [ARCH-001](../../docs/architecture/system.md), [ARCH-002](../../docs/architecture/contracts.md).
