# EXP-REP-004R — 研究・技術・測定統合決定稿 v1（設計のみ）
id: EXP-REP-004R-DECISION-V1
status: DESIGN_DECISION_CANDIDATE / NOT_IMPLEMENTED / NOT_SCORED / NOT_F0_FROZEN
updated: 2026-11-02
tags: research, experimental, architecture, preregistration-candidate, learning-curve
issue: https://github.com/ryonakayama234/DekaSugi/issues/139
parent: https://github.com/ryonakayama234/DekaSugi/pull/138

## 0. 決定の射程
対象は単一の工学実験 EXP-REP-004R。**G0で手法・比較・停止規則を記録し、G1–G6を連続した作業パッケージとして進める設計**。ただし各前段のfail-closed gateを通過しなければ後段を実行しない。歴史的REP004の学習済みSnapshot・1,920行の生採点・出典SHAは不変。古いF0/DEV/FINALや個人情報・秘密の評価結果にはアクセスしない。学習済み「知能モデル」の正式採用、main merge、独立封印FINALはこの決定稿では認可しない。

**主対象モジュール**: packages/rep004 内の条件付きConceptBodyのロール束縛/照合、固定対照の推論重み・予測選択。補助: テスト、実験ランナー、provenance、ARCH-001、ARCH-002、AGENTS、INDEX。

## 1. 観測済みの事実と未証明の主張
REP004（PR #138, head 24e660d）では TRAIN64=32個の異なる意味構造を64世界で観測、6,400 paid actions、7個の型付き実行可能概念、Snapshot保存→再読込→USE、48世界×8条件×5予算=1,920 disclosed scoringを実施。未知組合せの LQ=0.700000、LA=0.705208、FA=0.760417、STATIC-MACRO=0.700000。78/240の比較で質問経路変更。これは仮説生成を許す探索的証拠であり正式な独立評価ではない。
独立Codex review P1: 条件付きガードが固定スロット2へ束縛され、alpha-renamingで照合結果が変わる。P2: weights_forは空の学習ライブラリで早期returnし、STATIC-MACROの固定文法まで無効化する。未修正測定を純粋な学習因果効果として採用しない。
現行OOD群12個は全て名前を変えた3段連鎖の変種。**12独立した文法外意味ファミリーではない**。TRAIN曲線で「SEEN_ROLEBLIND」の固定12はn<32では必ずしも既知とは限らない。

## 2. 研究対象（操作的定義）
- **Mechanism validity（必要条件）**: 解釈した概念の意味が対象番号・並べ替えに不変で、保存済みbodyの入替えがその実行・候補重み・合法質問/予測に伝播する。
- **Learned query utility（性能）**: 同一Snapshot・予測器を共有したLQ（概念を質問に使用）対LA（質問には使用しない）の未知構造における事前固定した家族単位の予測差。
- **Unique learned value（独自の学習価値）**: 強力なFAに加え、学習無しで同じ7種の意味を事前実装したSTATIC-MACROを上回るか。
- **Reliability/limits**: 観測不足と文法外矛盾を区別し、強制的な0点棄権や不確実性の過大な主張を避ける。
- **Total cost**: 訓練・Sleep・Snapshot保存/読込・質問・推論・キャッシュの実コスト。性能のみで省計算を主張しない。
この実験は概念**文法の自律的発明そのもの**や汎用対話知能を評価しない。

## 3. 反証可能な仮説と帰無仮説
- **H-INV**: 4対象の任意の24置換 π に対し、各適法な候補Eで match(C,E)=match(C,π(E))。さらに状態/操作も同時にπ変換したとき、概念が予測する次状態は共変。反例一件で失格。
- **H-CONTROL**: STATIC-MACROの重み・質問・予測は、同一候補・公開観測・予算のもとでTRAIN0/64の学習ライブラリに依存しない。反例一件で失格。
- **H-ACT**: learned bodyを活性/遮断・合法な意味変更した際、公開履歴だけを用いたUSEのbody実行が確認できる。意図した対照差を必ず示す固定fixtureを保持する。これは性能証拠ではない。
- **H-Q**: 未知組合せ12意味ファミリーで平均 Δ(LQ−LA)>0。帰無: Δ<=0。追加の探索的実用閾値 +0.02 は「性能候補」への進路判定であり有意差検定ではない。
- **H-UNIQUE**: 同群でΔ(LQ−STATIC-MACRO)>0かつ Δ(LQ−FA)>0。帰無: いずれか<=0。成立しなければ独自知能獲得の主張を却下する。
- **H-DOSE**: 選択したTRAIN exposure水準によって性能/概念数/原始操作費用に変化がある。帰無: 新規意味ファミリーを増やしても有益な変化なし。方向・単調性は決め打ちしない。
- **H-OOD-DIAG**: 既知の探索上限内で矛盾を検知したときだけ棄権可能。未検知を「文法内の証拠」や「校正済み」と呼ばない。現行1トポロジー12別名は探索的な診断に限る。

