# Q-20261105-07 — Museへの科学事前登録設計の逆質問（独立精査依頼）

id: DIAG-Q-20261105-07-MUSE-REVIEW
status: questions_to_muse / draft / docs_only / no_approval / no_experiment / no_scoring / no_source_selection
updated: 2026-11-05
tags: gate-r2-m-science, muse-questionnaire, independent-review, preregistration, no-auto-go

> 提出者: Research Lead。回答書は [DIAG-R-20261105-06](R-20261105-06-science-preregistration-response.md)。発端は[DIAG-Q-20261105-06 / PR #179](https://github.com/ryonakayama234/DekaSugi/pull/179)。本書はMuseへの**設計上の逆質問**であり、承認・科学実行・源泉選定・法則抽選を開始しない。現行R2-M-ENG/method-v2と歴史的NULL/STOPは維持。

## 立場の提示（率直な反証を希望）

現行F00には合法 runtime affine decoder があり、Snapshot復元も公開履歴から係数復号・validatorを再実行する。F_affの4公開回答は4係数の十分統計であり、事前固定16macroなら全16法則をカバーできる。したがって「永続bodyによる新しい予測能力」については**現行Aが構造的NULL**であると考える。合法経路を削るだけのBによる陽性救済は採用しない。

この判断が誤りなら、反例と到達可能な具体的コード経路（復元・fallback・Snapshot情報の含有範囲を含む）を提示してほしい。

### MQ1：Aの科学的情報価値とSTOP判断

**問い:** 予測差ゼロが理論・実装の双方からほぼ導かれるAを、将来「独立source付き科学実験」として12 episode実行するのは妥当か、それとも先に**紙上NO-GO→限定費用ベンチ（非科学の工学）へ縮退**すべきか。

- 当方の推奨: Aの前登録は費用・経路・生涯償却のためにのみ意味を認める。ただし科学研究資源の節約を優先するなら**独立科学採点なしの紙上STOP**を有力代替とする。
- Museへの依頼: ①A science-GO（費用の独立再現性を重視）②engineering cost-only ③R2-M route STOP のいずれを支持するか、研究上の費用対効果と棄却理由を明示してほしい。
- STOP条件: 費用のn反復上限や公平な固定macro準備費を確定できない、又は科学的に新規の測定項目がない。

### MQ2：Bの非恣意的なuse-time制約を本当に作れるか

**問い:** 学習時の公開P+Q001、同一immutable Snapshotと全合法nonbody fallbackを保持したまま、Bで使う「USE時に再復号できない正当な環境」の実例を**1個でも**示せるか。現行restoreが復号すること、public4bitが保存されていること、STATIC-H+とFIXED-MACROが最適を達成することを考慮せよ。

- 当方の推奨: 本当に外部要件（締切・処理能力・通信切断）に根差した制約なら別policy/別登録の資源配分試験として検討。**単にdecoderをOFFだけから消す設計はINVALID**。同一USE制約をON・OFF双方へ適用し、復元処理・sufficient-statistic lookup・全macroにも同じ前登録規則を適用すること。
- Museへの依頼: ①有効な環境制約と同予算対照を示せる ②実際は永続化利得を費用に帰着できるのみ ③現有限F_affから撤退、のどれかと、最強の反論を示してほしい。
- STOP条件: OFFの合法経路の後出し除去、time-budgetとtrain-costを非対称に扱う、復元時再復号の隠蔽。

### MQ3：16法則の独立source・統計上の主張限界

**問い:** 既公開parity3例を封印の対象から除き、16法則しかない事前公開F_affで、12独立law抽選（4 private USE点×12）から具体的に何を推定できるか。**独立law抽選と独立生成familyの差**、lawに対応する公開4bit取得後のsource秘匿の実質的意味を査読してほしい。

- 当方の推奨: N_episode=12（暫定）、N_rep_family/T=NOT_EVALUATED。秘密は学習済み意味論ではなく**source target/seed・スコア・結果の後出し変更を防ぐ事前選定性**のために保管する。16候補を裸hashせず高エントロピーnonce付きcommit-then-revealとする。
- Museへの依頼: 無作為抽選 with/without replacement、既知target除外による母集団偏り、妥当な独立custodian、事前の定量閾値を含めて反証または修正してほしい。
- STOP条件: 秘密選定主体が学習結果を閲覧した後でlaw選択できる／抽選・nonceの事前証拠が残らない。

### MQ4：今の方法を捨てるべき基準／次の最小研究質問

**問い:** 機構M_useの研究が「人間提供F_affのデコードとキャッシュ」に吸収されるなら、DekaSugi本来の目標である「新しい行為の構造や述語を自力で発見する」ために、**一段階だけ増やすべき反証可能な仮説**は何か。

- 当方の作業仮説（**別研究ポインタ、今は起動しない**）: 固定H0では説明しきれない**公開介入による反例**から、新たな関係述語を生成→型付き実装として保存→異なる生成機構の世界へ再利用。そのとき、(a) static H+ all-macros、(b) policy-only、(c) episodic、(d) target-family hindsight/oracleとの明示比較が必要。
- Museへの依頼: この学習目標を本当に最小構成で検証する方法、**提案が初期メタ文法の組合せにすぎないことをどこまで許容するか**、反例となるNULL環境を1つ挙げてほしい。既存[#142](https://github.com/ryonakayama234/DekaSugi/issues/142)、[#168](https://github.com/ryonakayama234/DekaSugi/issues/168)を超える新Issue/実装のGOではない。
- STOP条件: 新規述語の外延が初期H0またはstatic H+で同予算再現可能、又は異なる生成機構への利益が再現しない。

## 合意形成の依頼形式

Museには**各MQについて「推奨／根拠（証明・反例）／棄却案／P0・P1・条件付き合格」を明記**してほしい。Research Leadは条件を受けて必要なら本PRに修正文書を追加し、Ownerが採否を判断する。**沈黙・PR作成・CI合格は合意でも承認でもない**。

最優先の合意点は「Bが単なるOFF弱体化にならないことを示せるか。示せなければ現在のF_aff路線を費用研究としてのみ扱い、M_use陽性を追わないこと」である。
