# Windowsでの利用

Git for WindowsとPython 3.11以上を使用する。追加Pythonパッケージは不要。PowerShellとGit BashのPATHが異なっても、bootstrapが実行中のPythonを当該repositoryの `harness.python` に保存し、両方のlauncherが参照する。絶対パスはGit管理するファイルには保存しない。

```powershell
# 初回だけ、利用するPythonで実行する。
python scripts/bootstrap.py
# pythonがPATHにない場合は手元のPython実行ファイルの絶対パスで同じscriptを実行する。
./scripts/python.ps1 scripts/doctor.py
./scripts/python.ps1 scripts/check.py
./scripts/python.ps1 build-vlt.py --output-dir .harness-local/dist
```

Git Bashでは `bash scripts/python.sh scripts/check.py`。runtimeを移した場合は新しいPythonでbootstrapを再実行する。`HARNESS_PYTHON` でそのセッションだけ指定することもできる。bootstrapは他のcustom hooksを検出した場合に上書きせず終了する。旧`install-hooks.sh`も同じbootstrapへの入口。

## Computer Use

操作の直前にGUI担当とhost/user共通leaseを確認する。Windowsでは`msvcrt`のfile lock、macOS/Linuxでは`flock`を使用する。既定のstateはOSの一時directory内のuser別namespaceで、repositoryごとには分けない。Windowsのstateはuser用一時領域の既存ACLを継承する。secret storeの代用ではなく、同一ユーザーの悪意あるprocessを防ぐ境界でもない。

```powershell
./scripts/python.ps1 scripts/gui_lease.py status
```

取得には実在Issue、owner、run、full source SHAが必要。tokenは共有ログへ貼らない。期限が切れても所有権を自動移譲しない。WSLから同じデスクトップを操作する場合は別のleaseを並立させず、担当を一本化する。

## Windowsで利用しないPOSIX機能

`handoff_registry.py`のprivate registryはPOSIXの所有者・0700/0600・dir_fd検査を要求する。Windowsのchmodで同じ保証を装わず、明確なエラーで拒否する。Windowsでの引継ぎは[workflow](../workflow.md)の公開記録とprivateなローカル対応記録を使う。自動coordinatorのopaque registry連携は未対応である。

## 別途の接続

GitHub CLI/connectorの認証、Issues/PR書込み権限、rulesets、独立レビューの実行経路、参照アプリの起動・画面取得はdoctorのファイル検出とは別に確認する。テンプレートを配置しただけで外部設定済みとは判断しない。
