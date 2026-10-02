# 調査対象と移植判断

この文書はテンプレート上流の調査履歴です。今回のコンピューターで実施した調査・導入結果は[導入記録](adoption-status.md)を参照してください。以下の過去の実行結果を今回のpassへ転記しません。

調査日: 2026-09-30。調査対象は元repositoryの開発用入口・scripts・workflow・運用文書、およびこの実行環境で参照できた関連する個人設定/外部ハーネスです。製品コード全体の監査や個人会話履歴の探索ではありません。

元repositoryの調査開始HEADは `c178c6faa444886e92864318cde134368c403b79`。fetch後のdevelopは `5a51ef6fe3fc6411f93ac7f958619eeb1aafbb3c`、mainは `a1e841ccaeb113687d676536c2d13ae98fe77ef4`。今回参照した共通指示・Skills・運用scripts・workflowの対象群に開始HEADからdevelopまでの差分がないことを確認しました。移植元のrepository名/アカウント/Issue IDへの依存は持たせず、個別作業の対応は作成Issueに記録します。

## リポジトリ内

| 元の入口・根拠 | 観測した役割 | 移植判断・現在の入口 |
| --- | --- | --- |
| AGENTS symlink / CLAUDE | 共通制約、詳細への条件付き参照 | 共通AGENTSへ汎用化。CLAUDEを逆向きsymlinkにして正本1つ |
| `.agents/skills` / `.claude/skills` | start/finish、Issue/claim/worktree/PR/受入 | 両clientの発見経路を保持。重複本文はsymlink |
| `.cursor/rules` | 開発・GUI検証への入口 | 共通ruleとoperationsへ統合 |
| `.claude/settings.json` | Gradle等の実行許可、Context7許可 | 製品コマンドと広いallowlistを除外。導入先で選定 |
| architecture/knowledge | 用途別言語、正本、履歴/証拠 | context.mdへ汎用化 |
| GitHub workflow / work-management | 作業管理、所有、統合/完了 | workflow.md、GitHub setup |
| Codex execution policy | 特定modelの子agent禁止、独立sessionの区別 | clientの実制約を守る規約へ。固定model名は移植しない |
| `.githooks` / git_guard / bootstrap | branch/push保護、custom hooks保全 | 実行可能な共通ツールへ適合 |
| change_impact | 製品path→Gradle/Python/ZIP選択 | 専用品は除外。小さいharnessは全検証。拡張時の境界を説明 |
| CI / PR policy / Acceptance | tests、trusted base、PR/Issue/Case検証 | 共通CIを同梱。製品schemaのgateは同梱せず境界を文書化 |
| rulesets / CODEOWNERS | 実GitHub保護、担当 | 新repositoryで再設定。元ID/アカウントなし |
| agent_loop / agent_policy / agent_worker | coordinator、固定review、bounded fix | 汎用prompt/実行手順へ。専用engineと同等自動実行とはしない |
| handoff_registry | opaque公開recordとprivate source/host | 共通APIを保持。実registryは除外 |
| gui_lease | host/user排他、期限切れの所有保護 | 共通CLI。全project共通namespaceへ変更、旧leaseと調整必須 |
| verification / QA handoff / QA document | Case、双方向引継ぎ、候補受入 | workflowへ共通要件を保持。製品JSON/schemaは除外 |
| loop / human runbook / evidence | 再現→修正→独立review→実画面確認 | operationsとreview promptへ。製品試験課題は除外 |
| ACP / browser / memory / Swing fixtures | 製品通信・GUIの合成試験 | 製品依存。使い捨て/実観察との区別だけ共通化 |
| branch ZIP / compatibility / release candidate | 固定build、hash、配布、cleanup | 製品依存。信頼境界・成果物同一性の手順を保持 |
| governance audit | 全page読取、監査baseline/発火条件 | 既存監査状態を確認。共通監査観点だけ移植 |
| source relocation / private runtime | 既存worktree/ownerの移転・復旧 | 状態移行の注意として記載。実データをコピーしない |

## リポジトリ外

