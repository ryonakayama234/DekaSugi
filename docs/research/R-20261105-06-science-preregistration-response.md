# DIAG-R-20261105-06 — 科学段階の事前登録設計回答（QS1–QS8）

id: DIAG-R-20261105-06-SCIENCE-PREREGISTRATION
status: response_proposal / draft / docs_only / no_experiment / no_scoring / no_source_selection / no_sealing / pending_muse_review_and_owner_decision
updated: 2026-11-05
tags: gate-r2-m-science, preregistration, response, effective-h0, causal-use, closure, independent-custody

> **権限と限界:** [質問票 DIAG-Q-20261105-06（PR #179）](https://github.com/ryonakayama234/DekaSugi/pull/179) のQS1〜QS8へ番号どおり回答する。本書は採用済み[方法v2](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md)を変更しない**判断案**であり、事前登録確定稿でも科学段階GOでもない。source抽選・真のUSE採点・封印・policy変更・実装・過去データ再実行は一切しない。Ownerの正式許可とMuse独立精査を要する。
>
> **まず結論:** 第一推奨は**QS1(c) 二つの独立した登録を設計し、A（現行在庫）を先行させる**。ただしAの主評価は「保存による予測能力の増加」ではなく、費用・経路・保存の運用効果である。B（新環境／新policy）は**別の方法版・前登録・実装審査・Owner許可**が揃うまで実施しない。Bが恣意的なOFF弱体化にしかならないなら**取りやめる**。現時点の判定は M_use NOT_CERTIFIED / M_gap UNKNOWN / N_rep・U・T NOT_EVALUATED のまま。

## 根拠の照合と研究上の立ち位置

- [PR #176](https://github.com/ryonakayama234/DekaSugi/pull/176)、[#177](https://github.com/ryonakayama234/DekaSugi/pull/177)、[#178](https://github.com/ryonakayama234/DekaSugi/pull/178) のR2-M-ENG各段階はmainへ着地済み。mainの固定F00は episodic_exact → h0_consistent → runtime_affine_decoder を合法に保持し、F10との差は原則route/費用にとどまる。[実装](../../packages/r2_m_eng/dispatch.py)と[Stage 3仕様](../specs/R2-M-ENG-STAGE3.md)を確認。
- **追加の強い注意点:** Snapshot復元自体が public historyからbodyの係数復号と検証を再実行する。したがって「USE時にdecoderを単にdispatchから消す」だけでは、復元時の再計算や他の合法ルートという抜け道を残す。Bはこの情報・時相・計算権限を**双方同じ条件で**定義し直す必要がある。
- F_aff（3bit affine 16法則）の公開4点 P=(000,100,010), Q001 は係数(d,a,b,c)を完全に特定する。これは**人間が提供した族・復号規則による識別**であり、未知の概念意味論・F_affそのものの発明ではない。
- [R1-ENG](../specs/R1-ENG-2BIT.md)は全4点公開によるlookupで因果差なし。[OPPORTUNITY-001](../../experiments/OPPORTUNITY-001/runs/20261029-train64-real-paired-recount.md)は64ペアで片側だけ正解0・UNDERIDENTIFIED。[#166](https://github.com/ryonakayama234/DekaSugi/issues/166)は公開混合の適応機会ゼロでSTOP。これらを新sourceの陽性証拠に変えない。
- 指針: [REPO-GOV-001 #146](https://github.com/ryonakayama234/DekaSugi/issues/146) は同時進行を絞り、独立査読・Owner意思決定を要求する。[方法v2 §5.2](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md) の D_use は、同じSnapshotと合法fallbackを維持した予測または合法行動の差に限る。

---

## QS1 在庫の宣言（中心質問）

### 推奨
**(c) 二段構え。ただし二つの相異なる研究質問を厳密に分離する。**

**登録A／現行在庫の忠実な評価（最初に設計・承認）:** mainの現行R2-M-ENG固定policy、runtime decoder、Snapshot復元時再復号、全合法fallbackを保持する。F00とF10の私的USE予測差をprimary positive endpointにしない。事前に D_use=0 が構造的予測であることを明記し、経路差、decoder・validator呼出、static/実行時ASTメータ、CPU/wall、RSS、保存/復元bytes、USE反復回数別の生涯費用を**別単位**で測る。Aの証拠上限は「この実装での保存・再構築コストと配線の差／機械的再現性」。M_use・M_gap・新概念・知能向上は主張できない。予測差が意外に発生した場合はまず漏洩/dispatch不一致として監査し、自動的に陽性化しない。

**登録B／環境制約下のpersistent-body利用（将来の別登録に保留）:** **新しいpolicy版**に対し「学習時は公開照会・構成できるがUSE時の合法操作、計算枠、公開資料へのアクセスが変わる」という現実のタスク環境要件を**source前**に固定できた場合だけ検討。両armで同じUSE環境・Q・メモリ・Snapshot・計算量の規則を課し、OFFはlearned bodyの実行のみ無効にして**そのpolicyで最初から合法な全nonbody経路**は残す。初期在庫を作る前にその配線、理由、許容経路、隠れた復元時復号、固定macro/充分統計による代替を公開監査する。Bは方法v2の現行F00を遡及変更した同一実験ではなく、**別方法版の条件付き因果使用試験**。成立したとしても主張上限は「指定されたUSE制約下の永続body利用（M_use候補）」であり、静的H+・完全固定macro・同情報の充分統計対照に勝たない限り新能力/Uを主張しない。

**最強の反対意見:** 同じ公開4点から16法則の係数が一意に得られるので、USE時decoderを禁止したBは必ず実験者がOFFを弱体化しただけではないか。しかもSnapshot内の公開履歴と復元時復号から予測関数は再計算可能で、固定macro16個でも同精度を達成する。この反論は**現行システムについて正しい**。ゆえにBを現行method-v2の陽性救済策としては採用しない。真に独立した環境制約（例：有限deadline・利用不可の外部入力・phase-specific計算権限）が実在し、両側同条件で別実験として意味を持つことをMuse・Ownerが証明・承認できない限り**B NO-GO**とする。

### 根拠
- 同じ公開回答ベクトル r=(r000,r100,r010,r001) から d=r000, a=r100 XOR r000, b=r010 XOR r000, c=r001 XOR r000。OFFの合法runtime decoderがこの復元を行えば予測機能はONと同一。探索される16候補というより「既知F_affを1回復号する」方式である。
- 「観測4bitという十分統計が利用可能」「係数復号を利用可能」「予測に同一公開情報を利用」を同時に認めるなら、情報論的な新規予測能力の差は生じない。持続化は時間・資源配分の変換に過ぎない（この限定された設定での推論）。
- 固定macro対照やSTATIC-H+は、弱いOFFだけを打ち負かして過大主張することを防ぐ。

### 棄却した代替案と理由
- **(a)だけでM_use科学陽性を狙う:** 識別不能な主評価を立てるため不適切。Aはあくまで保存/費用の限定研究。
- **(b)を現行method v2のまま直ちに主評価へ移す:** 明示採用済みの「既存合法fallbackを切らない」条件に反しINVALID。復元時decoderも未整理。
- **(c)をA結果に都合よくBへ即時切替える運用:** 後付けmethod selectionとなる。Bは対象/閾値/根拠を事前独立凍結できなければ停止。

## QS2 閉包監査の格上げ

### 推奨
未解決5件を**科学実行ゲート**と**認定ゲート**に分ける。Aで科学結果と称するなら(1)source-first独立監査、(5)外部原本/前登録/採点権威は**実行前必須**。追加して、F00/F10の全**実際に接続されたroute**と復元処理、同一資産・合法操作・予算の監査はM_use比較の実行前必須。(2)全合法historyの網羅証明、(3)全可能方策に対する最良OFF証明、(4)同予算H+対OFFの非実現可能性証人は、**M_gapや実効表現修復を主張しないAではUNKNOWNのままでよい**。ただし(2)の未解決を隠して「全合法fallback監査済み」と呼ばない。Bで既存OFF経路が何か曖昧ならM_useも実行不可。

**手順案:** Research Leadが読むだけのsource-first dossier（対象commit/依存import graph/route map/各history遷移・復元計算/保存統計/各armの合法行動とB/negative tests一覧）を作り、Museが**同じ原本を独立に**確認してP0/P1指摘を返す。Ownerが監査合格とscience gateの可否を別決定する。Research Lead自己監査のみでは不十分。秘密law・私的正答を見ず、公開の方法・コード・路線だけを監査する。独立source受託者はこの監査の後に鍵を持つ。

### 根拠
方法v2 §4のCOMPLETE基準とUNKNOWN正直宣言の両立。M_useの最小要件は合法なON/OFF介入の真正性であり、M_gapの全到達可能方策の完全性と区別できる。

### 棄却した代替案と理由
- **すべてCOMPLETEまで科学Aを全面停止:** 費用・経路比較に不要な高額な証明を混同。ただし真のM_gap認定なら必要。
- **UNKNOWNなら無監査で実施:** 隠れdecoderや非合法なOFF削減による見せかけの差を排除できない。
- **自己監査のみ:** source選択/解析と監査が自己完結し、独立性がない。

## QS3 独立sourceと封印

### 推奨
**Ownerをsource custodian / 抽選実行者、Museを事前方法・seal手続の独立監査者、Research Leadを公開データのみ受け取る学習・評価案作成者**とする。Ownerが研究実装を触る場合はcustodianをMuse等の別人へ分離するか**独立custody未確保→NO-GO**。誰がどの秘密を知るかを権限表で先に凍結する。

1. 科学GO前にfamily、抽選母集団、分布、除外済みの過去公開target群、試行数、端点、全arm SHA、seeds扱いを固定。**既公開parity3の真理値表・それを使った既存artifactを独立確認sourceに再利用しない**。F_affの有限16法則はすでに仕様として公開済みなので「全て未知family」と誤称しない。
2. 新たなsource抽選時、Ownerがオフラインで暗号学的乱数から各lawを選ぶ（重複可否・分布は前登録）。選定器は指定された方法・候補母集団だけを参照し、学習器の実行結果、USE score、モデルのtrialごとの出力を閲覧しない。方法上の既知情報とtarget-specific結果の非共有を区別する。
3. 各秘密payload（登録ID、法則係数、抽選seed、指定split、対象digest、nonce）をcanonical JSON化し、**ランダム256bit nonce付き SHA-256 commit**を公開先行登録。16候補のlawだけを裸hashすると総当たりで秘密が漏れる。payload/nonceは外部のOwner管理領域に保存し、commitより前に学習側へ渡さない。発表前の公開commitは法則や答えを含まない。
4. 公開Pと合法Q001応答のみを定めた時系列で学習側へ渡す。各USE出力の前commitを監督者/Ownerの別管理のappend-only原本へ写したことを検証後、Ownerがcommit-then-revealしてsalt/seed/法則と照合・スコアし、監査receiptを追記。
5. 既公開exampleのファイルSHA・law係数を「不適格既知例レジストリ」に事前列挙。重複判定を秘密選定側で行い、結果を見てから除外を変えない。**ただし母集団を除外で狭めること自体の偏り**は明記する。

**限界:** Owner/Museの運用上の独立性は暗号だけでは保証されない。GitHubのローカルhashとcommitにはそれ単独で第三者時刻証明・閲覧制御の保証はない。外部の不変な登録サービス（例：OSF Registries）を利用する場合もOwnerが別途実施・確認する。source selectionも封印も本書では未実施。

### 根拠
4bit程度の秘密を直接hashするだけでは簡単に総当たりされる。先行ランダムnonceによるcommitは隠匿と後日の開示照合を両立できる一方、学習担当者と秘密保管者の役割分離が必要。

### 棄却した代替案と理由
- **Research Leadがlawを選び同時に学習実行:** 独立性がない。
- **公開targetの裸SHAを先行公開:** 総当たり可能。
- **GitHub hashだけで第三者保管を代替:** timestamp/秘密保持/改ざん防止の独立性不足。
- **過去parity fixtureを新sealed真値に再分類:** 既知対象で独立性違反。

## QS4 評価設計

### 推奨
**Aに限定した数量案（すべて未採用・未実行）:** 12個の**独立なlaw抽選エピソード**（指定の有限F_aff母集団から、事前分布に従い各回抽選。重複可なら重複も全件記載）。それぞれ P=(000,100,010) の3公開点、Q001の1有料照会、fresh USE入力4点=(011,101,110,111)を**全部**使用。選別した成功点だけで評価しない。各エピソードで7arm×4 USE点を個別fresh processとする案（現行runnerは1入力点仕様なので**将来の新実装/独立審査が必要**）。USE入力の順序はsource前に固定または決定的shuffleを凍結。**N_episode=12、N_use=48 paired points**。ただし4点は同一lawのclusterであり48個の独立標本と数えない。同一F_affの抽選を繰り返しても**独立機構familyの N_rep や T は満たさない**（N_rep_family=NOT_EVALUATED、T=NOT_EVALUATED）。

- **事前の主要判定（機構）:** D_use(e,u)=1[(prediction,legal_action)_F10 ≠ (prediction,legal_action)_F00]（方法v2 §6相当）。episode単位 D_episode(e)=1[4 USE点の少なくとも1点でD_use=1]、総数 K=Σ_e D_episode(e)。同一Snapshot/公開/費用規則、commit-before-score、全fallback維持が成立して初めて Kを解釈。Aの**事前機構予測 K=0**であり、K>0ならまずINVALID/契約逸脱を調査する。**M_useはAでNOT_CERTIFIEDのまま**。経路差/保存費用の符号はD_useに含めない。
- **費用の主たる記述的評価:** Aでは予測成功の有意差検定をprimaryにせず、F00/F10について①デコーダ/validator/候補/走査、②実行時AST訪問・原始演算、③wall/CPU/RSS、④bytes・paid Q、⑤ n回利用時の C_life(n) の**費用ベクトル**を提示。n∈{1,4,16,64}を将来の事前登録候補とするが、n=64の繰返しはUSE点の新規独立証拠でなく**コスト反復**と明記。学習・復元の再decoder、Snapshot生成、全16固定macro事前構築を各armのlife ledgerに含める。費用次元を事後に恣意的加重合算しない。時間測定は同じPC・Python・CPU状態・起動順の対称化で実施し、ノイズ幅は繰返しで報告。
- **対照:** STATIC-H+は公開4からUSE時1回再decoder（必須）、FIXED-MACROは16-entry作成・占有容量を前払い含め必須。EPISODIC-EXACT、NEAREST-1NN、STUMP-1も仕様v2通り必須。比較しても**F00へ新fallbackを後付け注入せず**、既に存在する正当な経路はOFFに残す。ORACLE-REFはevaluator-only、F01/F11は引き続きNOT_EVALUATED（許可なしに起動しない）。
- **独立性・統計:** 12 law抽選は1 family内の反復。母集団が高々16法則なので普遍的な学習や独立family差を統計的に実証しない。各law×4点の結果表・K/12と欠測/INVALID内訳・費用分布/誤差を全件記述。最初に定義したK以外の後付け陽性endpointを使わない。正式な信頼区間/検出力・CPU閾値・停止境界は、source前に独立レビュー・Owner凍結が必要。Bで陽性狙いのpower設計は新方法で最初から行う。

### 根拠
4個のUSE点は完全固定の有限集合なので「有利な問題だけ選ぶ」自由度を消す。各lawでON/OFFペアにすればsource差を統制できる。小さいF_affに対し疑似反復で独立family数を誇張しない。

### 棄却した代替案と理由
- **48個を独立N_repとする:** 同一law由来の相関と同一生成機構を無視。
- **parityなど陽性を見込むlawだけ選ぶ:** 事後選択と既知例再利用。
- **OFFからdecoder/代替routeを削りKを稼ぐ:** 本方法ではINVALID。
- **対照をSTATIC-H+なしの弱いbaselineのみとする:** 永続bodyの独自性を誇張。
- **F01/F11を今起動:** 学習policy/容量/予算が未凍結。

## QS5 費用と運用負担

### 推奨
Aでは小規模WSL2/Linux・Python標準ライブラリ・ローカルCPUで完結する設計。**必要な実行単位の算術見積り:** 1 episode=7arm×4 private inputs=**28 fresh children**、12 episode=**336 children**、Qは12 paid actions（実験内課金単位であり外部決済ではない）、公開初期点36、公開追加Q12、private USE比較点48。1 childに仮のwall hard cap=5秒を設定した場合、**child時間の保守的上限は一episode140秒、全体1,680秒＋source/準備/監査/起動等の時間**。これは**現行実測ではなく設計上限案**で、source前に無害な工学fixtureで妥当性を確認し、Ownerが数値を承認するまで科学実行しない。timeout/超限は個別INVALID/STOP規則に従う。RSS cap/CPU/wallの実数値は現段階では未計測、捏造しない。

Ownerの最小立会いは**設計/母集団承認1回、sourceとsalt保管・precommit確認1回、全出力commit後の開示1回、最終判定1回**の4 checkpoint案。通常の個別USEを逐一監視する必要はないが、custody原本と異常停止時の承認はOwnerが持つ。追加の外部有料API、GPU、クラウド課金は設計上不要。電力・人手・外部時刻証明サービスの費用は「ゼロ」とは断言しない。Owner立会いの上限時間（提案: 合計60分以内、独立査読を除く）は採用前に合意が必要。

### 根拠
現行R2-M-ENGは小規模の有限Bool演算と7arm fresh childの人工fixtureを実装済み。科学用の原本保管・全USE4点のrunner拡張・外部閲覧権限の整備は**未実装**で、その工数をゼロとしない。

### 棄却した代替案と理由
- **1点のfixture速度を本物の科学実行時間と断言:** 実測がない。
- **全部のUSEをOwnerが毎回手動承認:** 小規模運用に不釣合いで人為的選択の余地も増す。
- **高額なクラウド／大きなGPUを初期必須:** 有界16法則の評価に不要。

## QS6 STOP / INVALID と結果の解釈規則

### 推奨
方法v2 §7（質問票でいう§6のSTOP/INVALID論点を含む）を、**優先順位付き判定木**として前登録する。

1. **INVALIDが最優先:** source/seed/private答え漏洩、未承認source・split・tie/容量改変、禁止Q/事前commit欠落、Snapshot上書き、独立性破綻、非法OFF弱体化、隠れた復元経路削除、原本custody不一致。隔離・証拠保持・Owner承認なく再試行なし。事前登録の全試行数/INVALID数も透明に報告。
2. **次に識別・計算ゲート:** Q001拒否/応答期限切れ/公開情報不完備なら UNIDENTIFIABLE、候補・時間上限なら SEARCH_INCOMPLETE、public validator不一致なら VALIDATION_FAILED。既存H0で十分なら SUFFICIENT_H0、限定H0だけ不足なら MISMATCH_CANDIDATE（M_gapではない）。各ラベルと原因を公開し、陰性を成功へ変換しない。
3. **有効なペアのみ事前指定Kを記録:** AでK=0なら**「現行在庫では保存bodyが予測・合法行動を変えなかった」**との範囲内NULL。命題「汎用的な概念獲得は不可能」「永続化に価値なし」は言えない。経路/費用改善があってもM_useではない。K>0なら配線・source・OFF合法性を精査し、想定外差と記載。原因不明ならINVALID/NOT_CERTIFIED。**有意差がない＝同等性の証明**とも言わない。
4. **次分岐は結果前に固定:** A NULL→Aの陰性を保存し、費用のみ事前基準で結論、Bの独立policy成立条件を審査。B環境の正当化不可→B STOP。費用も利点なし→現路線はSTOP/REDESIGNをOwnerへ勧告。新法則族への拡張、未知の新文法/新概念発明は**別研究ゲート**でありNULLの事後救済に使わない。Aで有効な費用差が出てもBの自動GOにはしない。

### 根拠
安全性/推論の順番を固定すると結果に合わせた除外・成功定義の変更を抑える。[#166](https://github.com/ryonakayama234/DekaSugi/issues/166)の陰性STOP、歴史的封印を保存する運用と整合。

### 棄却した代替案と理由
- **NULL後に法則族や用途を無制限に変更:** 選択的報告。
- **INVALIDだけ除き成功率100%を表示:** 母集団と停止率を隠す。
- **検査済み機構が予測に寄与しなくてもroute差をM_useと呼ぶ:** 方法v2のD_useに違反。

## QS7 事前登録文書の形式と凍結手続き

### 推奨
**本ラウンドは回答＋構成案まで**。Ownerが設計方針を採択したら**A用前登録稿**を別のdocs-only Draftで作り、Muse方法/安全精査→Owner署名付きの採用判断→main merge（確定SHA）→必要なら外部read-only timestamped registryで凍結→その後のsource抽選とseal、最後に**別途**science execution GOとする。source/scoreを見た後は古い前登録を上書きせず、v3等の新ID・新digest・逸脱表を新規登録する。GitHub上のmerge commitだけを絶対不可変・独立保管と誤認しない。

**前登録案の章立て:** 1 authority/原本SHA・研究質問・主張上限、2 provenance/歴史的除外、3 inventory/dispatch/restore/閉包UNKNOWN、4 source抽選・独立保管・脅威モデル、5 公開/私的分離とprecommit/nonce、6 arm・同予算・費用単位、7 episode/cluster/USEと数値閾値・解析式、8 invalid/stop/null/修正禁止、9 情報公開と監査署名、10 手順別owner GO と結果テンプレート。Bは**別方法版と別前登録**を作り、Aの最新版に追記しない。

### 根拠
事前登録は観測前に判断・除外・条件分岐を固定する必要がある。研究計画の公開/登録と秘密sourceの保管は異なる行為。外部レジストリを使える場合、OSFのread-only timestamp記録がGitHubと独立した保全になる（[OSF guidance](https://help.osf.io/article/330-welcome-to-registrations)、[COS preregistration](https://www.cos.io/initiatives/prereg)）。

### 棄却した代替案と理由
- **本回答をそのまま科学実行権限にする:** 数値閾値・custody・実装が未採択。
- **GitHub Draftの更新を凍結と呼ぶ:** Draftは変更可能である。
- **結果後に同じ前登録を書換える:** 事後性が追跡不能。

## QS8 本ラウンドの出口条件

### 推奨
**今提出するのは「QS1–QS8回答＋理由＋棄却案」「前登録章立て＋未決定decision log」「Museへの逆質問」の3点**であり、完成済み科学前登録・コード・source・hash・本採点ではない。MuseのP0/P1独立精査とOwnerの**設計判断**によってのみ次の前登録起草へ進む。現時点で科学実験許可なし。

**Owner決定表（いずれも未決定）：**

| Decision ID | 判断と候補 | 推奨 / 不許可時の扱い |
|---|---|---|
| OD1 | QS1: Aのみ / Bのみ / A→Bを別登録（c） / 研究STOP | **c条件付き**。Aの主張は費用・経路。Bは正当化不可ならSTOP |
| OD2 | 科学Aの目的: M_use陽性探索 / 費用・手続再現 / 紙上決着 | **費用・手続再現**。純粋科学の優先度が低ければA実行を省き紙上STOPしてよい |
| OD3 | source custodian: Owner / Muse / 独立第三者 | **Owner**、利益相反時は**別人**。独立秘密保管不能ならNO-GO |
| OD4 | closure: AはUNKNOWNでM_gap保留 / COMPLETE要求 | **UNKNOWNで限定実施**、ただし実route監査は必須 |
| OD5 | 実験規模: 12 law抽選×4 USE / 別のpower根拠付き規模 / STOP | **12を暫定案**。正式実施前に数値・power/母集団を凍結 |
| OD6 | F01/F11: 引続きNOT_EVALUATED / 別method後に実装 | **NOT_EVALUATED**。今は触らない |
| OD7 | 登録/凍結: main SHA＋独立保管 / main SHAのみ / 外部registry併用 | **可能なら外部registry併用**。GitHub単独なら限界明記 |
| OD8 | Bの環境制約: 非恣意的実環境証人あり / 証人なし / 新研究へ改題 | **証人ない限りB NO-GO** |
| OD9 | 実行権限: 設計案承認のみ / 前登録起草承認 / 科学実行GO | **前登録起草まで**、科学実行は別決定 |

**受入・出口:** ①Museが質問票8件へ内容面の査読（特に「Bは現行復元decoderの密かな消去ではないか」「12抽選が何の独立性か」「custodianが本当に独立か」を確認）、②OwnerがOD1〜OD9を承認/修正/STOPで記録、③後続の**前登録作成許可**のみ出す。未決事項が残れば本Draftは未採択として保存。

### 根拠
実証できないM_useを狙う前に方法的限界を宣言し、Ownerの費用・時間・主張の選択を保証する必要がある。

### 棄却した代替案と理由
- **今すぐ科学GO:** 独立source/外部seal/科学runner/事前費用閾値は未整備。
- **完成版のような偽凍結:** Owner/Muse判断と数値事前登録が未完了。
- **将来の表現修復全般を同じ一件で許可:** #146 WIP/方法v2の単一課題境界に反する。

---

## 追加精緻化：因果的寄与の層を分離した研究ロジック

研究を次の**別の可観測命題**に分ける。すべてを単一「賢くなった」で合算しない。

| 層 | 問うこと | 必要な証拠 | Aでの上限 |
|---|---|---|---|
| L0 可識別性 | F_affは公開4回答で一意か | GF(2)でrank=4・公開validator | 人間提供の既知族内識別 |
| L1 構成 | public-onlyからtyped body生成できるか | 漏洩なしtrace・独立validator | 工学実装の正当性 |
| L2 外部化 | 保存→fresh復元で同一意味か | immutable digest・別cwd・独立子process | 工学再現性 |
| L3 因果的使用 | 同一Snapshotでbodyだけ切ると予測/合法行動が違うか | D_use、全合法fallbackの同一性 | decoderがあるため原則NULL |
| L4 費用・償却 | 保持に総費用利益があるか | CPU/wall/bytes/計数・指定nと全生涯費用 | あり得るが未実測 |
| L5 実効表現拡張 | 現行H0_effectiveでは同資源不可能か | COMPLETE/最良OFFの証人 | UNKNOWN |
| L6 新概念・転移 | F_aff自体を獲得/異なる機構に再利用したか | 独立family試験・強い対照 | 対象外 |

**設計ロジックの帰結:** この有限問題では公開4bitがaffine係数の十分統計で、さらに固定16macroは完全な代替表現である。したがってBが合法でも、「永続化と事前計算のスケジュール上の価値」以上を示すことは困難。将来本当に狙うべき新規性は、**表現が足りないことを先に検出し、未知の関係・述語を公開介入から獲得し、異なる生成機構の未知世界へ転用する能力**である。ただしこれは既存の[#142](https://github.com/ryonakayama234/DekaSugi/issues/142)/[#168](https://github.com/ryonakayama234/DekaSugi/issues/168)の**別軸ポインタ**にとどめ、今は起動しない。

### Museへの再質問

同時提出する[Q-20261105-07-preregistration-review-to-muse.md](Q-20261105-07-preregistration-review-to-muse.md)で、監督者に対し本文の反証・別解・最小実行に関する**4問の設計質問**を提出する。これは合意の依頼であり、Museが回答・承認済みとの主張ではない。

### 科学的事前登録の外部基準（参考）

- [OSF Registrations / preregistration guidance](https://help.osf.io/article/330-welcome-to-registrations): 結果収集前の読み取り専用時刻付き研究計画、事前指定の分析・除外・条件分岐。
- [Center for Open Science — Preregistration](https://www.cos.io/initiatives/prereg): confirmatory/exploratoryの分離、予定した陰性を含む全分析の報告。
- 数値と因果解釈の根拠は外部文献の一般論ではなく、採用済み方法v2・main実装の特定の契約と、その代数的帰結に置いている。
