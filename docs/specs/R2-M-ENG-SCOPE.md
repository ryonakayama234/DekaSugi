# R2-M-ENG — 方法v2に基づく実装範囲案（工学診断のみ・未許可）

id: R2-M-ENG-SCOPE-20261104
status: proposed_scope / docs_only / pending_claude_review / pending_owner_implementation_go / not_implemented / no_experiment / no_scoring
updated: 2026-11-04
tags: r2-m-eng, scope-proposal, method-v2, engineering-only, public-private-boundary, controls, immutable-snapshot

> **決定の正本:** [PR #174 Owner決定コメント](https://github.com/ryonakayama234/DekaSugi/pull/174#issuecomment-6632937532)。Ownerは [方法v2（R2-M-20261104-SINGLE-METHOD-V2-PROPOSAL、PR #174の査読済みcommit）](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md) を**R2-M系統の後継方法として採用**した。本書はその**R2-M-ENG実装範囲の提案1件**であり、実装GO・科学実験・採点の許可ではない。Claudeの範囲精査とOwnerの別途決定まではコードを書かず、Draftのまま保持する。

## 1. 権限・不変の境界

| 対象 | 本範囲案の扱い |
|---|---|
| R2-M後継方法 | Owner採用済みv2を唯一の**今後のR2-M設計・審査の方法正本**として参照。本文の修正・別版作成はしない |
| 凍結方法v1とR1 | R0/R1の歴史的正本として保全。[`R1-ENG-2BIT`](R1-ENG-2BIT.md)、`packages/r1_eng`、既存結果を変更しない |
| 今回のPR | **このscope文書1件と`docs/INDEX.md`登録のみ**。コード、テスト、CI設定、既存PR/Issue、mainは変更しない |
| 将来のR2-M-ENG（Ownerが別途GOした場合に限る） | 隔離した`packages/r2_m_eng`＋人工fixtureの**工学的動作確認のみ**。結果は機構診断であり、科学的能力の証拠ではない |
| 科学研究 | 新sourceの独立選定・封印、preregistrationを要する実行、private USE採点、M_use/M_gapの認定、N_rep/U/T評価、独立family転移は**対象外・未許可** |
| 既知の例と過去資産 | [PR #173](https://github.com/ryonakayama234/DekaSugi/pull/173)で公開済みのparity3真理値表を**独立性の証拠として使用しない**。旧sealed/heldout、旧DEV/FINAL、過去のsource・scoreを実行・修正しない |

権限の時系列は **方法v2採用 → 本scopeのClaude独立精査 → Ownerが実装GOと範囲を別途決定 → 許可された人工fixtureのENG実装/CI → さらに別の科学前登録・Owner許可がなければ実験・採点を行わない**。scopeが受け入れられても実装・科学実験のGOは自動発生しない。

現時点の研究状態は **`M_use=NOT_CERTIFIED`、`M_gap=UNKNOWN`、`N_rep/U/T=NOT_EVALUATED`**。R1-ENGの2bit Rでは全4点を公開し、合法なepisodic lookupが全点再現してON/OFFの予測・合法行動差は0だった。この陰性結果・履歴は改変しない。

## 2. 将来の実装対象（方法v2 §1〜§5の逐条対応）

**原則:** すべて人工的・既知法則のfixtureでのみ検査する。source-privateな情報とlearner-publicの情報を構造的に分ける。モデルの事前バイアス（F_affと復号/コンパイル規則）は全armに開示するが、実際のOFF初期dispatchに存在する合法経路を取り除いて差を作らない。

| 方法v2の契約 | 隔離ENGで検証可能にする最小機能 | 境界・拒否条件 |
|---|---|---|
| §1 Source / public gateway | 3bit `X={0,1}³`、`F_aff`16法則の**人工source**、初期公開点000/100/010、事前commitした合法paid Q001（予算1）、公開計4/8、private入力011/101/110/111のラベルをEvaluator側だけに隔離。合法行動集合＋digest、期限、費用、受領順の記録 | law係数・seed・個別target・private labels・将来USE outcomeがlearner、decoder、validator、Snapshot、公開trace、対照armへ流れたら`INVALID` |
| §2.1 係数復号 | `d=r000, a=r100 XOR r000, b=r010 XOR r000, c=r001 XOR r000`。4応答の到着後のみ復号1回。入力順x→y→z、係数1を左結合、空列は0、d=1なら末尾NOT。XORは`OR(AND(A,NOT(B)),AND(NOT(A),B))`に決定的展開 | 型付きBool**木AST**（定数0/1、x/y/z、NOT/AND/ORのみ）、静的最大32ノード。列挙・「最初に一致したAST」方式への変更不可。族16、候補上限16と、実際の生成0/1個・decoder起動1回は別記録 |
| §2.1 公開validator | decoderと別経路の純粋なpublic-only interpreterによる型/ノード数/構文/公開4点との整合検査。失敗なら`VALIDATION_FAILED`、恣意的再候補なし | 秘密の法則やprivate正答による選抜禁止。独立validatorをdecoder内部の同一実装で代用しない |
| §2.2〜§2.3 H0 / 状態 | 8個の`H0_object={0,1,x,!x,y,!y,z,!z}`とN/S/R/E/VALIDATION_FAILEDの診断分岐を保持 | `H0_object`の不一致を`H0_effective(B)`の不可能性証明・M_gap陽性と取り違えない |
| §3 Fixed dispatch | 同一immutable Snapshot・同一公開履歴/予算/固定policyでF00（BODY OFF）とF10（BODY ON）をfresh子プロセスで比較。ONは検証済みbodyを優先。body不在時はexact episodic → 整合するH0（指定順）→ 監査済みの**その他すべての既存合法経路**→ ABSTAIN | OFFではlearned bodyの呼出だけを無効化。既存decoder接続・Kernel・macro・近傍・policyを意図的に断線/削除/縮退しない。routeだけの差は効果としない。実在する経路が§3単純図と食い違えば§4閉包監査へ戻す |
| §3 Controls/v2 | `R2-M-CONTROLS-v2.0`を版固定してSTATIC-H+、FIXED-MACRO、EPISODIC-EXACT、NEAREST-1NN、STUMP-1の人工fixture比較経路を用意 | STATIC-H+には同じF_aff decoder・AST・上限を認めUSE時再構築費を計上。FIXED-MACROは事前に16法則**すべて**を登録、target別注入禁止。episodicは公開全4点を保持、容量上限8を人工削減しない |
| §3 Tie/arm未起動 | 1NNはHamming全最短同点を多数決、同数ならABSTAIN。STUMP-1は定数2＋各x/y/zの4出力対＝14枠、公開0-1誤り最小、同点は方法指定の列挙順。全armのcapacity/route/cost/tieをmanifestに記録 | F01/F11（学習policyの効果）は**NOT_EVALUATED**のschema枠だけ、学習器を新規起動しない。ORACLE-REFはEvaluator-only理論参照枠で、public routeにはしない。未固定のpolicy/結果後のarm変更は禁止 |
| §4 Closure | `R2-M-CLOSURE-v2.0`様式と資産・経路・容量・履歴・digest・不明理由を記録。**初期`status=UNKNOWN, closure_complete=false, M_gap=UNKNOWN`**を保持 | 人工fixtureの通過やH0の8述語列挙だけでCOMPLETEを偽装しない。実効dispatchの全経路・全合法history・資源・最善OFFを対象結果前に独立証明できない限りUNKNOWNを維持。事後上書き救済は禁止 |
| §5 Sleep-lite / Snapshot | 意味保存だけのAND/OR可換正規化、receipt、公開journal・係数由来・compiler/validator/policy/arm/closure digestを含む`Snapshot/v2`。排他的作成・上書き拒否、schema・型・digest・public整合の復元検証 | `Path.resolve()`相当の**絶対Snapshotパス**を作成時に確定し、cwdの異なる子プロセスにもそのパスのみ渡す。ローカルSHAは独立原本保管/信頼時刻証明ではない |
| §5 記録・メータ | `PublicStep/v2`、`HypothesisCertificate/v2`、`ConceptBody/v2`、`Snapshot/v2`、`UseTrace/v2`、`ScoreReceipt/v2`の版・権限別schema。body/fallbackのavailable/selected/executed/finishedを別項目化 | `ScoreReceipt`のENG用途は**schema/人工値の検証のみ**、本当のprivate outcome採点はしない。予測・合法行動とtraceは公開可否を区別し、後日の採点に使う前commitの工学検査に留める |
| §5 R1-P2 / 費用 | `ast_nodes_static`（木の静的ノード数）、`node_visits_runtime`（短絡を反映した実訪問数）、`primitive_ops_runtime`（実行したNOT/AND/ORのみ）を分離。Q/候補/decoder/validator/復元/CPU秒/単調wall秒/RSS bytes/保存bytesを異なる単位で台帳化 | 静的数を実訪問数として代用しない。候補上限16を生成16個と数えない。不可換な異種費用の事後加重和、後出しの予算・閾値変更は禁止 |

### 2.1 ENGにおける合法な「人工fixture」の上限

- 人工的に選んだ**既知のF_aff法則**で、公開4点からの復号・保存・fresh ON/OFF・対照経路・拒否動作を検査してよい。必要なら全16係数組を単体機能テストするが、16法則の既知性・係数の人間提供は明記する。
- **既公開のparity3例そのものを独立証拠として使わない**。人工テストのパス、工学的ON/OFF差、全16法則の動作確認は、M_use・M_gapの科学的認定や未知概念の発見、独立family転移ではない。
- Source-privateの人工正答はtest oracleでのみ扱い、learner側への入力値をpublic4点から外挿・先取りしない。真の未見USE点の採点・source-first固定・独立custodyは別ゲート。

## 3. 将来実装時のテスト計画（すべて人工/negative）

| 区分 | 合格させる検査・期待結果 | 不合格時 |
|---|---|---|
| 識別・復号 | 16個の人工affine係数で公開4回答と復号係数が1:1、rank=4。Q001の欠落/期限超過はUNIDENTIFIABLE、budget不足はSTOP。係数順・左結合・末尾NOT・32ノード・公開一致を検査 | 非一意・無承認Q・型不整合は明示停止。偶然一致ASTへの差替え禁止 |
| 公開境界 | public gatewayにlaw/seed/private labelsを混ぜる、改ざんしたlegal digest、回答の先取り、precommit欠落、privateモジュールimportを試みる負例で拒否 | `INVALID`隔離・再試行禁止（当該実行を成功分母へ含めない） |
| OFFの合法性 | ON/OFFのSnapshot bytes・公開履歴・Q予算・非body fallbackと容量が等しい。episodicの全公開点、8 H0、既存の合法Kernel/decoder経路をOFFが保持し、隠れたrouteは監査対象 | fallbackを削る人為ABSTAIN、OFFのdecoder切断、容量削減を`INVALID` |
| 対照/tie | STATIC-H+のdecoderと使用時計数、FIXED-MACRO事前16全件、EPISODIC容量8、1NN最短距離全票と同数ABSTAIN、STUMP14枠と列挙順tieを人工反例で確認 | comparator manifestの勝手な変更・後出し弱体化を拒否 |
| 意味保存/検証 | 別interpreterのpublic4点再生、Sleep-lite前後で全8入力の**人工意味同値**、validator独立性、typed AST上限、receipt不一致を検出 | `VALIDATION_FAILED`または`INVALID`、秘密の正答で修理しない |
| 3種メータ | AND/ORの短絡で実際に評価した木ノードのみを訪問数に計上、NOT/AND/ORの実行回数のみprimitive費に計上。AST静的数・実訪問・primitive数が異なる負例を検算 | 静的数のコピーや未実行branchの加算を拒否 |
| Snapshot/プロセス | exclusive-createで上書き拒否、内容・schema・digest・public receipt改ざんを検知。親と異なるcwdのfresh ON/OFF子プロセスが**同じ絶対パス・同じbytes**を復元、復元前再照合 | 相対パス依存、cwd変化で別ファイル復元、汚染のある再保存は`INVALID` |
| 記録・閉包 | 6 schemaのrequired fieldsと公開/私的分類、活動イベントの別計上、候補0/1と予算16の区別、費用単位・precommit順序。closure=UNKNOWNから勝手にCOMPLETEへ昇格できないこと | 漏洩・欠損・後追い書換えを拒否、`M_gap=UNKNOWN`保持 |
| 工学受入 | 許可された人工fixtureだけのunittest・safe CIで繰返しパス、source-privateの公開混入0件、関連差分のみ、PR headごとの独立確認 | 実データ・sealed source・採点/学習を起動しない |

## 4. 提案する成果物・受入ゲート（将来の別GO後）

**今回作る成果物**は本仕様書1件とINDEXの登録のみ。以下は実装許可を得た場合の**予定**であり、存在・実行・合格を主張しない。

1. **仕様と実装:** 方法v2への契約トレーサビリティ表、本scopeで固定した境界の実装メモ、隔離モジュール、変更なしの`packages/r1_eng`を示す差分。
2. **工学テスト:** 人工fixture/negative testsの再現可能な呼出し、branch最新headのtestログ、公開境界・対照・短絡メータ・Snapshot別cwd・closure UNKNOWNのレポート。旧評価資産・既知parity例の科学証拠利用は0件。
3. **CI:** 既存のsafe successor CIのallowlistとrun範囲を独立レビューしたうえで**許可後**に追加する、または隔離された安全な新規チェック。旧main-push研究ワークフローとsealed資産は変更・実行しない。今はCI設定を触らない。
4. **Claude独立検証（P0）:** Owner決定・方法v2との逐条整合、frozen v1/R1の非改変、source/private境界、合法OFF全fallback、全対照公平性、closure UNKNOWN、Snapshot不可変性と絶対パス、メータ3種の実測、一切の科学的claim不在を差分と人工負例で確認。P1はLOC・費用・候補数と未知の実効経路の網羅性を査読。
5. **受入判定:** CI/単体試験とClaude精査が合格しても**ENG機構が仕様どおり動く**という工学判定まで。科学的M_use認定やM_gap/独立転移・実用的優越の判定は別の事前登録・原本保管・Owner許可が必要。

## 5. 予定ファイルと概算規模（実装を約束・承認する表ではない）

| 将来の予定パス（新規、または明示された将来変更） | 役割 | 見積（行） |
|---|---|---:|
| `packages/r2_m_eng/__init__.py`, `records.py` | export・6 record schema/型/権限分類 | 240 |
| `packages/r2_m_eng/source_gateway.py` | evaluator-only人工source／public gateway・paid Q journal（厳密なimport境界を別レビュー） | 200 |
| `packages/r2_m_eng/decoder.py` | 公開係数復号・決定的木ASTコンパイル | 170 |
| `packages/r2_m_eng/validator.py`, `sleep_lite.py` | 独立public interpreter・意味保存のみの正規化 | 250 |
| `packages/r2_m_eng/snapshot.py` | immutable Snapshot・絶対パス・復元検証 | 210 |
| `packages/r2_m_eng/dispatch.py` | fresh F00/F10・全合法fallback・活動trace | 170 |
| `packages/r2_m_eng/controls.py` | STATIC-H+、16 fixed macros、episodic、1NN、STUMPとtie | 240 |
| `packages/r2_m_eng/closure.py`, `meter.py` | UNKNOWN manifest・静的/実行時メータと費用台帳 | 240 |
| `packages/r2_m_eng/runner.py`, `__main__.py` | synthetic-only工程調停・fresh子プロセス | 250 |
| `tests/test_r2_m_eng_gateway_decoder.py` | source漏洩/合法Q/係数/型の人工正負テスト | 300 |
| `tests/test_r2_m_eng_controls.py` | OFF全経路、5対照arm、tie/容量 | 260 |
| `tests/test_r2_m_eng_snapshot_meter.py` | cwd差、排他・改ざん・短絡メータ | 260 |
| `tests/test_r2_m_eng_security_schema.py` | 公開/私的schema、closure UNKNOWN、INVALID | 220 |
| `tests/test_r2_m_eng_fixture.py` | 人工fixture一貫性・科学起動禁止 | 180 |
| `docs/specs/R2-M-ENG-IMPLEMENTATION.md` | 実装後の設計・テスト・CI受入記録（将来のみ） | 160 |
| CIのsafe successor側の明示レビュー済み変更（**許可後のみ**） | 人工fixture限定のテスト導線 | 約20〜50 |

概算は**新規Python約3,190行（本体約1,970・test約1,220）、将来ドキュメント約160行、CI差分約20〜50行**。設計段階の概算であり、監査により調整する。表の名称や行数は実装GOではない。今回のPRは**Markdown 2ファイルだけ**である。

## 6. 未決定事項（Claude/Ownerに判断を求め、先に決めない）

1. **有効な初期dispatchの閉包:** 方法§3の簡約順と、実際の合法なKernel・macro・runtime decoder接続の全列挙が一致するか。既存経路があればOFFに残す。H0_effective(B)のCOMPLETEは今回認定せず、当初UNKNOWN。
2. **source/gatewayの実行境界:** evaluator-only sourceをモジュール/プロセスどこで分割し、privateフィールドがpublic-only schemaに混入しないことをどう独立監査するか。敵対的同一プロセス防御まで保証するかは別承認。
3. **F01/F11とORACLE-REF:** 方法v2にはarm定義があるが、学習policyの設計・容量が未固定。ENGではF01/F11をNOT_EVALUATEDとして扱う案。ORACLEは評価者専用の参照schemaのみでよいか。
4. **科学source・preregistration・原本custody:** 将来のlaw抽選/seed、未知課題、private正答の独立保管、予測前commitの外部真正性、具体的評価予算/閾値/STOP再開条件。**ENGで決定・稼働しない**。
5. **CI安全導線と実装PR分割:** safe workflowに追加するか完全独立のsynthetic-only workflowとするか、既存保護ワークフローの動作保証、コード規模が大きい場合の段階的独立レビューとGO条件。
6. **N_rep/U/T、W-B/W-C、表現修復:** 本ENGでは評価・起動しない。別Owner判断なしに代替の陽性研究路線へ移行しない。

## 7. 提出後の状態・次ゲート

- **今回:** docs-only範囲案を新規Draft PRで提出し、`docs/INDEX.md`へ登録。**実装0、実験0、採点0**、旧PR/Issue/main/既存コード変更0。
- **次:** Claudeが本範囲のP0/P1と上記未決定を独立精査し、Ownerが**R2-M-ENG実装GOと許可範囲を別途明示**する。条件不成立ならREDESIGN/STOPへ戻す。
- **将来:** 仮にENG受入後もsource-firstの独立preregistration・custody・科学採点の別許可を欠く限り、`M_use=NOT_CERTIFIED`、`M_gap=UNKNOWN`、`N_rep/U/T=NOT_EVALUATED`から昇格しない。

参照: [Owner決定（正本）](https://github.com/ryonakayama234/DekaSugi/pull/174#issuecomment-6632937532) / [後継方法v2（査読済みcommit）](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md) / [Claude独立精査 R-20261104-07](https://github.com/ryonakayama234/DekaSugi/pull/174#issuecomment-6632909530) / [PR #170 凍結v1](https://github.com/ryonakayama234/DekaSugi/pull/170) / [R1-ENG](R1-ENG-2BIT.md)。
