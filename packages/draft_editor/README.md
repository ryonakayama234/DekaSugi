# E1 — ローカル下書き記録器

id: E1-EDITOR
status: implemented_pending_independent_and_device_checks
updated: 2026-11-17
tags: editor, local, japanese, episodes

配布物は [editor.html](editor.html) **一枚**です。ダウンロードして、同じ場所のファイルをWindows＋Edgeで開きます。サーバ・アカウント・有料API・実行時依存は不要です。

- [使い始めと5〜10分の端末確認](../../docs/process/e1-editor-checklist.md)
- [形式・保存・取得欠損の仕様](../../docs/specs/E1-DRAFT-EDITOR.md)
- [工学検証の記録と未確認項目](../../experiments/E1/runs/20261117-editor-engineering.md)
- 許可：[Issue #227 Owner最終確認](https://github.com/ryonakayama234/DekaSugi/issues/227#issuecomment-6935058538)。学習・実入力の共有・マージは含みません。

本文を入力・訂正して「保存して区切る」。任意の目的欄は空でも構いません。JSONを書き出せば、削除前の文字を含む編集履歴を別ファイルで持ち出せます。履歴画面は読み取り専用です。

自動退避はブラウザ領域です。ファイルの移動・更新・ブラウザ変更・ブラウザデータ消去の前にJSONを書き出してください。保存要求だけでは実ファイルの完成を判定できません。一度読み込み直して確認してください。変換中の文字と未退避の末尾は障害時に失われる場合があります。

Windows＋Edgeは主対象ですがOwner実機は確認待ち。Galaxy Tab A9+＋Chromeは副対象で、起動・IME・保存往復が実機で確認されるまでは対応未確認です。file起動が成立しない場合は起動方式だけを再判断し、自動同期や新たなサービスを追加しません。

## 人工例だけの検証

```sh
node --test tests/draft_editor/core.test.cjs
node tests/draft_editor/browser.test.cjs
python scripts/check_docs.py
```

ブラウザ検証にはNodeから解決できるPlaywright 1.62.1とChromiumが必要です。Linuxでは既定で `/usr/bin/chromium`、他の場所は `E1_CHROMIUM` で指定します。配布HTMLそのものにはPlaywrightもNodeも不要です。CIは独立したE1専用workflowで、架空文だけを使います。旧研究の生成器・scorer・holdoutを呼びません。
