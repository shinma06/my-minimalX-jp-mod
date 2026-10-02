# Issueから実機検証・統合まで

参照元は [cursor-in-android-studio の開発フロー](https://github.com/shinma06/cursor-in-android-studio/blob/a1e841ccaeb113687d676536c2d13ae98fe77ef4/docs/development/github-workflow.md)。目的に関係する所有・検証・二段階統合を採用し、Android/Gradle/ACP固有処理は移植しない。

## 開始

1. Issue、コメント、関連PR、既存claim、worktree、dirty状態と依存を確認する。
2. 重複がなければ具体的な目的・受入・次操作を持つIssueを登録する。実在するProject/Milestoneだけ関連付ける。labelは `type:*`、`priority:P0|P1|P2`、`status:*` を各1個とする。
3. owner、scope、base SHA、target、レビュー担当、GUI要否、Case ID、次操作をclaimし読み戻す。未解放claimは時間だけで失効しない。
4. 通常は `origin/develop`、GUI不要の管理ツールは `origin/main` から `codex/<Issue>-<slug>` と専用worktreeを作る。継承された統合先upstreamを解除する。
5. `scripts/bootstrap.py` を実行する。最初の意味あるpushでDraft PRを作成し、[PRテンプレート](../.github/pull_request_template.md)を埋める。

Issue/PR公開やアカウント変更は実際のユーザー指示・クライアント権限に従う。外部通信の承認がまだない場合はローカルにレビュー可能な変更と依頼文を用意し、登録・公開待ちと記録する。Issue番号は捏造しない。初回導入の未公開変更は `codex/harness-setup` に保管できるが、このbranchでのcommit/pushをguardは許可しない。登録済みIssueの専用worktreeに移して通常経路へ乗せる。

## 実装・検証

必要なソース、参照、テストを読んでから変更する。`scripts/check.py` を実行し、GUI変更は [Case JSON](verification/cases.json) に初期状態・操作・期待・観察を記録する。skin XMLと配布物の変更はGUI必須。

コミット時はguardの後で、ステージされたsrc/build変更に対して配布物を再生成する。build入力には `build-vlt.py` と配布名の正本 `scripts/validate_skin.py` を含む。未ステージのsrc/buildや未追跡assetがある場合は止め、意図しない変更を配布物へ混ぜない。配布物だけの変更も、ステージされたGit blobの全収録パス・内容を同じindexのsrcと照合し、欠落・破損・不一致を拒否する。push前はmain/master/develop、別branch、dirty、非fast-forwardを拒否し、共通検証を実行する。

## 二段階統合

- **develop / implementation**: テスト、別sessionのコードレビュー、全Caseの追跡を必要とする。GUIのpending/blocked/failはそのまま記録し、QAへ引き継げる。`Refs #N` を使い、PR本文で自動closeしない。
- **main / tooling**: docs/scripts/tests/CI/agent入口のみの差分。GUI不要の具体的理由、CLI検証、別sessionレビューが必要。srcや`.vlt`は含めない。
- **main / promotion**: 固定候補SHA・配布物hashの全Caseがpassであることを実機証拠と照合し、全対象commit、最新CI、別sessionレビューを確認する。developからの履歴を保つmerge commitで反映する。

develop統合後は未確認項目をQA Issueに移し、元Issueと双方向リンクを読み戻す。実装受入が満たされた範囲だけ完了とし、親・QA・main反映までまとめて完了扱いにしない。GUI差分は修正Issueへ分離して再確認する。

## レビューと自動進行

レビュー担当はwriterと別sessionで、固定HEAD/base・受入・検証結果を確認する。同一sessionの自己点検やテスト成功で独立レビューを代替しない。[レビュー依頼文](../prompts/review.md)を使う。session生成はこの文書だけでは許可されない。

テンプレートのcoordinatorは[手順と依頼文](setup/automation.md)であり、元製品の常駐engineではない。今回のCIは `test` と `PR policy`。promotionでは全候補commit・base・Case定義・配布物hashを照合する。`Agent review` の自動承認は実装していないため、PMが別sessionレビューの実証拠を確認してから通常の保護付きPR経路で統合する。guard/required checkを無効化しない。

CIは権限を絞ったPRテストとして動き、PRに含まれるscript自体を信頼できる承認者とは扱わない。現在のbaseで確認済みのpolicyを使う追加検証と、gateへの変更の独立レビューをPMが行う。参照元のtrusted coordinatorによる完全自動mergeとは区別する。

## 中断・終了

owner、scope、HEAD/base、branch/target、PR、dirty、検証、未解決Case、次の担当・操作を記録する。WindowsではPOSIX private registryを使わず、公開可能な引継ぎと非公開ローカルパスの対応を分離する。writer停止とclaim解放/再割当を確認してから再開する。

merge、Issue完了、GUI合格、配布、cleanupをそれぞれ確認する。自分の停止済み・cleanなbranch/worktreeだけ整理し、main/developや他担当の資源を削除しない。残す資源は担当と再開条件を記録する。
