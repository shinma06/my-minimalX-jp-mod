# ハーネス導入記録

2026-10-02。ハーネス導入と、検証で見つかったXMLの整合性修正を実施した。

この導入記録内の旧配布名とhashは、改名前の作業に対応する履歴として保持する。現行プロジェクトは **VLC WMP Video Skin**、配布物は `VLC-WMP-Video.vlt`。過去のファイル名やhashを新しい候補の識別へ転用しない。repository内のIssue/PR等へのリンクは移行先URLを使う。

## 出典

- [agent-harness-template](https://github.com/shinma06/agent-harness-template/tree/e822318a6c0fa7175a89687b929197dfae879184): `e822318a6c0fa7175a89687b929197dfae879184`
- [cursor-in-android-studio](https://github.com/shinma06/cursor-in-android-studio/tree/a1e841ccaeb113687d676536c2d13ae98fe77ef4): `a1e841ccaeb113687d676536c2d13ae98fe77ef4`
- 導入前の当repository: `3c3cb11`。参照cloneはGit管理外の作業資料であり、設定・認証・実行中stateを移植していない。

## 導入内容

AGENTS、Claude/Cursor入口、start/finish Skills、Git guard、hooks bootstrap、doctor、GUI lease、検証・引継ぎ手順、CI、Issue/PRテンプレートを統合した。Windows launcher、GUI file lock、XML/asset/ZIP検査、再現可能な配布物生成、Case追跡とPR経路検査を追加した。

旧pre-commitの自動packageは維持し、未ステージsrcの混入とworktree名による配布名の変化を修正した。CLAUDE入口はWindowsで通常ファイルとして読める形とし、symlinkの文字列だけが残る問題を回避した。

新しい検査で、存在しない`files/segoeuil.ttf`の未使用Font宣言と、通常/全画面で重複する`bottom_resize_E`を検出した。未使用宣言を削除し全画面側のIDを分離した。実機への影響は未確認なのでGUI不要の変更として扱わない。

## このコンピューターでの検証

- Windows / Python 3.12.14で`./scripts/python.ps1 scripts/check.py`成功。初回14件中12件成功、POSIX専用の2件は対象外。Windowsのprivate registry拒否は別テストで成功。初期base移行と独立レビュー指摘の回帰試験を追加し、17件中15件成功、POSIX専用2件skipとなった。
- 使い捨てrepositoryでbootstrapの再実行、既存hook保全、mainへのcommit/push拒否、Issue branchでの自動package、未ステージsrc混在の拒否を確認した。
- XML・asset参照・生成ZIP内容、候補固定後のソース改変、Case不足・未合格・hash相違の拒否を確認した。
- 当repositoryの`core.hooksPath=.githooks`と`harness.python`を設定し、PowerShell launcherとdoctorから読戻した。
- 試験用成果物は`.harness-local/dist/My-MinimalX-JPMod.vlt`。SHA-256は`447af19d3dbe2894abaf599f877404d6be2f7803b8020dee968c79a2fec70615`。未commitの作業ソースからの試験buildであり、公開候補のSHAには対応付けていない。
- 独立レビューで、WindowsのZIP順序とpromotion側の再構成順序の相違、追跡配布物の検査漏れを検出した。修正commit `d75ee65780470347a4faf721134cac54d04febf6`ではUTF-8パス順を固定し、候補Git blobの実配布物をsrcと照合してそのhashを受入へ結び付けた。修正後のfresh/追跡/index/candidateは `e3568684cea2e241c8b27cb411299468fe2f3e7e0c6237a16ce46fcd344bd746` で一致した。packageのみの破損・欠落・旧内容も拒否する。

## 外部反映と残条件

- GitHub connectorから当初privateだったrepositoryへの接続を確認し、ユーザーの反映許可後に[導入Issue #1](https://github.com/shinma06/vlc-wmp-video-skin/issues/1)とdevelopを作成した。Issueにはtype/priority/status labelと所有claimを登録・読戻した。
- 当初はprivate repositoryのプラン制約でrulesets APIが403となったが、2026-10-02にユーザーがpublicへ変更して解消した。[main ruleset](https://github.com/shinma06/vlc-wmp-video-skin/rules/24364210)と[develop ruleset](https://github.com/shinma06/vlc-wmp-video-skin/rules/24364212)を適用し、GitHub APIで設定とbranchのeffective rulesを読戻した。両方activeで、PR必須、strictな`test` / `PR policy`、会話解決、force push/削除禁止、bypassなしを確認済み。
- [PR #2](https://github.com/shinma06/vlc-wmp-video-skin/pull/2)をdevelopへDraftで提出。`5de62d491db8ea9578fec2c3663f7b5273c90b23`の[CI run](https://github.com/shinma06/vlc-wmp-video-skin/actions/runs/37008548915)でWindows/Ubuntu、PR policy、testの成功を確認した。独立レビュー指摘の修正後も固定HEADの再レビューを必要とする。最新のレビュー・CI・統合状態はIssue/PRを正本とする。クライアント再起動後のSkills読込は未検証。
- 自動coordinator、`Agent review`サーバーgate、trusted coordinatorによる自動mergeは未導入。固定候補promotion検査は実装し、統合判断と別sessionレビューはPMが行う。参照元の完全自動運用とは区別する。
- WindowsのPOSIX private registryは明示拒否。GUI leaseとは別機能であり、手動引継ぎは利用できる。
- ユーザーの追加指示で一致対象を動画再生画面だけに限定した。Case定義をその範囲の10件へ更新し、すべてpendingとした。[QA Issue #3](https://github.com/shinma06/vlc-wmp-video-skin/issues/3)が担当と実機試験の正本。参照アプリの導入・準備画面の観察は進んだが、動画再生比較は未実施。詳細は[検証記録](verification/README.md)。

導入時の作業branchは `codex/1-agent-harness`、targetはdevelop。[PR #2](https://github.com/shinma06/vlc-wmp-video-skin/pull/2)は固定HEAD `04ceddf8e0141edaa571fe8a82c4c9229f136cd5` の独立レビュー後、developの `f1cbe3813d7c90d1816f22f355683cbb9b136919` へ統合された。GUIの全10件はpendingのままQA #3へ引き継いでいる。最新のCI・受入・統合状態はIssue/PRを正本とする。

## 動画再生画面プロジェクトへの移行

[Issue #4](https://github.com/shinma06/vlc-wmp-video-skin/issues/4)で、表示名をVLC WMP Video Skin、repositoryを `vlc-wmp-video-skin`、配布名を `VLC-WMP-Video.vlt` へ揃える。原作Maverick07x氏と日本語環境向け改変のrexent_gx氏の由来を残し、旧XMLとシアン固定化レビューを [legacy/minimalx](../legacy/minimalx/README.md) に原文のまま移す。ソースは引き続き `src/` を使用する。

GitHubの改名、remote更新、developを既定branchにする操作はPMによる読戻しの対象で、この文書の変更だけでは実施済みとしない。mainへの反映は固定候補の実機合格後に行う。原典の手順を追加の通知・定期実行の承認として扱わない。
