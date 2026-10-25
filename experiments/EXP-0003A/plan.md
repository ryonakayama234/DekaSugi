# EXP-0003A — Wake–Sleep / Counterfactual Dream preregistration v1

id: EXP-0003A-PLAN-V1
status: proposed_preregistration; no EXP-0003A execution
updated: 2026-10-25
tags: exp0003a, preregistration, wake-sleep, dream, ablation

> PR 1で結果観測前に固定する方法案。**本PRではgenerator・training・DEV・FINALを一切実行しない**。レビュー・統合後のplan-v1を不変の方法正本とする。コード実装上の重大な問題で方法変更が必要なら、同一planを上書きせずv2と未開封の新しいholdoutを別途事前登録・人間合意する。

## Hypothesis / 反証可能な仮説
- H0: 同じ基本演算と探索予算では、経験から作ったマクロもDreamも未知課題の監査付き正答と実際の探索費用を改善しない。
- H1: WAKEの成功解法から、手動で技能本体を教えずに、型・body hash・出典を持つ再利用可能なSkillCandidateを決定的に抽出できる。
- H2: その候補をTRAINだけで使い分けると、独立FINALで基本演算のみの条件より探索費用が減ることがある。
- H3 (primary): 同数・同family配分の仮想課題について、技能の正例に特徴が近い例を選ぶDreamは、ランダムDreamより未知課題での技能使用の費用を減らす。**効果ゼロ/悪化も正規の結果**。
- この実験はマクロの探索上の有用性を調べる。既存DSLで表現不能な変換、新原始演算、領域間転移、総CPU高速化を初期から仮定しない。

## Scope / 介入と固定対象
- `String -> String`、既存の純粋原始演算 `trim/lower/upper` と型付き一引数ASTのみ。既存`packages/learning`の2回以上現れる部分式発見、`packages/evaluation`のSEC-004真正性検査・展開AST予算・MEASURE-0001 meterを再使用。任意Python/シェル実行は禁止。
- WAKEはTRAIN入力のみを解き、公開2つのI/O例、非公開audit第3例で成功解法を独立判定。成功解法と失敗・探索traceを`WakeEpisode`に記録。失敗は候補発見の教師正解として流用しない。
- Sleepは成功したdistinct train task_idを使い、既存`discover_skills`の`min_distinct_tasks=2`、AST正規化hash、primitive-only、マクロのネスト禁止を守る。候補を`(-occurrences, skill_id)`で整列し**先頭1候補だけ**採用候補にする。候補0個なら機能ゲートFAIL、実験を隠さず記録。技能bodyやidのハードコードは禁止。
- B1/B2/B3が使う**技能bodyは同じWAKE由来1候補**。Dreamは追加の技能発見や書き換えを行わず、技能のON/OFF方策だけを更新する。比較条件の介入は追加の訓練観測の有無・選び方に限定。
- すべての探索比較は`max_ast_nodes=4` **展開後原始ASTノード数**、`max_candidates=100`、同じ原始演算の版と列挙順を使用。ONは検証済み1候補を末尾にのみ追加し、OFFは原始演算だけ。
- 学習済み方策はEXP-0002Bの8次元pre-solve `features(TaskSpec)`を再利用。コードが既存EXP-0002Bの凍結hash検査を壊さないよう別のversioned implementationとする。近傍は8次元平均L1距離昇順、公開TaskSpec由来の不透明な`task_id`辞書順で同点処理（ID-v1規則を後述）。k=5、max_distance=0.18、close>=3、ON支持>=4、5近傍平均primitive削減>=2、監査危険があればOFFの保守的選択。近傍条件を満たさない場合もOFF。学習レコードはOFF/ONの独立paired trialによる監査付き正誤・primitive数で作る（ORACLEの事前参照なし）。
- 1周期のみ: WAKE → SLEEP → DREAM → PolicySnapshot → FINAL。複数周期・オンライン自己変更・自律的タスク選択は後続研究。

