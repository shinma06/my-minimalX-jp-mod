# プロジェクトの目的と実行コマンド

VLC media player の**動画再生中の画面と、その画面で使うUI/UXのみ**を、Microsoft Store の [Windows メディア プレーヤー](https://apps.microsoft.com/detail/9wzdncrfj3pt?hl=ja-JP&gl=JP)（製品ID `9WZDNCRFJ3PT`）と一致させる。2026-10-02のユーザーの追加指示に基づく範囲である。表示だけでなく、動画の再生・シーク・音量・字幕/音声・速度・全画面・メニュー・キーボード操作を同じ実機・同じ素材で比較する。ホーム、音楽/動画ライブラリ、アプリ全体のナビゲーションは再現対象に含めない。Windows Media Player Legacy は比較対象ではない。

現在の実装は VLC Skins2 の `src/theme.xml` と `src/files/`。Python 3.11以上の標準ライブラリで `.vlt` を生成する。既存の動画表示・操作部品を活用し、観察した差分から小さく修正する。秒数スキップ、音量範囲、通常画面での自動非表示、フォーカス遷移等はSkins2の実現範囲と照合し、観察なしに実現済みとしない。動画画面に必要な要件が満たせないと確認するまで全面再実装を前提にしない。既存のシアン固定は現状の仕様であり、今後の一致目標より優先する要件ではない。

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

成果物名は `My-MinimalX-JPMod.vlt`。ZIP直下に `theme.xml` と `files/` が入り、worktree名に依存しない。収録順は相対パスのUTF-8バイト順に固定し、同じソース・Python/zlib環境から同じバイト列を生成する。Python/zlib版をまたぐhash一致は仮定しない。検証では保存またはDeflate形式のZIPを許容し、全収録パス・内容とソースの一致を必須にする。実機では候補コミットに追跡された配布物をロードし、そのファイルのSHA-256を記録する。

`scripts/check.py` は指示の相対リンク・設定構文・限定的な機密候補、回帰試験、XML/asset参照、追跡済み配布物と新規生成ZIPの内容、Case構造を検査する。DTD全体の適合、VLCへのロード、UI/UX一致、外部サービス認証は別の受入である。

## ブランチと完了条件

通常の実装は `develop`、実機確認済みの固定候補は `main`。GUIに影響しない管理ツールは `main` へ直接PRを出せる。ローカル/リモートのbranch作成とGitHub保護の反映は別の操作で、[導入記録](adoption-status.md)に実状態を残す。

Issue番号を含む `codex/<番号>-<slug>` 等の専用branch/worktree、1 writer、固定HEAD/baseの別sessionレビューを使う。原典の製品固有engine・GitHub ID・過去承認をコピーしない。管理基盤の導入、動画画面の実装、実機合格、main反映を別々に確認する。PMはユーザーの許可に基づき担当を割り振るが、同じデスクトップのGUI担当は同時に1名とする。
