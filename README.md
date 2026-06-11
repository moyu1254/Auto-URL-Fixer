# Auto URL Fixer

クリップボードにコピーされた URL を監視し、Discord などで展開しやすい fixer 系 URL に自動変換する小さなツールです。

## 概要

- クリップボード内のテキストから URL を検出
- 対応サービスのホスト名だけを変換
- 複数 URL を含むテキストにも対応
- Python を別途インストールしなくても `.exe` 配布で利用可能
- ターミナルを表示せずにバックグラウンド起動可能
- 停止用バッチとスタートアップ登録用バッチを同梱
- 変換ルールは `config.example.json` をもとにカスタマイズ可能

## クイックスタート

通常利用では Python は不要です。配布フォルダ内の `Auto URL Fixer.exe` と同梱スクリプトをそのまま使えます。

配布版をバックグラウンド起動する場合:

`start_auto_url_fixer.vbs` をダブルクリックしてください。

開発中に Python で直接起動する場合:

```powershell
py -m auto_url_fixer
```

起動後、たとえば次の URL をコピーすると、

```text
https://twitter.com/example/status/123
```

クリップボード内容が次のように置き換わります。

```text
https://fxtwitter.com/example/status/123
```

停止方法:

- ターミナル起動中は `Ctrl+C`
- バックグラウンド起動中は `stop_auto_url_fixer.bat`

## 同梱ファイル

- `start_auto_url_fixer.vbs`: ターミナルを表示せずに起動
- `start_auto_url_fixer.bat`: 上記 VBS ランチャーを呼び出す補助バッチ
- `stop_auto_url_fixer.bat`: 実行中の Auto URL Fixer を停止
- `enable_startup_auto_url_fixer.bat`: Windows ログイン時の自動起動を有効化
- `disable_startup_auto_url_fixer.bat`: スタートアップ登録を解除
- `Auto URL Fixer.exe`: Python 不要で実行できる Windows 配布用実行ファイル
- `config.example.json`: 設定ファイルのサンプル

## 設定ファイル

まずサンプル設定をコピーします。

```powershell
Copy-Item config.example.json config.json
```

設定を指定して起動します。

```powershell
py -m auto_url_fixer --config config.json
```

設定例:

```json
{
  "name": "X / Twitter to FxTwitter",
  "enabled": true,
  "hosts": ["twitter.com", "www.twitter.com", "mobile.twitter.com"],
  "target_host": "fxtwitter.com"
}
```

`enabled` を `false` にすると、そのルールは使われません。

主な設定項目:

- `poll_interval_seconds`: クリップボード監視間隔
- `log_rewrites`: 変換内容をログ出力するかどうか
- `rules`: 変換ルール一覧

## 既定で有効な変換

| 対象 | 変換例 |
| --- | --- |
| X / Twitter | `twitter.com` -> `fxtwitter.com`, `x.com` -> `fixupx.com` |
| pixiv | `pixiv.net` -> `phixiv.net` |
| Instagram | `instagram.com` -> `ddinstagram.com` |
| TikTok | `tiktok.com` -> `tnktok.com` |
| Reddit | `reddit.com` -> `rxddit.com` |
| Tumblr | `tumblr.com` -> `tpmblr.com` |
| Bluesky | `bsky.app` -> `fxbsky.app` |

追加候補として `tfxktok.com`, `tiktokez.com`, `rxyddit.com`, `instagramez.com`, `fixthreads.net`, `fxtwitch.tv` などのルールも `config.example.json` に含めていますが、初期状態では `enabled: false` にしています。

## 停止とスタートアップ

- `stop_auto_url_fixer.bat` は、まず停止要求を送り、その後 `Auto URL Fixer.exe` または `auto_url_fixer` を実行中のプロセスを探して停止します。
- PID ファイルが無い古い起動でも停止できるようにしています。
- `enable_startup_auto_url_fixer.bat` を実行すると、Windows の Startup フォルダに起動用バッチを作成します。
- `disable_startup_auto_url_fixer.bat` を実行すると、そのスタートアップ登録を削除します。

## 配布用ビルド

開発者向けに、Windows 配布用 `.exe` を作るバッチを同梱しています。

```powershell
build_windows_exe.bat
```

成功すると `dist\Auto URL Fixer\` に次の配布セットを出力します。

- `Auto URL Fixer.exe`
- 起動 / 停止 / スタートアップ操作用の `.bat` / `.vbs` / `.ps1`
- `config.example.json`
- `README.md`

## テスト

```powershell
py -m unittest discover -s tests
```

## 補足

- すでに別の Auto URL Fixer が動いている場合、新しい起動は多重起動を避けるため失敗します。
- バックグラウンド起動時は標準出力が見えないため、必要ならターミナル起動で動作確認してください。
- `start_auto_url_fixer.vbs` は `Auto URL Fixer.exe` を最優先で起動し、見つからない場合だけ開発用に Python 実行へフォールバックします。