## Dataset / splitと生成規則（実装より前の仕様）
- 8 familyをこの順で固定: `identity`, `trim`, `lower`, `upper`, `normalize_lower` (lower(trim(x))), `normalize_upper` (upper(trim(x))), `reverse_ood`, `replace_first_ood`。後二者はprimitive-only DSLで表現できない陰性/領域外対照。新しい表現能力を獲得したという主張はしない。
- TRAIN=8 family ×20 = **160問**、DEV=8×8 = **64問**、FINAL=8×16 = **128問**。各問にpublic 2例と非公開audit 1例。splitごとに異なる文字集合: TRAIN `abcdeFGHIJ`、DEV `klmnoPQRST`、FINAL `uvwxyUVWXY`（ASCIIのみ）。3例は個別乱数系列で生成。文字列長3〜7、異なる文字を2種以上含み、非回文。identity以外のfamilyは表記・前後空白などを調整して非自明な変換になるよう、後述条件で棄却サンプリングする。
- 条件: identityは空白なし、trimは前または後にASCII空白を必ず含む、lowerは大文字を1個以上含み空白なし、upperは小文字1個以上含み空白なし、normalize_lowerは前または後の空白と大文字を含む、normalize_upperは前または後の空白と小文字を含む、reverse_oodは入力非回文、replace_first_oodは先頭がZ以外で先頭のみZに置換。trim/normalizeの空白は`(" ", ""), ("  ", " "), ("\t", "\n")`を問番号+例番号で周期選択。無限ループ回避の上限4096回を超えたらfail closed。
- 生成器は`random.Random(seed)`。各例で `length = rng.randrange(3, 8)` とし、`token = ''.join(rng.choice(alphabet) for _ in range(length))` を生成。2種未満の文字・回文・familyのcase条件不一致は同一RNGから再抽選し、4096試行で失敗として停止。familyの目標出力は固定参照変換から計算する。シードは衝突しない名前空間: TRAIN 110000000、DEV 210000000、FINAL 310000000、DREAM 410000000。各レコード例の`seed = master + 100000*family_index + 10*task_index + example_index` (example_index=0,1,2)。dream poolのtask_index=0..63。各split task_indexは0始まり。同一seed・同一ID・全partitionおよびDream poolをまたぐ同一公開TaskSpecはfail closed。**同一split内で偶然重なる文字列入力は許容し重複件数をmanifestで報告**（結果に合わせた再抽選は禁止）。
- DREAM候補プールはTRAINアルファベット、family各64問の**512問**を独立DREAM seedで生成し、B2/B3共通の入力プールにする。両方とも各familyから12問ずつ計**96問**を追加教師観測に使用。
- B2ランダムDream: 各familyの64プールを固定seedから導出した順序（`random.Random(510000000 + family_index).shuffle(indices)`）で先頭12件採用。B3 Counterfactual Dream: 各familyの候補と**WAKEで技能ONが監査正解・OFFよりprimitive削減になった課題**との8次元feature平均L1距離の最小値が小さい順に12件選択。同距離ならgenerator/evaluator側のID-v1`pool_id`辞書順。各familyの層化件数を同じに保ち、**類似しているのに技能が役立たない負例**を狙う（positive familyも同じ規則を適用）。参照用ON正例が0件ならB3生成をFAILとし、恣意的に条件を変更しない。
- Dreamでは生成根拠のプログラムまたは変換familyとその第三auditから教師信号を独立確認する。`reverse_ood`/`replace_first_ood`の参照変換は信頼された**benchmark generator内の正解データ生成**に限り、DekaSugiのDSL primitive/実行用Registryには追加しない。Kernel方策の入力は公開2例のTaskSpec特徴と、実際に行ったpaired search/cost観測だけ。非公開audit・family・seed・split・正解変換ID・生成元programはKernel方策の`choose`関数に渡さない。
- 公開seedの合成family評価であり、blindな自然分布テストではない。FINALの課題を事前登録後に採点したら、同じFINALを方法修正後の確認試験には用いない。