## 4. 技術選定と棄却理由
- Python 3.12+標準ライブラリ、CPU、WSL2/Linux、既存の型付きAST/純粋インタプリタ/JSON-SHA256を維持。可観測性・再現性が高く、変更の因果帰属に適する。
- 本タスクはREP004を局所的に修正する。DSLを大規模再設計しない、GPU・SGD・外部LLM・学習ライブラリの自動昇格を導入しない。
- ロール束縛は body(source,target,guard) の抽象スロットを候補内の実対象番号へ単射対応する**明示的なRoleBinding**で行い、guard=-1の無条件形は guard=Noneで記録する。実行時・照合時の座標系は同一とする。単にAST内の名前を書き換えるだけの見せかけ修正を禁止。
- 固定対照は独立したSTATIC_LIBRARY_DIGESTと独立経路で生成し、Snapshot.libraryが空でも同じ重みが出る。共通するのは公開仮説・候補生成・計算予算・型付き実行器のみであり、学習産物や頻度表には依存しない。
- 2辺同時XORは**pre-action state**で判定し、順序に関係なく同時反映する。CHAIN等のmotif名一致だけでは新しい意味の獲得を示さない。
- コード責務: role binding/matching, baseline configuration, query planner, Snapshot integrity, source/evaluation accountingを小さい純粋関数単位で分けて試験する。既存1ファイルの分割は必要な範囲に限る。

## 5. アーキテクチャ・独立境界
~~~mermaid
flowchart TD
    H["Host-only world / hidden rule"] --> S["Charged Session: set/pulse"]
    S --> T["Public ObservationTrace"]
    T --> L["Sleep: infer semantic models and typed AST"]
    L --> N["Snapshot + SHA256"]
    N --> R["RoleBinding + ConceptMatchWitness"]
    R --> I["Typed AST interpreter on public hypotheses"]
    I --> W["LQ: learned weights"]
    F["STATIC-MACRO: preinstalled independent grammar"] --> Q["Query planner under same budget"]
    W --> Q
    Z["LA / FA / fixed controls"] --> Q
    Q --> P["Committed prediction + action trace"]
    P --> V["Independent-in-interface disclosed evaluator"]
    H --> V
    V --> O["Append-only score receipts / immutable history"]
    V -. "no hidden truth into learner" .-> T
~~~
注: Mermaidの破線は『渡さない』という禁止関係であり、情報フローではない。当前のevaluatorは同一研究環境の disclosed synthetic scorerで、独立カストディを保証しない。

## 6. データ契約（ARCH-002と同期）
- RoleBinding/1: {source:int,target:int,guard:int|null, public_ids_digest:str}; source!=target、guard有りならsource/targetと相異なる。guard無しを意味上の位置2へ偽装しない。
- ConceptMatchWitness/1: {snapshot_sha,body_sha,candidate_signature_sha,role_map,matched:bool,permutation_certificate_sha,interpreted_transition_sha,valid:bool}。trusted truthは禁止。測定モードは集約時にwitness全件のストレージ費用を計上。
- ComparatorConfig/1: {arm,policy_sha,static_library_sha|null,learned_library_access:bool,query_body_access:bool,prediction_body_access:bool,budget}; armsを文字列条件の偶然に依存させない。
- Snapshot/1: 元のcanonical payload+digestを維持。変更が必要ならschema/2と移行器を新設し、旧snapshotを黙って書き換えない。
- ScoreReceipt/1: {source_commit,manifest_sha,train_snapshot_sha,train_worlds,distinct_semantic_families,arm,family_id,stratum,seen_in_train,budget,preaudit_prediction_sha,exact_correct_out_of_64,abstained,paid_actions,model_checks,logical_body_calls,physical_body_evals,cache_hits,cpu_seconds,phase_costs,run_provenance}.
- RunProvenance/1: {experiment_id,source_sha,method_sha,policy_sha,dataset_sha,engine_version,python_version,run_group,run_status,raw_sha,retrospective_or_prospective,review_status}.
- Truth / family / seed / oracle output はlearner-facing public APIへ投入しない。評価器のみが真値を持つ。

## 7. データ・分割・設計空間
既存の公開人工文法を維持: 4 Boolean対象、各set/pulseが課金1、候補文法は0〜2辺の同時XOR・無条件/条件付き。1,831構文候補/1,735意味シグネチャ/85置換同型ファミリーをテストで再照合。現行研究用manifest（TRAIN32、既知参照群12、未知CHAIN12、未知その他12）とOODの3辺連鎖12別名例を固定して再利用するため、今回のスコアは**同じ公開開発集合上の修正後診断**に限定。
TRAIN exposure=0/3/8/16/32/64、各世界100 paid actions、64世界時点の意味ファミリー数は32。訓練投入順は現行ソースで固定されているため低nでの学習曲線はORDER-CONFOUNDEDと明記。追加の学習順序/分割への一般化は新しい研究IDで扱う。
固定のSEEN_ROLEBLIND stratumラベルはn<32で事実でない可能性がある。生データに per-task seen_in_train を付与し、固定参照群という名称と実際に既知かの属性を分ける。共有した評価集合をnごとに切り直して都合よく効果を出すことは禁止。OODの12行は1 topology clusterである旨を明記し、12独立ファミリー扱いしない。

