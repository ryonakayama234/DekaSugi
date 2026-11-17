# E1 — 人工例による工学確認（2026-11-17）

id: E1-ENGINEERING-20261117
status: local_core_pass_browser_ci_pending_device_checks_pending
updated: 2026-11-17
tags: editor, engineering, invented, evidence

許可：[Issue #227](https://github.com/ryonakayama234/DekaSugi/issues/227#issuecomment-6935058538)。基準main `ae44f126e36410b98dc5ee450a05348c9f11105b`。成果物：[HTML](../../../packages/draft_editor/editor.html)、[仕様](../../../docs/specs/E1-DRAFT-EDITOR.md)、[端末確認](../../../docs/process/e1-editor-checklist.md)。本票は研究結果・学習能力の認定ではない。

## 確認の範囲

- core検査は配布HTML内のcoreをそのままNode VMへ読み込む。架空の日本語訂正、600組のUnicode文字列対、改行・絵文字・ZWJ、undo/redo履歴、選択、目的変更、gap、JSON/JSONL、型・版・範囲・再生・品質の偽装拒否を確認。
- browser検査は同じHTMLを実ブラウザで開く17シナリオ。DB再起動、区切りと子revision、native undo、合成composition順序変種、中止の不確定性、変換中の保存拒否、未通知変化、JSON別コピー、読込み全体拒否、保存不能・失敗注入・再試行、二重タブCAS、履歴ごと削除、CSP/通信、tablet寸法を対象にする。
- 実入力はゼロ。browserのcompositionは合成イベントで実IMEではない。Android端末ではなくChromiumの寸法模擬である。

## 実測と未確認

| 確認 | 状態 | 証拠・限界 |
|---|---|---|
| Node core人工検査 | PASS 15/15 | `node --test tests/draft_editor/core.test.cjs`。最終ソースへの再実施をPRに記載 |
| ローカルheadless Chromium | 実行不能 | この実行環境でUNIX socketが拒否され、ブラウザ起動前に停止。試行を合格数へ含めない |
| cloud browserのfileプレビュー | 実行不能 | 許可プロトコルがhttp/httpsでfile表示が拒否。迂回していない |
| E1専用GitHub browser検査 | pending | このPRの専用workflowから人工例のみ実施し、結果はPR／Actionsに追記する |
| docs-check／既存source境界 | pending | 最終ソースで実施し記録する |
| Muse独立確認 | 未実施 | 正確なheadでの別環境確認待ち |
| Windows＋Edgeの実IME | 未実施 | Owner主端末の確認カード待ち |
| Galaxy Tab A9+＋Chrome | 未実施 | 起動・IME・保存往復を確認するまで対応未確認 |
| 別日の実用下書き3件程度 | 未実施 | E1完了条件。制作提出時の合格へ数えない |

専用workflowはPRのE1変更にだけ反応し、read-only権限・10分上限。Node coreと独立のPlaywright 1.62.1／Chromiumだけを使う。パッケージ取得は検証環境の準備で、配布HTMLの実行時依存ではない。旧workflow・scorer・研究生成器・凍結データを変更／実行しない。既存CIを復活・無効化しない。

## 判定

制作物の工学提出であり、E1完了・学習能力の獲得・マージ許可ではない。ブラウザ検査の失敗は同じDraftで修正し、独立確認と実機確認へ渡す。未確認をPASSへ読み替えない。
