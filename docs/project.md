# プロジェクトの目的と実行コマンド

VLC media player の UI/UX を、Microsoft Store の [Windows メディア プレーヤー](https://apps.microsoft.com/detail/9wzdncrfj3pt?hl=ja-JP&gl=JP)（製品ID `9WZDNCRFJ3PT`）と一致させる。表示だけでなく、操作順序、状態遷移、フィードバック、キーボード操作を同じ実機・同じ素材で比較する。Windows Media Player Legacy は比較対象ではない。

現在の実装は VLC Skins2 の `src/theme.xml` と `src/files/`。Python 3.11以上の標準ライブラリで `.vlt` を生成する。スキンだけで目標を実現できるかは実機差分の調査対象。ライブラリ機能等の制約は先に記録し、観察なしに実現済みとしない。既存のシアン固定は現状の仕様であり、今後の一致目標より優先する要件ではない。

## 入口

- 作業開始・統合・終了: [開発フロー](workflow.md)
- 実機ケースと再開条件: [検証](verification/README.md)
- Windows のセットアップ: [ローカル環境](setup/windows.md)
- 移植元と導入結果: [導入記録](adoption-status.md)
- GitHub側に反映する設定: [GitHubセットアップ](setup/github.md)

## コマンド

PowerShellでは、bootstrap後に以下を使う。macOS/Linux/Git Bashでは `./scripts/python.ps1` を `bash scripts/python.sh` に置き換える。

```powershell
./scripts/python.ps1 scripts/doctor.py
./scripts/python.ps1 scripts/check.py
./scripts/python.ps1 build-vlt.py --output-dir .harness-local/dist
./scripts/python.ps1 scripts/verification.py validate
```

成果物名は `My-MinimalX-JPMod.vlt`。ZIP直下に `theme.xml` と `files/` が入り、worktree名に依存しない。同じソース・Python/zlib環境から同じバイト列を生成する。OS/Python/zlib版をまたぐhash一致は仮定せず、実際にVLCへロードしたファイルのSHA-256を記録する。

`scripts/check.py` は指示の相対リンク・設定構文・限定的な機密候補、回帰試験、XML/asset参照、生成ZIPの内容、Case構造を検査する。DTD全体の適合、VLCへのロード、UI/UX一致、外部サービス認証は別の受入である。

## ブランチと完了条件

通常の実装は `develop`、実機確認済みの固定候補は `main`。GUIに影響しない管理ツールは `main` へ直接PRを出せる。ローカル/リモートのbranch作成とGitHub保護の反映は別の操作で、[導入記録](adoption-status.md)に実状態を残す。

Issue番号を含む `codex/<番号>-<slug>` 等の専用branch/worktree、1 writer、固定HEAD/baseの別sessionレビューを使う。原典の製品固有engine・GitHub ID・過去承認をコピーしない。ユーザーの依頼は今回まずハーネス導入であり、UI全面改修の完了を意味しない。
