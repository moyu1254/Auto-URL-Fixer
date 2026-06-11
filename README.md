# Auto URL Fixer

クリップボードにコピーされた URL を監視し、Discord などで展開しやすい fixer 系 URL に自動変換する小さなツールです。

## 概要

- クリップボード内のテキストから URL を検出
- 対応サービスのホスト名だけを変換
- 複数 URL を含むテキストにも対応
- Python を別途インストールしなくても `.exe` 配布で利用可能
- 起動 / 停止 / スタートアップ ON / OFF をターミナル表示なしで実行可能
- `Auto URL Fixer.exe` を中心に運用可能
- 変換ルールは `config.example.json` をもとにカスタマイズ可能

## クイックスタート

通常利用では Python は不要です。配布フォルダ内の `Auto URL Fixer.exe` と同梱の `vbs` ランチャーをそのまま使えます。

配布版をバックグラウンド起動する場合:

`start_auto_url_fixer.vbs` をダブルクリックしてください。

停止する場合:

`stop_auto_url_fixer.vbs` をダブルクリックしてください。

スタートアップを有効化する場合:

`enable_startup_auto_url_fixer.vbs` をダブルクリックしてください。

スタートアップを無効化する場合:

`disable_startup_auto_url_fixer.vbs` をダブルクリックしてください。

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
- バックグラウンド起動中は `stop_auto_url_fixer.vbs`

## 同梱ファイル

- `Auto URL Fixer.exe`: Python 不要で実行できる Windows 配布用実行ファイル
- `start_auto_url_fixer.vbs`: ターミナルを表示せずに起動
- `stop_auto_url_fixer.vbs`: ターミナルを表示せずに停止
- `enable_startup_auto_url_fixer.vbs`: ターミナルを表示せずにスタートアップ登録
- `disable_startup_auto_url_fixer.vbs`: ターミナルを表示せずにスタートアップ解除
- `config.example.json`: 設定ファイルのサンプル

補助的に `.bat` / `.ps1` も同梱していますが、通常は `exe` と `vbs` 側を使えば十分です。

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

- `Auto URL Fixer.exe --stop` で停止、`--enable-startup` でスタートアップ有効化、`--disable-startup` で解除できます。
- 同梱の各 `vbs` ファイルは、これらの引数付き `exe` 実行をターミナル非表示で呼び出すためのランチャーです。
- `stop_auto_url_fixer.vbs` は、まず停止要求を送り、その後 `Auto URL Fixer.exe` または `auto_url_fixer` を実行中のプロセスを探して停止します。
- PID ファイルが無い古い起動でも停止できるようにしています。
- スタートアップ有効化時は、Windows の Startup フォルダに非表示起動用の `vbs` エントリを作成します。

## 配布用ビルド

開発者向けに、Windows 配布用 `.exe` を作るバッチを同梱しています。

```powershell
build_windows_exe.bat
```

成功すると `dist\Auto URL Fixer\` に次の配布セットを出力します。

- `Auto URL Fixer.exe`
- 起動 / 停止 / スタートアップ操作用の `.vbs` / `.bat` / `.ps1`
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
- 配布用 `Auto URL Fixer.exe` は `console=False` でビルドするため、直接実行してもターミナルは表示されません。
