# GitHub側への反映

対象は`shinma06/my-minimalX-jp-mod`。ローカル導入とGitHub反映は別で、現状は[導入記録](../adoption-status.md)を参照する。原典のIssue番号・ruleset ID・過去承認を再利用しない。

## 反映順序

1. GitHub CLIまたは認証済みconnectorでrepository、visibility、既存Issue/PR、main/develop、rulesetsを読み戻す。認証値は表示・転記しない。
2. 導入Issueを登録しowner、scope、受入、GUI残条件をclaimする。現在のローカル変更を番号付き専用worktreeへ移す。`codex/harness-setup`の番号なしbranchではcommit/pushしない。
3. `develop`を確認済みmain SHAから作成し、導入PRをdevelopへ提出する。今回のXML修正はGUI対象なので、単純にmain toolingへ混ぜない。
4. 別sessionレビューと実CI `test` / `PR policy`を通し、developへの統合を確認する。GUIはCase正本とQA Issueに引き継ぐ。
5. 各required checkの実行実績を確認後、[develop設定案](../../.github/develop-ruleset.json)と[main設定案](../../.github/main-ruleset.json)を必要な権限で適用し、GET rulesetとbranchのeffective rulesを照合する。既存設定を盲目的に置換しない。
6. mainへの初回導入は、Case正本のない旧baseをどう移行するか独立レビューで確定してから行う。通常のpromotion検査を弱めて通さない。以後は[固定候補手順](../verification/README.md)を使う。

このrepositoryはprivateである。プランによりrulesetsが利用できない場合は未適用と記録し、ローカルguardをサーバー保護の代用として報告しない。

## 設定案

両branchともPR必須、strictな`test`と`PR policy`、会話解決、force push/削除禁止、bypassなし。developはsquash、mainはtoolingのsquashまたはpromotionのmerge commitを使う。GitHubユーザーが同一でも別sessionレビューを必須とするが、架空の`Agent review`checkをrequiredへ登録しない。

```powershell
gh api repos/shinma06/my-minimalX-jp-mod/rulesets
gh api repos/shinma06/my-minimalX-jp-mod/rules/branches/main
gh api repos/shinma06/my-minimalX-jp-mod/rules/branches/develop
```

CIはPRコードのテスト用の最小`contents: read`権限で動かし、checkoutに資格情報を残さない。artifactはCIでbuildしたSHAに対応する名前で保存する。独立レビューとlive Issue ownershipをCI内の自己申告に置き換えない。trusted coordinatorによる自動review/mergeは別途実装・検証が必要。

## Issue・Project・Milestone

Issue題名は`[機能]`、`[修正]`、`[調査]`、`[試験]`、`[運用]`、`[追跡]`から作業種別を選ぶ。typeはfeature/bug/research/qa/maintenance/tracking、priorityはP0/P1/P2、statusはready/in-progress/review/blocked/deferred/doneのlabelを使う。

Issueは具体作業、Projectは全体状況、Milestoneは到達目標。必要なものだけ作り、実際の親子・依存関係を登録して読み戻す。分類のためだけに親を捏造しない。初期の受入候補は環境識別、スキン機能限界の調査、Case別差分修正、固定候補QAの順。
