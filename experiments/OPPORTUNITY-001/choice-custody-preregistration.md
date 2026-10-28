# OPPORTUNITY-001 — PR9 事前判断原本の品質試験・保全計画

id: OPPORTUNITY-001-CHOICE-CUSTODY-PREREG-V1
status: proposed_engineering_preregistration; no_experiment_run; no_scoring_authorization
updated: 2026-10-28
tags: preregistration, evidence-quality, negative-tests, no-scoring, provenance

## Research unit / falsifiable claims
**Primary object** = 正式main pretrial workflow run `40659741488` / artifact `12803053107` にある**公開**decision JSON member原本と、その独立保存コピー。研究対象は公開TRAIN64 × B1/B2/B3 = **192件の採点前のaction+reason**であり、学習能力ではない。

次の工学的主張を試す。仮説・失敗条件の正本は [spec H1–H5](../../docs/specs/OPPORTUNITY-001-CHOICE-LOCK-DESIGN.md)。各項目は`pass/fail/not_observed`を個別に記録し、1項目でも必要条件を満たさなければ受入れず、統計p値や任意の総合点を計算しない。

| check_id | 観測・判定対象 | 完成条件 |
|---|---|---|
| C01 | 元artifact出典 | 公式run/job/artifact/commit IDとActions APIの参照が一致 |
| C02 | public元member raw bytes | 単一の事前定義member・byte SHA256を固定、保存コピーbyte一致 |
| C03 | canonical logical digest | 既存方法で計算したsha256が`8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2`と一致 |
| C04 | 64×3完全性 | exact task IDs 64、重複0、B1/B2/B3各64、各action/reason valid、順序保持 |
| C05 | source/skill/policy linkage | 既存新TRAIN source lock（public manifestと3 policy/skill SHA）に一致しsource-first |
| C06 | temporal precedence | 公式pretrial証拠を後続scoring eventより前に固定、将来scorerは封印lockを参照 |
| C07 | public-only boundary | private raw third audit、family、seed、source_record_id、scoring outcomeは一切公開しない |
| C08 | retention and independent audit | public Gitへraw memberとlock保存、原本ZIPの期限切れを前提に再照合可能、latest-head CIと独立レビュー |
| C09 | scope and permissions | `paired_trials_executed=0`、`dev_or_final_evaluated=false`、全scoring permission false |

## 検証実装の順序（実行していない計画）

1. 原本をofficial run/job/artifactに限定して**取得**。不正ZIP名、複数JSON/duplicate member、予期しない圧縮、ZIP bomb、size overshoot、member差替えをfail closed。元ZIP hashとmember byte hashを**別々に**保存。
2. 元member byteを一切書き換えず別ファイルへコピーし、strict JSON schema parse → canonical hash。数値0/falseはbool/intを厳密区別。キーホワイトリストと配列順までチェック。
3. 現行9-source generator + 14-source old freezeの**byte-first gate**を検証し、その後にTRAIN/DREAM-only snapshot再構築。旧DEV/FINAL生成・`load_frozen_assets`・旧`verify_frozen`・scorerのimport禁止。source-firstで新TRAIN64公開TaskSpecを検証後、64 task ID/order/choice/reasonのparityを比較。
4. 保存先を公開Gitの`experiments/OPPORTUNITY-001/evidence/pilot-choices-public-v1.json`、lockを`experiments/OPPORTUNITY-001/pilot-choice-lock-v1.json`として別のreviewed commitで提案。生private監査原本をpublic Gitには保存しない。元Actionsの保持期限だけに依存しない。
5. 原本が得られなければ、再演算で生成した「同じ内容」を**元の証拠として代用しない**。停止し、失敗記録を残す。ソース同一性、計量器、レビューいずれも自動的に代替しない。
6. **このPRはdocs-only**。上記は後続の独立実装PRでしか走らせない。たとえC01–C09が全てpassでもactual evaluatorとprivate raw custody/one-shot activationは別ゲート（Issue #66）。

## Negative / adversarial calibration matrix （すべて人工fixtureのみ）

