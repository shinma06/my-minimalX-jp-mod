# Windows メディア プレーヤーとの実機比較

正本は [cases.json](cases.json)。2026-10-02のユーザーの追加指示に従い、比較対象は**動画再生中の画面と、その画面で使うUI/UXのみ**とする。ホーム、音楽/動画ライブラリ、アプリ全体のナビゲーションは再現対象から外した。Case定義を動画専用の全10件へ更新し、未実施の結果はpendingに戻した。これはユーザー指定による受入変更であり、範囲外の操作を合格扱いしたものではない。

Computer Useで両アプリを同じ環境・同じ動画fixtureで操作する。参照側の動画画面にある操作を観察してから期待値を具体化し、見た目だけでUX一致を認定しない。まず通常の動画画面を固定し、再生・シーク・音量、字幕/音声・速度、全画面/自動非表示、キー操作の順に差分を小さな修正Issueへ分ける。

1. 実在IssueとGUI ownerを決め、共通leaseを取得する。
2. Windows、表示倍率、ウィンドウの寸法、言語、テーマ、参照アプリ版、VLC版を記録する。
3. 個人の音楽/動画ではなく、共有可能な固定fixtureを用意しSHA-256を記録する。
4. 候補のfull source SHAに追跡された `VLC-WMP-Video.vlt` をロードし、その配布物のSHA-256を記録する。dirtyなsourceや別環境で再生成した異なるhashのファイルを既存候補の配布物と扱わない。
5. 両アプリで同じ初期状態・順序の操作を行い、画面・動作・観察結果をCase別に保存する。私的データを含む画面は公開しない。
6. 差分が残ればfail、操作環境の障害ならblocked、未実施ならpending。passには証拠参照、版、環境、fixture、候補SHA、配布物hash、差分なしが必要。

```powershell
./scripts/python.ps1 scripts/verification.py validate
# 実機比較後の固定候補受入。未実施のCaseが1件でもあれば失敗する。
./scripts/python.ps1 scripts/verification.py accept --candidate FULL_SHA --artifact VLC-WMP-Video.vlt
```

schema検査は証拠の真偽や画面の一致を自動判定しない。独立レビュアーが実際の証拠とbuildを照合する。caseの削除・期待値の緩和は受入変更としてレビューする。

## mainへの固定候補

mainをdevelopへ同期後、対象develop SHAとmain SHAを固定し、候補に含まれる全commit・Case・配布物hashを記録する。

```powershell
./scripts/python.ps1 scripts/promotion.py --candidate FULL_DEVELOP_SHA --base FULL_MAIN_SHA
```

候補以降の差分は`cases.json`の結果と`promotion.json`だけにする。`Integration: promotion`のPRでpolicyが候補の祖先関係、mainの移動、Case定義変更・不足、配布物hashの相違、未合格Caseを拒否する。候補の配布物とsrcをGit blobとして読み、ZIPの全収録パス・内容を照合したうえで、配布物そのもののSHA-256を固定する。配布物の欠落・破損・不一致は拒否し、PR内のビルドscriptをこの判定のために実行しない。圧縮率・収録順・日時などが異なる同内容のZIPでもhashは別になるため、実機へは固定した候補の配布物をロードする。

初回の旧main `3c3cb11b9d290351b72be8bdb06549d24cddd4aa` にはCase正本がないため、この確認済みSHAに限りUI-001〜UI-010の全10件を既存の必須Caseとして扱う。GUI合格、候補固定、hash、全commit、独立レビューは省略しない。それ以外のbaseで台帳が欠落していれば拒否する。[GitHubセットアップ](../setup/github.md)を参照。

名称移行後の候補は `VLC-WMP-Video.vlt` を追跡する。旧mainが持つ配布物や導入記録の旧hashを、候補の配布物の代わりに使わない。名称やGitHub既定branchの変更は、初回promotionの全10件の合格条件を変更しない。

## 観察と再開条件（2026-10-02）

初回はStoreウィンドウの取得で失敗した。その後、ユーザーの明示許可でMicrosoft署名を確認した公式インストーラーを起動し、参照アプリ11.2607.16.0とVLC3.0.23を識別した。参照のホーム、音楽ライブラリの空状態、Ctrl+Oのファイル選択をComputer Useで観察したが、これらは動画画面の合格証拠ではない。

参照アプリは登録ID `Microsoft.ZuneMusic_8wekyb3d8bbwe!Microsoft.ZuneMusic` で再表示するとスクリーンショットを取得できた。アクセシビリティ情報はnullだった。GUI操作はEscによる停止通知で中断し、共通leaseを解放した。動画fixtureの入力・再生、VLCへの候補スキンのロード、動画画面の比較は未実施。

個人データを含まない640×360/30fps・12秒の無音テスト動画を用意した。SHA-256は `a93372f49d74e4de981f85f10dd411e265bd4731112fc89ee08f1a7f39282c1d`。素材と準備段階の画面はGit管理外で保持し、字幕/複数音声用fixtureは別途用意する。表示倍率・同一ウィンドウ寸法も動画試験時に確定する。

次のGUI担当は、操作再開後に現在のウィンドウ状態を取り直し、修正後の固定candidate・追跡配布物・fixtureのhashを記録してUI-001から開始する。古い準備用buildやホーム画面の観察を動画画面の合格に流用しない。[QA Issue #3](https://github.com/shinma06/vlc-wmp-video-skin/issues/3)が担当と再開状態の正本。
