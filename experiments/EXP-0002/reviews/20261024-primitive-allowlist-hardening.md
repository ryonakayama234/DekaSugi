# EXP-0002-SEC-003 — 原始演算の偽装を防ぐ境界検査

id: EXP-0002-SEC-003
status: implemented; independent re-review pending; CI outcome tracked on PR
updated: 2026-10-24
tags: security, exp0002, audit, provenance, reproducibility, macro

## 問題と再現条件

[PR #6 第3回Codex P1レビュー](https://github.com/ryonakayama234/DekaSugi/pull/6#discussion_r4367347313)で、登録済みmacroの`semantics_version`だけを通常の原始演算風に書き換えた`Registry`を評価器に渡すと、`learned=None`で登録外macroを原始演算として扱い、展開後ASTの物理ノード予算を過少申告できると報告された。過去2件のP1修正は残す。

- 改変対象: `registry_with_skill(discover_skills(TRAIN)[0])`のmacroを`dataclasses.replace`で版だけ偽装。
- 影響: `bounded_synthesize`は版接頭辞を信頼してmacroを識別していた。実行するPython callbackの真正性も実行時に検査していなかった。
- 誤用例: `max_ast_nodes=2`で、物理的には3ノードのmacro解を合格扱いする可能性。
- 改善は**実行基盤の安全性修正のみ**。公開済みholdoutでの新たな科学的採用判定は行わない。

## 対応方針・固定契約

`packages.evaluation._trusted_search_registry`を導入し、検索を開始する前に次を満たさなければ拒否する。

1. 通常演算の個数・順序・ID・入出力型・`semantics_version`・**Python実装オブジェクトの同一性**を`DEFAULT_REGISTRY`の承認済み`trim/lower/upper`と照合。偽装、未知演算、順序変更はfail closed。
2. macroは登録済み`derived-<canonical body hash>`、`SkillCandidate`のID/body/型/依存/来歴を検証した上で、承認済み原始演算を使う**検証済みASTから実行レジストリを再生成**。呼び出し元のmacro callbackを実行しない。
3. 型・展開後ノード数・候補数・独立Verifierは以前の境界を維持。新たな技能の正式昇格を行わない。
4. `Registry`自体は公開コンテナであり、値・版文字列だけで実装を認証したことにはしない。学習器が使用できる原始演算は既存3種類に固定。

## 回帰テスト

`tests/test_exp0002_learning.py::LearningTests.test_disguised_macro_and_unapproved_primitives_fail_closed`

- [ ] 偽装された非derived版のmacroを、`learned=None`でも拒否。
- [ ] 原始演算名・版を真似る別Python callableを拒否。
- [ ] 原始演算レジストリの入替え・未知演算追加を拒否。
- [ ] 同じmacroのメタデータを維持しながらcallbackを悪意ある関数へすり替えても、そのcallbackを**実行せず**canonical ASTから再構築した経路で評価する。
- [ ] 既存のEXP-0001/0002回帰と文書検査がPASS。

チェック欄は新headでのCIを観測するまで未確定。実行された証跡は[PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6)のcommit/Actionsを参照し、履歴的な実測runと混同しない。過去の[RUN-001 / RUN-002](../runs/README.md)は書き換えない。

## 限界と判定

この境界はEXP-0002専用の**承認済み固定primitive**を前提とする。新しい原始演算を導入する場合は、allowlist拡張・独立レビュー・別実験を必要とする。現行EXP-0002Bの計測器は、このcanonical registryの内部を計数する必要がある。

**判定: 修正は提出済み、第三者レビューとCI再検証が完了するまでPR #6は未承認・未統合。**

[仕様](../../../docs/specs/EXP-0002.md) / [全体図](../../../docs/architecture/system.md) / [契約](../../../docs/architecture/contracts.md) / [目録](../../../docs/INDEX.md)。