| 調査面 | 観測状態 | 再現方法/除外 |
| --- | --- | --- |
| CLI | Git 2.55.0、gh 2.101.0、Python 3.14.7、Node 26.10.0、npm 11.19.1、Codex 0.157.1、Claude Code 2.1.281、Cursor agent 2026.09.23-86fc751が実行可能 | 観測版であり推奨固定版ではない。公式導入→version記録 |
| 個人Codex AGENTS | 日本語応答・Android専門領域等 | 表現方針を共通化し、個人属性/技術前提を除外 |
| Codex config | model/reasoning、features、notify、MCP、Plugins、trust、project設定 | キーと関連項目を確認。全体コピー禁止 |
| 個人Codex Skills | harness-improve、instruction-audit、tune-agent-instructionsとsystem Skills | 関連原則を参照。個人全Skillsの配布はしない |
| Codex MCP | node_repl、context7、github、computer-useの設定 | Context7/GitHubは接続例。app管理serverはinstallerに任せる |
| Claude settings / project entry | 個人hooks、auto権限mode、Plugins、project trust。project固有MCPは空 | 個人mode/trustを継承せず、正規初期化 |
| Claude MCP | Context7 stdio、GitHub HTTP | 必要なserverを再登録。実認証成功とは分ける |
| Cursor CLI config | model、permissions、network、sandbox、履歴/cache等 | 全体を移植せず必要設定をUI/CLIで選定 |
| MCPファイル | 元projectの `.mcp.json` / `.cursor/mcp.json` と個人Cursor MCPファイルは不在 | 不在は他のUI管理接続がない証明ではない |
| Ponytail | 4.10.0 cache、3イベント定義、個人trust記録あり | 正規installと本人のtrust。trust記録だけで発火保証しない |
| Warp | Codex/Claude双方のplugin設定、Codex側trust記録 | 任意のterminal連携。cacheを配布しない |
| Vibe Island | Codex/Claude hooksがbridgeを参照、launcher実在 | 正規app導入と連携生成。通知表示は未試験 |
| app内蔵Plugins | app tools、Computer Use、browser/Chrome、visualize等 | 選択clientの正規導入。内部helper/REPLパスを除外 |
| 文書系・Swift LSP等 | 有効設定に存在 | 開発必須とはせず、用途がある場合だけ導入 |
| heartbeat | PR進行用1件、PAUSED。promptには旧子agent許可の記述も存在 | 停止維持。現規約と不一致の文面をコピーしない |
| `.git`配下runtime | agent-loopのprivate状態directoryが存在 | 件数/存在だけ確認。登録・owner・process・ログはコピーしない |
| host GUI lease | 保存directoryあり | 既存予約へ操作なし。templateテストは隔離directory |
| GitHub server | main/develop用active ruleset、Actions enabledをAPI確認 | new repoへID/設定を無断複製しない。個別readback |
| GUI/remote tool surface | 現セッションにbrowser/desktopと別host連携機能が提供 | 画面・remote実設定/実操作は未確認 |
| 管理設定/常駐候補 | 既知のCodex/Claude管理設定候補不在。関連名LaunchAgentの範囲を確認 | 全MDM/サービス/cronの不存在とは言わない |

## 意図的に採取しないもの・限界

token、認証ファイル、ブラウザーcookie、会話履歴、private wire、実行中registry、全環境変数は成果物に含めません。秘密候補を見つけても値を報告せず、種類と是正先だけ残します。

remote host、組織管理画面、未接続クライアント、全バックグラウンドサービス、過去の全Git履歴、配布artifact内容は網羅確認していません。設定あり・現在tool公開・実接続成功・新規導入smoke testを区別します。全個人サービスを探索することを「全ハーネス」の再現条件にせず、このprojectの確認可能な開発面を上表で追跡しています。

元コードにLICENSEファイルは確認できませんでした。本人の依頼による非公開での移植であり、外部利用者への再配布ライセンスを新たに推定・付与していません。公開や第三者配布の前に権利を確認してください。Ponytail等の第三者plugin本体はvendoringしていません。
