# Auto URL Fixer

クリップボードにコピーされた URL を監視し、Discord などで展開しやすい fixer 系 URL に自動変換する小さなツールです。

## 概要

- クリップボード内のテキストから URL を検出
- 対応サービスのホスト名だけを変換
- 複数 URL を含むテキストにも対応
- Python を別途インストールしなくても `.exe` 配布で利用可能
- `Auto URL Fixer.exe` だけで起動 / 停止 / スタートアップ ON / OFF を操作可能
- 監視本体はターミナルを表示せずにバックグラウンド実行
- 変換ルールは `config.example.json` をもとにカスタマイズ可能

## クイックスタート

通常利用では Python は不要です。配布フォルダ内の `Auto URL Fixer.exe` を開くと操作パネルが表示されます。

操作パネルから次の操作ができます。

- `Start`: クリップボード監視を開始
- `Stop`: クリップボード監視を停止
- `Startup ON`: Windows ログイン時の自動起動を有効化
- `Startup OFF`: スタートアップ登録を解除

開発中に Python で直接起動する場合:

```powershell
py -m auto_url_fixer --watch
```

起動後、たとえば次の URL をコピーすると、

```text
https://twitter.com/example/status/123
```

クリップボード内容が次のように置き換わります。

```text
https://fxtwitter.com/example/status/123
```

## 同梱ファイル

- `Auto URL Fixer.exe`: Python 不要で実行できる Windows 配布用実行ファイル
- `config.example.json`: 設定ファイルのサンプル

配布フォルダでは基本的に `Auto URL Fixer.exe` だけを操作します。`_internal` フォルダは exe の実行に必要なので、削除せず同じ場所に置いてください。設定を変更したい場合だけ `config.example.json` を `config.json` にコピーしてください。

## 設定ファイル

配布版で設定を変更したい場合は、`Auto URL Fixer.exe` と同じフォルダに設定ファイルを置きます。

```powershell
Copy-Item config.example.json config.json
```

`config.json` が同じフォルダにある場合、操作パネルの `Start` やスタートアップ起動でも自動的に読み込まれます。

開発中に任意の設定ファイルを指定して起動する場合:

```powershell
py -m auto_url_fixer --watch --config config.json
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
| X / Twitter | `twitter.com` -> `fxtwitter.com`, `x.com` -> `fxtwitter.com` |
| pixiv | `pixiv.net` -> `phixiv.net` |
| Instagram | `instagram.com` -> `ddinstagram.com` |
| TikTok | `tiktok.com` -> `tnktok.com` |
| Reddit | `reddit.com` -> `rxddit.com` |
| Tumblr | `tumblr.com` -> `tpmblr.com` |
| Bluesky | `bsky.app` -> `fxbsky.app` |

追加候補として `tfxktok.com`, `tiktokez.com`, `rxyddit.com`, `instagramez.com`, `fixthreads.net`, `fxtwitch.tv` などのルールも `config.example.json` に含めていますが、初期状態では `enabled: false` にしています。

## 停止とスタートアップ

- `Auto URL Fixer.exe` を開くと操作パネルが表示されます。
- `Start` は同じ exe を `--watch` でバックグラウンド起動します。
- `Stop` は停止要求を送り、必要に応じて監視プロセスを終了します。
- PID ファイルが無い古い起動でも停止できるようにしています。
- スタートアップ有効化時は、Windows の Startup フォルダに `Auto URL Fixer.exe --watch` を非表示で起動する `vbs` エントリを作成します。

## 配布用ビルド

開発者向けに、Windows 配布用 `.exe` を作るバッチを同梱しています。

```powershell
build_windows_exe.bat
```

成功すると `dist\Auto URL Fixer\` に次の配布セットを出力します。

- `Auto URL Fixer.exe`
- `_internal`
- `config.example.json`
- `README.md`

## テスト

```powershell
py -m unittest discover -s tests
```

## 補足

- すでに別の Auto URL Fixer が動いている場合、新しい起動は多重起動を避けるため失敗します。
- バックグラウンド起動時は標準出力が見えないため、必要ならターミナル起動で動作確認してください。
- 配布用 `Auto URL Fixer.exe` は `console=False` でビルドするため、直接実行してもターミナルは表示されません。
- PyInstaller の一時展開フォルダ削除エラーを避けるため、配布版は `onefile` ではなく `onedir` 形式でビルドします。
