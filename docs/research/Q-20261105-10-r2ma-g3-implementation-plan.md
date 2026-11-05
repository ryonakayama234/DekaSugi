# R2-M-A G3 実装計画の依頼 — 監督者質問票 Q-20261105-10

id: R2-M-A-G3-Q-20261105-10
status: question_for_lead / docs_only / plan_only / no_implementation / no_execution
updated: 2026-11-05
tags: r2-m, preregistration-a, g3-implementation-plan, supervisor-questionnaire

> 本書は外部監督者Claude（ごま）から Research Lead への依頼である。対象は凍結済みの事前登録 [R2-M-A-20261105](R2-M-A-20261105-exhaustive16-engineering-prereg-draft.md)（main commit `cf844094fb5907a37bb496760e206f9061deb021`、文書 SHA-256 `865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68`、凍結 receipt は PR #181）の **G3（実装計画）** である。求めるのは実装計画の提案文書（docs-only の新規 Draft PR）であり、**実装そのものではない**。計画への監督者精査と Owner の別途 GO が出るまで、コードの追加・変更、測定の実行、順序の確定は行わない。凍結した事前登録の内容は変更しない（変更が必要と考える場合は、その旨を計画の中で「新版が必要な逸脱候補」として明示すること）。

## 依頼の範囲

凍結した測定（全16法則×USE 4点×7 arm = 448 fresh child）を実行可能にするための、次を対象とする実装計画:

- 科学用4点 runner（現行 Stage 3 の1点 fixture runner の流用可否を含む）
- 費用計測（CPU/wall/RSS、decoder/validator 呼出、候補数、trace 量など凍結文書 §6 の費用ベクトル）
- precommit・digest 固定・append-only 原本・receipt などの保管機構
- 上記のテスト戦略と、G4 実経路監査に提出する資料（dossier）の構成

## 質問（QG1〜QG6）

**QG1（runnerの構造と分離）**: 科学用 runner をどのパッケージ/モジュール構成で実装するか。既存 `packages/r2_m_eng` の資産（records/gateway/decoder/validator/snapshot/dispatch/meter）をどこまで再利用し、どこからを新規とするか。工学 fixture と科学用実行の混線を防ぐ境界（モジュール分離・import 境界テストなど）をどう置くか。凍結文書 §5 の手順（公開3点の配布→Q001 前の precommit→係数構築と独立 validator→Snapshot 生成と expected SHA 固定→arm×点ごとの fresh child→採点前の digest commit→評価側照合）を、プログラムのどの単位にどう対応づけるか。

**QG2（費用計測の実装方式）**: 凍結した上限（wall 5秒/child、CPU 5秒/child、RSS 512 MB/child）に対し、(a) 各費用の測定方法、(b) 上限の強制方法（事前の資源制限か、事後の超過判定か）とその根拠、を提案すること。特に RSS は上限値のみ凍結され測定方式が未定であるため、方式の候補と比較（例: 子プロセス自身による自己申告、親側からの取得）を示すこと。decoder/validator 呼出回数の learn/restore/use 別計上、FIXED-MACRO のカタログ構築費の `per_fresh_process` / `one_off_preparation` への計上列（精査 R-20261105-09 の注記2。G4 で確定する前提で、計画時点の提案を示すこと）も扱うこと。

**QG3（保管・receipt 機構）**: precommit 記録、出力 digest の採点前 commit、append-only 原本、計測環境（CPU/OS/Python 版）の記録、失敗・INVALID の保存（自動リトライなし・単回計測の凍結条件と整合する失敗処理）を、どのファイル形式・どの書き込み手順で実現するか。法則の実行順序は G5 で別途固定するため、計画では順序 manifest を差し込む位置だけを設計し、順序自体は決めないこと。

**QG4（テスト戦略）**: 実装の正しさをどうテストするか。単体テストに加え、凍結手順の負例（Q 前 commit の欠落、expected SHA 不一致、子への真値混入、欠測の隠蔽など §8 の INVALID 条件に対応するもの）をどう再現・検出するか。無害な fixture による通し確認は、G6 の本測定と混同されない形（対象・記録の分離）をどう担保するか。

**QG5（G4 監査 dossier）**: 実経路監査のために、実装後にどの資料を提出するか。想定する含み: 対象 exact commit の import graph、全実接続 route の一覧と fallback 到達可能性、公開/評価側のフィールド分離の根拠、7 arm 同一入力・同一コスト規約の確認方法、負例テストの結果。監査対象 commit の固定方法も示すこと。

**QG6（作業分割と PR 構成）**: 実装を何段階に分け、各段階の成果物・受入条件・PR 構成をどうするか（R2-M-ENG の3段階方式の踏襲可否を含む）。規模の見積もりと、計画に含めないもの（本測定の実行、順序の確定、結果の採点・解釈は G5/G6 であり、本計画の範囲外）の明示。

## 回答の形式

- 新規 Draft PR（main 基点、docs-only）で、計画文書1件＋ `docs/INDEX.md` 登録を提出すること。
- QG1〜QG6 に番号どおり回答し、方式の選択肢が残る箇所は「提案」と「代替案とその不採用理由」を分けて書くこと。
- 凍結値を再掲する場合は凍結 receipt（PR #181）の値と一致させること。凍結内容と矛盾する提案はしない（必要な場合は逸脱候補として明示）。
- 逆質問があれば計画文書に併記してよい。

## 権限の再確認

本依頼は G3 の計画作成のみを許可する。実装 GO は計画への精査と Owner 決定の後であり、本質問票の提出・回答のいずれも実装・実行の許可ではない。G4 監査・G5 順序・G6 実行はいずれも未許可のままである。認定状態（M_use NOT_CERTIFIED / M_gap UNKNOWN / N_rep・U・T NOT_EVALUATED）にも変更はない。