| ID | 注入する変異 | 期待結果 |
|---|---|---|
| N01 | 63/65行、重複task ID、行順入替 | missing/duplicate/order driftとしてhard stop |
| N02 | B1欠損、B4混入、ON/OFF以外のaction、空reason、reason改変 | hard stop |
| N03 | 異なるpolicy snapshot・skill digest・public TaskSpec manifest | hard stop |
| N04 | 元artifact IDが異なる／PR初期不許可runの同じpayload SHAを転用 | identityとoriginを分離してhard stop |
| N05 | ZIP内の複数member、nested path、重複member、size over-limit | 既定の単一public member以外をhard stop |
| N06 | 同一JSON意味だが改行/空白の違うbyte列 | logical digestが同じでも原本copy raw hash差を拒否 |
| N07 | 重複JSON key、NaN、Infinity、bool-as-int、余分なnested/top key | hard stop |
| N08 | public出力のprivate第三audit/family/seed/source_record_id/score混入 | hard stop、公開前 |
| N09 | 証拠出典がscoring後・lockが後付け・clockのみを根拠 | chronology `fail`/`not_observed`、seal禁止 |
| N10 | Artifact期限切れだが保存済み原本コピーあり | 原本copyの再検証のみ可能、元出典の過去取得記録がなければoriginはunknown |
| N11 | 旧DEV/FINAL生成器を呼ぶfake、byte gate以前のproject import | hard stop、元実験へ副作用なし |
| N12 | 診断replayのJSONが一致するが元Actions member未取得 | `not_observed`を`pass`に変えない |

## 計量形式と記録する不確実性

- **測定値**: raw member SHA256、canonical payload SHA256、集計件数(64/192)、構造エラー数、出典run/job/artifact/source SHA、保持コピーのbyte一致判定。
- **観測ではない値**: accuracy、regret、policy utility、学習利得、総CPU利益、新TRAIN64のscored rows。すべて`not_observed`として扱う。
- **再現性**: 決定的な整数/ハッシュはbit-for-bit一致。CPU/wallは元pretrial payloadのstable hashに含まれず、ロックの検査対象に後付けしない。
- **独立性の限界**: original artifactをsourceとし、解析器を別実装にすることと、同じchooserを再実行して同じ結果が出ることを厳格に区別する。meta-runの信頼根拠とGitHub側の削除/履歴改変リスクを明記。
- **保管の安全**: public Gitはprivate backupではない。非公開第三監査元bytesの保管はIssue #66の別要件で、SHAコミットだけでは代用不可。

## 依存・非変更・採用基準

- 入力正本: [PR #65](https://github.com/ryonakayama234/DekaSugi/pull/65) merge `c6b01c2`、source [pilot-generator-lock-v1](pilot-generator-lock-v1.json)、[PILOT-V1](pilot-v1.md)。
- 未統合の[PR #67](https://github.com/ryonakayama234/DekaSugi/pull/67)は**結果正規化器**であり、ここでの選択原本保全はその変更に依存させない。独立exact-headレビューが終わるまで混同/統合しない。
- 旧EXP-0003A DEV64/FINAL128、EXP-0002B FINAL112、元のsource/method freeze、既存policy snapshotsは読み取り/参照のみ。新採点・old holdout再生成・学習器改変・技能昇格なし。
- PR9の設計ゲート: 図、data contract、実験/試験計画、run台帳、INDEX、AGENTSの同期；`python scripts/check_docs.py`と標準CI、最新headへの独立レビューを**実際に確認して**採否決定。完了までは`proposed_design_only`。
- 後続の保存ゲート: C01–C09全部pass、N01–N12を拒否、origin metadata・保存コピー・provenanceが確認できて初めて`sealed_pretrial_only`。この状態でさえscoringはfalse。

## 将来のrun / report形式（設計のみ）

`run_id, source_commit, evidence_origin, artifact_raw_sha256, member_raw_sha256, copied_member_raw_sha256, canonical_payload_sha256, source_manifest_sha256, skill_sha256, policy_sha256_by_arm, exact_task_ids_count, exact_choices_count, check_results, negative_fixture_results, review_head, CI URLs, custody_target, retention_risk, known_unknowns, permission_flags, outcome_claims=none, actual_paired_trials=0`。

未実行のstatusを`planned`または`not_run`として残し、原本の実測値・CI合格を推測で埋めない。関連: [設計契約](../../docs/specs/OPPORTUNITY-001-CHOICE-LOCK-DESIGN.md) / [run ledger](runs/README.md) / [Issue #68](https://github.com/ryonakayama234/DekaSugi/issues/68)。