## Deterministic ID and tie-break protocol (EXP-0003A ID-v1; before any generated dataset)
- **Evaluator-only provenance IDs**: `<split>-f<family_index:02d>-i<task_index:03d>`。splitはlowercase `train|dev|final|dream`、family_indexは上記固定順の0..7、task_indexはTRAIN 0..19 / DEV 0..7 / FINAL 0..15 / DREAM 0..63。例: `train-f00-i000`、`final-f07-i015`、`dream-f04-i007`。整数のゼロ埋め幅とASCII小文字・ハイフンは固定。全生成物でprovenance ID重複を拒否する。
- **公開TaskSpec ID**: `task_id = "t-" + sha256(PUBLIC_TASK_BYTES).hexdigest()` (小文字hex64)。PUBLIC_TASK_BYTESは次の辞書のUTF-8 `json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)`: `{"schema_version":"0.1","domain":"string_to_string","limits":{"max_ast_nodes":4,"max_candidates":100},"examples":[{"input":public0.input,"output":public0.output},{"input":public1.input,"output":public1.output}]}`。公開2例の**順序を保持**する。`task_id`自体、family/split/seed、audit例、正解プログラムをこのhash入力に含めない。ハッシュ衝突または同一公開TaskSpecが重複したら全partitionとDream pool横断で**生成を停止**し、結果を見てIDを調整/再抽選しない。64hexを省略しない。
- **参照の分離**: generator/evaluatorのprivate manifestは `source_record_id` → `task_id` → `public_task_sha256`（上記sha256の64hex）と`audit_ref`/`family`/`seed`を保持する。Kernel/Skill discoveryの`TaskSpec.task_id`と`TrainingObservation.task_id`は上記`t-...`のみを利用する。並べ替えのために公開IDへ出典情報を連結しない。Generatorのメタデータやmanifestそのものを`features`/`choose`に渡さない。
- **Dreamの区別**: 全512件の`pool_id`は上記`dream-fNN-iNNN` (= evaluator-only `source_record_id`)。B2/B3は共通のpool_idとpublic `task_id`を保持し、選別された記録だけ `dream_case_id = "b2:" + pool_id` または `"b3:" + pool_id` を付ける。`TrainingObservation.task_id`はarmごと独立のsnapshot内で一意のpublic `task_id`を使う。Arm識別と`dream_case_id`はsnapshot/manifestの出典相互参照で保持し、Kernel特徴や距離には含めない。B1/B2/B3の同じWAKE観測は同じ`task_id`を使う。
- **5NN**: 各armの観測集合で `(mean_abs_L1_8D_distance, task_id)` の昇順に最初の5件を選ぶ。距離はPython binary64の8個の絶対差の和/8（追加の丸めなし）、ID比較はASCII codepointの辞書順、距離が完全一致したときだけIDで決める。同一`task_id`観測は拒否する。入力順、JSONL行順、armによる接頭辞の違いが5NNを変えてはいけない。
- **B3 pool ranking**: 先にfamilyをindex 0..7で区分し、各64 poolから `(min_distance_to_positive_wake_features, pool_id)` 昇順で先頭12件。同点の`pool_id`はASCII辞書順で比較する（幅固定なので数値index順と一致）。正例集合はTRAINでの監査正解かつprimitiveコスト削減に該当するWAKEの公開8D特徴のみによる。Dreamのauditやfamilyはgenerator/evaluator内で参照可だが、Kernelは`TaskSpec`のみ受ける。
- **B2 selection**: family 0..7の順に `indices=list(range(64))`、`random.Random(510000000+family_index).shuffle(indices)`、各先頭12個を**得られた順序のまま**選ぶ。B2/B3とも選別済み`pool_id`の**順序付きリスト**と、その対応`task_id`順序、選択前pool全件の`public_task_sha256`をfamily/index順に並べたcanonical JSONのSHA-256、選択ルール版`ID-v1`をmanifest/snapshotに保存する。集合だけを保存して順序を失うことは禁止。
- **決定性の仕様例**（実データでもスコアでもない）: B3で同一familyの候補 `dream-f02-i009` と `dream-f02-i010` の距離が完全一致したら009が先。5NNで距離がともに0.125の仮の`t-` + `"a"`×64 と`t-` + `"b"`×64は"a"側が先。入力レコードをシャッフルしても選別済み順序・近傍ID順序・snapshotsの意味的hashは不変。ID-v1違反、重複、poolとTaskSpecのhash不一致はfail closed。

## Experimental arms / 厳密な対照
| arm | 技能 | 方策の学習源 | Dream配分 |
|---|---|---|---|
| B0 | 無効（常時OFF） | なし | なし |
| B1 | WAKE由来同一技能 | TRAIN WAKE160のpaired観測 | なし |
| B2 | B1と同一 | WAKE160 + 無作為層化Dream96 | 8 family×12 |
| B3 | B1と同一 | WAKE160 + 類似度優先Dream96 | 8 family×12 |

- B1/B2/B3のKernel方法と閾値は同じ。各armの学習snapshotは独立hashで保全。FINALごとに選択を先に行い、独立meterとVerifierでB0・B1・B2・B3を計測する。事後ORACLEは診断のみ。
- B2/B3とも512問のプール生成費用を計上し、B3の特徴計算/選別CPU費用も報告。Wall/CPU、学習費用の償却は主指標と分ける。モデルが正答を直接受け取ることは禁止。

