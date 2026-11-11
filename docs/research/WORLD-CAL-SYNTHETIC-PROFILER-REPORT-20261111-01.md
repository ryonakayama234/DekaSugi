# WORLD CAL — 合成 fixture 専用コンポーネント profiler 実測報告

id: WORLD-CAL-SYNTHETIC-PROFILER-REPORT-20261111-01
status: IMPLEMENTATION_GO_ONLY / COMPONENT_PROFILE_COMPLETED / FULL_FEASIBILITY_STOP_UNKNOWN / NOT_CAL_AUTHORIZED
updated: 2026-11-11
tags: world-expansion, cal-implementation, synthetic-profiler, research-lead, no-cal, cpu-feasibility

## 1. 権限、対象、証跡

本報告は Owner の **実装 GO** と PR #205 の監督者 [AGREE](https://github.com/ryonakayama234/DekaSugi/pull/205#issuecomment-6794011459) に基づく、合成 fixture **コンポーネント単体の小規模計測**のみである。CAL 実施、L90 実測、ID-only 実診断、費用ベクトルの CAL 計測、K0 本実行、power simulation 本実行（反復削減した「試走」も含む）、sealed split 実体化、seed 値生成、holdout instance/target/score 生成、正式 EVAL は行っていない。

- **計測コード**: `scripts/profile_world_cal_synthetic.py`、実装候補 `world_cal/{prf,gtheta,sampford,inference}.py`。
- **実測 CI**: [WORLD CAL synthetic-only run 43013021519](https://github.com/ryonakayama234/DekaSugi/actions/runs/43013021519)（**success**）。同 run の `world-cal-synthetic-component-profiler` artifact に機械可読 JSON と algorithm-source-manifest 候補を保存。
- **テスト**: 同 CI で独立した合成 golden／権限遮断／再現性／公開 Ed25519 検証ベクトルを実施。success は完成判定・監督者 PASS の代替ではない。
- **環境**: GitHub Actions `ubuntu-24.04`、Linux `7.0.0-1017-azure-x86_64`、x86_64／glibc 2.39、CPython 3.12.16、報告環境での `os.cpu_count()=4`。この数はベンチマークが4コアを並列占有したことを意味しない。
- **計時**: `time.perf_counter()` wall、`time.process_time()` CPU、`resource.getrusage(RUSAGE_SELF).ru_maxrss` プロセス RSS 高水位。RSS はプロセス全体の**累積最大**であり段階の差分ではない。小規模単発値にはばらつきがあり、不確かさの統計的 CI は未算出。

## 2. 段階別実測（小規模、合成 fixture のみ）

| component | 単体 fixture 量 | wall (秒) | CPU (秒) | throughput (fixture item/秒) | RSS 高水位 KiB |
|---|---:|---:|---:|---:|---:|
| HMAC PRF＋Gθ 二値判定の部分カーネル | 13,824 outcomes相当 | 0.077178 | 0.077174 | 179,118 | 18,708 |
| Sampford 小規模厳密全列挙＋二次包含 | N=8,n=2、64 N²項 | 0.000707 | 0.000709 | 90,533 N²項 | 18,708 |
| Sampford 二次包含 DP 候補 | N=32,n=8、1,024 N²項 | 0.004022 | 0.004024 | 254,585 N²項 | 18,836 |
| Sampford 二次包含 DP 候補 | N=64,n=16、4,096 N²項 | 0.029408 | 0.029411 | 139,281 N²項 | 18,964 |
| 親 cluster bootstrap＋7比較 max-T の部分カーネル | 48 resamples | 0.000578 | 0.000580 | 83,045 resamples | 18,964 |
| 合成ローカル I/O | 73,728 bytes | 0.000795 | 0.000797 | 92.72 MB/s (decimal) | 18,964 |

注記:

1. PRF/Gθ 部分カーネルは公開 RFC4231 HMAC テスト鍵と人工的な固定因子だけを用いる。**6因子 Gaussian のスコープ別生成、AR(1) 全時系列、law と cluster の共有 draw、全フロー結合は未計測**。1 outcome 相当の処理を本番生成コストと等置してはならない。
2. Sampford の N32/N64 は代数的 exact `π_ll'` **候補**の小規模計測。小 N では独立全標本列挙と突合したが、N=336／実 q／certainty を含む数値安定性・計算量・実際の PPS と一致することは監督者未監査であり、全実規模で PASS と認定しない。
3. bootstrap は親重み付き HT と小さな7次元 max-T のカーネル計測であり、実設計での per-law 999回 bootstrap、G1/G2片側区間、10ゲート統合の完全な工程を含まない。I/O もメモリ上の短い合成ブロックのファイル read/write に限る。

## 3. protocol の反復数を**変更せず**に行った算術外挿

規範上の全走査ケースを仮定した算術: `MC_R=10000`、全 `n=2..N` 昇順、3シナリオ、各反復 `576n` 二値 outcome、各反復999 bootstrap。以下は**実行済み反復や所要時間の保証ではない**。

| 全走査の仮定 | 候補 n 数 | MC の理論反復 | 二値 outcome 理論個数 | bootstrap の理論複製数 | PRF/Gθ 部分カーネル単純外挿 | bootstrap 部分カーネル単純外挿 |
|---|---:|---:|---:|---:|---:|---:|
| `n=2..336` | 335 | 10,050,000 | 978,307,200,000 | 10,039,950,000 | **約63.2 wall日** | **約1.40 wall日** |
| `n=2..512` | 511 | 15,330,000 | 2,269,330,560,000 | 15,314,670,000 | **約146.6 wall日** | **約2.13 wall日** |

これらは各カーネル throughput を単純に乗算・除算した**非常に楽観的な個別下界目安**であり、和を完全な所要見積として扱えない。初回成功 run の同一 PRF 部分カーネルは約228,679 outcome/s、後続 run は約179,118 outcome/s と変動している。PRF 完全生成、Sampford real-scale `π_ll'`、conditional draw、Gaussian/covariance 構築、999 resample での law 寄与、max-T, I/O, 保存・監査・並列環境を含めた現実的な CPU/wall/RSS は **算出不能（STOP_UNKNOWN）**。

算術の `N=336` は公開 parent quota からの設計個数に過ぎず、実 holdout allocation を生成／閲覧したものではない。最初の採択 n で停止する可能性はあるが、規範を変えずには事前に停止 n を保証できない。

## 4. 専門監査への結論と判断事項

- **G-COMPUTE = STOP_UNKNOWN**。calls upper bound `C(336)=4,944,976 < cost_cap=20,000,000` だけでは CPU feasibility を証明できない。
- 実測は小規模の合成 stage だけで、全段を統合した現実的 throughput・CPU・wall・RSS の再現可能な性能モデルは未完成。後続独立監査は、`N=336` 固定設計での Sampford inclusion 計算精度、realistic law/cluster input の計測可能性、段階間連携、キャッシュ方針、CPU とメモリ上限を要求すべきである。**simulation を「小さく回して確かめる」ことは認めない。**
- 現時点の監督者に提出可能なのは、機械可読 profiler と算術に裏付けられた**不確定な feasibility リスク**まで。計算予算が不足する場合はプロトコル版の改訂→再審査→Owner の別承認が必要であり、本 PR は勝手に反復数・閾値・n 走査を変更しない。

**権限状態**: `IMPLEMENTATION_GO=true`、`CAL_AUTHORIZED=false`、`CAL_EXECUTED=false`、`POWER_SIMULATION_EXECUTED=false`、`K0_EXECUTED=false`、`SPLIT_MATERIALIZED=false`、`FROZEN=false`。
