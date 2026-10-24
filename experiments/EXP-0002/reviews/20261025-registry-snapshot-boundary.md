# SEC-004 — Mutable Registry lookupを実行権限としない

id: SEC-004
status: implemented-in-review-branch; ci-and-codex-review-pending
updated: 2026-10-25
tags: security, registry, exp0002, audit, regression, architecture

## 問題・背景

[PR #6の第4回P1](https://github.com/ryonakayama234/DekaSugi/pull/6)では、呼出元が公開`DEFAULT_REGISTRY.by_name`を置き換えても`DEFAULT_REGISTRY.primitives`を変更しなければ、従来のprimitive同一性検査を通過できた。安全と思って`trusted = DEFAULT_REGISTRY`を使用していたため、PoisonされたPython callbackがVerifierから実行され、必要な操作数や解法に影響する。P1の既存3件とは異なる攻撃面である。

## 修正範囲

1. `DEFAULT_PRIMITIVES`タプルを原始演算の認証基準とする（公開可変`DEFAULT_REGISTRY`ではない）。
2. 検証通過後に`Registry(DEFAULT_PRIMITIVES)`を新規作成し、`primitives`・`by_name`・`signatures`を同じ固定定義から組み立てる。
3. `bounded_synthesize`のmacro照合も、呼出元の可変`by_name`ではなく`primitives`宣言値と`SkillCandidate.body_hash`に基づく。
4. 既存macro callbackは実行せず、検証済み型付きbody ASTから再構築する。
5. 原始演算の候補集合、探索順、候補予算、展開ノード予算、独立Verifier、過去のrun、保留評価条件は変更しない。

## 事前に固定する攻撃・回帰検査

`tests/test_exp0002_learning.py::LearningTests.test_mutable_registry_lookup_never_becomes_executable_authority`:

- `DEFAULT_REGISTRY.by_name["trim"]`に未承認callbackを注入し、`DEFAULT_REGISTRY.primitives`は正常でも旧実装がcallbackを実行しうる経路を再現する。
- 公開`DEFAULT_REGISTRY`の検索表・署名表・原始演算属性を差し替えても、正常な別`Registry`入力を使ったOFF/ON探索が元の結果と一致し、未承認callbackを実行しないことを確認する。
- 呼出元の`Registry`自身の`by_name`・`signatures`を改変しても、宣言済みの原始演算と技能が正しい場合の結果が変わらないことを確認する。
- 回帰不変条件：status、program AST、tested_candidates、trace_sha256。原始演算の検査・ネスト技能拒否・展開費用の既存テストも再実行する。

## 実行と第三者確認

- GitHub Actions: `python -m unittest discover -s tests -v`, `python scripts/check_docs.py`, EXP-0001 suiteとEXP-0002既存比較を実行し、対象head SHA・run URL・実測結果を追記する。
- GitHub PRへ`@codex review`を依頼する。Codexのレビューが返っても重大な未解決指摘がある場合、mergeは保留する。
- Code ReviewとSecurity Reviewが行える場合は独立に結果を記録。レビューが未着の場合は完了とはみなさない。
- 研究上の正式採用・新しいFINAL・ポリシー学習は対象外。これはPython内部の不正なオブジェクト利用を限定範囲で防ぐもので、任意の不正Pythonコードを同一プロセスに隔離するセキュリティsandboxではない。

## 進捗

この文書は変更コミットと同期する設計・監査記録。CIと外部レビューの結果は実際に確認した後に追記する。

関連：[Issue #14](https://github.com/ryonakayama234/DekaSugi/issues/14) / [PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6) / [ARCH-001](../../../docs/architecture/system.md) / [ARCH-002](../../../docs/architecture/contracts.md) / [資料目録](../../../docs/INDEX.md)。