## Metrics / 実測指標
1. WAKE: 160件中の監査付き成功・失敗、発見候補数、top技能の`body_hash`・来歴・展開AST長。
2. FINAL128: 4armごとの正答数、false solved、未解決、候補数合計、canonical primitive calls、探索trace/hash、family/課題ごとの正誤・費用差、OOD32件の誤ON。
3. Primary pair (B3−B2): 同一FINAL課題でのpaired primitive差(`B2_calls-B3_calls`)、候補差、正答差、tail regressions、family-cluster bootstrap1000回・seed 260303の95% percentile区間。8 familyしかないためCIがゼロを含む場合は不確実性を強調する。
4. Cost: generator、WAKE/SLEEP、Dream評価と選別、方策学習、推論、FINAL各arm、独立auditのCPU・wall。primitive-onlyと総CPU、1/32/128回再利用の償却見積りを区別。
5. Reproducibility: Python/OS、source commit、全generator/DSL/meter/learn/policy source Git blob SHA、split manifest hash、snapshot hash、run command、freeze時刻、元データhash。

## Acceptance / 事前固定ゲート
- **Functional**: TRAINだけからdistinct2件以上の来歴を持つ型安全・pure primitive-only skillを自動発見、hash一致、偽装callback・body改変・cycle/型不整合を実行前拒否、同一seedでAST/候補数/trace再現、既存EXP-0001/0002/0002B回帰PASS。候補0件や反証対象正例0件ならFAIL。
- **Safety**: 全arm・全FINALでfalse solved=0、audit/hidden labelが学習選択の入力に混入しない、OOD32件で誤ON数B3<=B2、学習器のRegistry正式採用なし。
- **Primary numeric (strict)**: B3監査付き正答>=B2かつ>=B0、B3のFINAL総primitive calls <= B2−32、B3総候補数<=B2、B3総primitive calls<=B0。全項目を満たした場合`numeric_pass_not_promoted`、一つでも不成立なら`numeric_fail`。統計的有意・実時間の高速化はこのゲートの意味に含めない。
- **Dream-specific evidence**: 上のゲートに加えB2とのpaired結果とbootstrap区間を必ず開示。対照に対する優位が確認できない場合は「反証Dreamの改善未証明」と明記。B3≦B2でも、B1/B0との差でDream固有の有効性を言い換えない。
- **Promotion**: 数値PASSしても`DEFAULT_REGISTRY`への昇格・標準能力の採用はしない。別ADRと独立レビュー・人間判断が必須。
- infeasible・不具合・欠測の際は`inconclusive`か`invalidated`として結果と原因を保存。結果を見た後にfamily/閾値/seed/予算/計算方法を変更しない。

## Frozen execution / approval gates
1. PR 1は文書・図・契約・run目録のみ。新機能コード、データ生成、DEV/FINAL、評価起動CI追加なし。文書チェックと既存回帰CIは可。
2. PR 2はTRAIN限定でgenerator、WAKE/SLEEP、証拠型を実装・検査。PR 3はDream・方策更新をTRAIN/DREAM fixturesで検査。各PRでARCH-001/002/UI責務・run目録を同時更新。PR上でDEV/FINALは採点しない。
3. DEVを開く前にplan-v1との一致、source manifest、生成器source・全split dataset hash（採点せず）、TRAIN snapshot・Dream selection hashesを固定して別コミットに保存する。DEVは工学診断のみ、方策/閾値/生成規則の再学習・調整には使用不可。
4. 独立したexact-headコード/研究方法レビューとCIの後、FINAL起動だけを別の人間承認付きPRで開く。初回レビューの重大な指摘・hash不一致・実行条件不整合なら**実行前に停止**。FINAL評価結果を一度だけ保存・独立再集計後、起動ゲートを削除。
5. 研究方法の変更が必要なときは同じplanの上書きや既開封holdoutの再採点で正当化しない。v2+新seed+新FINALを未評価のうちに再合意する。

## Limitations / 中止・相談条件
- 一引数DSLのマクロ化だけで`reverse`や`replace_first`が解けると主張しない。発明とは「既存操作の再利用可能な合成」であり、新しい原始意味論ではない。
- 別familyでも演算意味は同じ。データが合成であること、公開seedであること、8 familyの統計的限界、学習/推論費用が削減より大きい可能性を常に明記。
- この計画どおり実装できない、学習・評価分離を守れない、PR1への独立レビューでP1/P0の疑義が出た場合は、勝手に研究方法を変えずユーザーと相談する。

Related: [architecture](../../docs/architecture/system.md) / [contracts](../../docs/architecture/contracts.md) / [spec](../../docs/specs/EXP-0003A.md) / [UI correspondence](../../docs/architecture/ui-panels.md) / [run index](runs/README.md) / [previous FINAL](../EXP-0002B/runs/20261025-final112.md).