## 8. 比較条件・推定量・費用
腕: LQ（学習bodyを質問/予測へ）、LA（学習bodyを予測へだけ）、STATIC-MACRO（固定bodyを質問/予測へ）、FA（強い固定文法・学習priorなし）、LR（学習ランク）、ER（episode再利用）、BODY-OFF（bodyなし）、FX（固定質問列）。各armの共通コードと許される情報、学習訓練費用、補助キャッシュ初期化を検査する。
主指標: 知らないCHAIN組合せ12意味ファミリー、B={0,1,2,4,8}の家族単位平均64遷移正答率。family f について D_f=(1/5) Σ_b [Y(LQ,f,b)−Y(control,f,b)], Y=correct/64 (ABSTAINは事前規約として0 utility)。Δ=(1/12)Σ_f D_f。必ず signed per-family deltas、paired差、全腕、全部の予算を報告。64 audit遷移や5 budgetを独立した母集団サンプル数として扱わない。
探索的工学候補判定: Δ(LQ−LA)>=+0.02、Δ(LQ−STATIC-MACRO)>=+0.02、Δ(LQ−FA)>=+0.02、LQ対LAが12中少なくとも9ファミリーで正、かつ回帰/費用/境界PASS。これは厳格な目安であり科学的有意性・正式採用ではない。NULL/NEGATIVEは不合格として保存する。
並列armは各world/budgetで別セッション・同じ予算/開始状態・同じ公開許可操作。学習費用は勝手に対照へ無料配賦しない。総償却費用の算式: per-use equivalent cost = C_train/N + C_sleep/N + C_snapshot/N + C_use としN=1,10,100を説明的に出す。CPUは統一実行機のprocess-timeとcache設定を併記し、異機比較は主張しない。

## 9. 学習・使用・採点の一括計画
G0: 仕様・方法・manifest/policy/source/hashと停止規則をコード実装より先に固定（この文書は合意候補、未凍結）。
G1: 旧コードでP1/P2が再現する失敗fixture、役割単射と24置換、4 bit全16状態×4 pulseの共変性試験、同時XOR、bad evidence拒否。
G2: 最小修正＋全テスト/文書CI＋独立exact-headレビュー。未解決P1/P2ではスコア実行禁止。
G3: 実際の公開TRAIN 0/3/8/16/32/64でSleepから7種またはその部分集合の候補AST、Snapshot save/load/検査、別プロセスfresh USE。Snapshotの概念数・witness・データハッシュを記録。少量repeat/idempotence検査は実際の新世界投入と区別する。
G4: 学習済みSnapshotを再読込し、未知公開人工世界で合法課金質問を実行・予測事前確定・観測と予測を記録。bodyの有効化/変異/無効化による差分と反例を保存。
G5: 各train sizeで48世界×8腕×5予算=1,920行、合計6 exposureなら11,520行の新しい disclosed score。64 audits×11,520=737,280は独立サンプルでない。公開の同じsuiteを全条件で反復するためconfirmatory holdoutではない。必要ならデータソース固定順で分割実行し全hash連結を照合する。
G6: 新原本SHA/相関を保った家族別差・失敗例・OODの非同定性・費用を記録し、独立レビュー、採否と次期研究仮説を報告。原本はappend-only、歴史1,920行の再ラベル/上書き禁止。

### 停止条件と権限境界
P1/P2の回帰・Snapshot/hash・観測隔離・費用計測のいずれかがFAILした場合は以後の採点を行わずFAILレコードを保存。新規学習と公開人工世界での訂正後工学採点を本タスクの標準完走工程とするが、過去の封印済みF0/DEV/FINALは使用しない。正式に別所有の新F0/FINALへ進むときは別途、実験者から隔離された評価データと独立レビューが必要。main統合・モデル昇格は別ゲート。
結果が≤固定FA/STATICならResearch Referenceのみの保存、Validated Baseline/Model Releaseへの昇格なし。

## 10. 企画全体との関係
EXP-REP-004Rは「学習した概念を正しく使い、正しく比較できるか」という計測基盤の修復であり、本来の長期研究――未知世界での表現不足診断→能動的反例取得→述語/概念発明→Wake-Sleep再利用→領域横断転移――を代替しない。次の別IDでRepresentation Repairを検討する。対話も将来的には相互が仮説を変える介入/観測の一形態として検討するが、現段階の固定Boolean世界から汎用対話能力を主張しない。

## 11. 文献上の位置づけ
DreamCoder（Ellis et al., PLDI 2021）は記号ライブラリと探索方策の共同学習が有効な課題の例。ただし本試験には認識ネット・真の意味文法発明はない。介入設計とモデルのmisspecificationの研究は、情報量最大化の質問だけで未知文法への安全性が成立しない点を示唆する。引用は将来の研究動機であり本実験の成績証拠ではない。
- https://doi.org/10.1145/3453483.3454080
- https://doi.org/10.3982/TE2480
- https://proceedings.mlr.press/v300/tang26d.html
