# Auto URL Fixer

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-supported-0078D6?logo=windows&logoColor=white)
![PyInstaller](https://img.shields.io/badge/PyInstaller-onedir-2B5B84)
![Dependencies](https://img.shields.io/badge/runtime_dependencies-none-brightgreen)

Auto URL Fixer は、クリップボードにコピーされた URL を監視し、Discord などで展開しやすい fixer 系 URL へ自動変換する Windows 向けツールです。

通常利用では Python のインストールは不要です。配布フォルダ内の `Auto URL Fixer.exe` だけで、監視の起動・停止・スタートアップ ON/OFF を操作できます。

## 目次

1. [特徴](#特徴)
2. [クイックスタート](#クイックスタート)
3. [使い方](#使い方)
4. [変換ルール](#変換ルール)
5. [設定ファイル](#設定ファイル)
6. [コマンド一覧](#コマンド一覧)
7. [ディレクトリ構成](#ディレクトリ構成)
8. [開発・ビルド](#開発ビルド)
9. [トラブルシューティング](#トラブルシューティング)
10. [参考](#参考)

## 特徴

- クリップボード内のテキストから URL を検出します。
- 対応サービスのホスト名だけを fixer 系ホストへ変換します。
- 複数 URL を含むテキストにも対応します。
- 操作パネルから `Start` / `Stop` / `Startup ON` / `Startup OFF` を実行できます。
- 監視プロセスはターミナルを表示せずにバックグラウンドで動作します。
- 配布版は PyInstaller の `onedir` 形式で作成し、`_MEI...` 一時フォルダ警告を避けます。
- 設定ファイルを追加すると、変換先や有効/無効のルールを変更できます。

## クイックスタート

配布フォルダ `dist\Auto URL Fixer\` の中にある `Auto URL Fixer.exe` を起動してください。

```text
dist\Auto URL Fixer\Auto URL Fixer.exe
```

操作パネルが開いたら、`Start` を押すとクリップボード監視が始まります。たとえば次の URL をコピーすると、

```text
https://x.com/example/status/123
```

クリップボードの内容が次のように置き換わります。

```text
https://fxtwitter.com/example/status/123
```

## 使い方

| 操作 | 内容 |
| --- | --- |
| `Start` | クリップボード監視をバックグラウンドで開始します。 |
| `Stop` | 実行中の監視プロセスへ停止要求を送ります。 |
| `Startup ON` | Windows ログイン時に監視を自動開始するよう登録します。 |
| `Startup OFF` | スタートアップ登録を解除します。 |

Status 表示は定期的に更新されます。`Status: Running` なら監視中、`Status: Stopped` なら停止中です。

スタートアップ登録は Windows の Startup フォルダに `Auto URL Fixer.vbs` を作成します。この VBS は `Auto URL Fixer.exe --watch` を非表示で実行します。

## 変換ルール

既定で有効な変換は次の通りです。

| 対象 | 変換例 |
| --- | --- |
| X / Twitter | `twitter.com` -> `fxtwitter.com`, `x.com` -> `fxtwitter.com` |
| pixiv | `pixiv.net` -> `phixiv.net` |
| Instagram | `instagram.com` -> `ddinstagram.com` |
| TikTok | `tiktok.com` -> `tnktok.com` |
| Reddit | `reddit.com` -> `rxddit.com` |
| Tumblr | `tumblr.com` -> `tpmblr.com` |
| Tumblr サブドメイン | `staff.tumblr.com` -> `staff.tpmblr.com` |
| Bluesky | `bsky.app` -> `fxbsky.app` |

`config.example.json` には追加候補として `tfxktok.com`, `tiktokez.com`, `rxyddit.com`, `instagramez.com`, `fixthreads.net`, `fxtwitch.tv` などのルールも含めています。初期状態では `enabled: false` です。

## 設定ファイル

設定を変更したい場合は、`Auto URL Fixer.exe` と同じフォルダに `config.json` を置きます。

```powershell
Copy-Item config.example.json config.json
```

`config.json` が同じフォルダにある場合、操作パネルの `Start` やスタートアップ起動でも自動的に読み込まれます。

設定例:

```json
{
  "poll_interval_seconds": 0.5,
  "log_rewrites": true,
  "rules": [
    {
      "name": "X / Twitter to FxTwitter",
      "enabled": true,
      "hosts": ["twitter.com", "www.twitter.com", "mobile.twitter.com"],
      "target_host": "fxtwitter.com"
    }
  ]
}
```

| 項目 | 内容 |
| --- | --- |
| `poll_interval_seconds` | クリップボードを確認する間隔です。 |
| `log_rewrites` | 変換内容をログ出力するかどうかです。 |
| `rules` | 変換ルールの一覧です。 |
| `enabled` | `false` にすると、そのルールは使われません。 |
| `hosts` | 変換元のホスト名です。 |
| `target_host` | 変換先のホスト名です。 |
| `host_suffix` | サブドメインをまとめて変換する場合の変換元サフィックスです。 |
| `target_suffix` | サブドメインをまとめて変換する場合の変換先サフィックスです。 |

## コマンド一覧

配布版 exe では、次のコマンドを利用できます。

| コマンド | 内容 |
| --- | --- |
| `Auto URL Fixer.exe` | 操作パネルを開きます。 |
| `Auto URL Fixer.exe --watch` | 現在のプロセスで監視を開始します。 |
| `Auto URL Fixer.exe --start` | 監視プロセスをバックグラウンド起動します。 |
| `Auto URL Fixer.exe --stop` | 実行中の監視プロセスを停止します。 |
| `Auto URL Fixer.exe --enable-startup` | スタートアップを有効化します。 |
| `Auto URL Fixer.exe --disable-startup` | スタートアップを無効化します。 |

開発中に Python で直接実行する場合は、次の形式でも操作できます。

```powershell
py -m auto_url_fixer --watch
py -m auto_url_fixer --start
py -m auto_url_fixer --stop
py -m auto_url_fixer --once
py -m auto_url_fixer --watch --config config.json
```

## ディレクトリ構成

```text
.
├── auto_url_fixer/
│   ├── __main__.py
│   ├── cli.py
│   ├── clipboard.py
│   ├── config.py
│   ├── control_panel.py
│   ├── rewriter.py
│   ├── runtime.py
│   └── watcher.py
├── tests/
│   ├── test_rewriter.py
│   └── test_runtime.py
├── auto_url_fixer.spec
├── build_windows_exe.bat
├── config.example.json
├── pyproject.toml
└── README.md
```

| パス | 役割 |
| --- | --- |
| `auto_url_fixer/cli.py` | コマンドライン引数と起動処理です。 |
| `auto_url_fixer/control_panel.py` | Tkinter 製の操作パネルです。 |
| `auto_url_fixer/runtime.py` | 起動、停止、PID管理、スタートアップ登録を扱います。 |
| `auto_url_fixer/watcher.py` | クリップボード監視ループです。 |
| `auto_url_fixer/rewriter.py` | URL 変換処理です。 |
| `config.example.json` | 設定ファイルのサンプルです。 |
| `build_windows_exe.bat` | Windows 配布用 exe を作成するバッチです。 |

## 開発・ビルド

開発には Python 3.10 以上を使用します。通常利用だけなら Python は不要ですが、テストや exe の再ビルドには Python が必要です。

テスト:

```powershell
py -m unittest discover -s tests
```

配布用 exe のビルド:

```powershell
build_windows_exe.bat
```

成功すると `dist\Auto URL Fixer\` に次の配布セットが出力されます。

```text
dist\Auto URL Fixer\
├── Auto URL Fixer.exe
├── _internal\
├── config.example.json
└── README.md
```

`_internal` フォルダは exe の実行に必要です。削除せず、`Auto URL Fixer.exe` と同じ場所に置いてください。

## トラブルシューティング

### `Failed to remove temporary directory: ...\_MEI...` が出る

古い `onefile` 版 exe を実行している可能性があります。`dist\Auto URL Fixer.exe` のように `dist` 直下に単体 exe がある場合は使わず、`dist\Auto URL Fixer\Auto URL Fixer.exe` を使ってください。

### `Stop` を押しても `No running instance was found.` と表示される

古い exe や別の場所の exe から起動した監視プロセスが残っている可能性があります。新しい `dist\Auto URL Fixer\Auto URL Fixer.exe` から起動し直してください。スタートアップ登録済みの場合は、`Startup OFF` の後に `Startup ON` を押して登録先を更新してください。

### `Status` が `Running` に変わらない

監視プロセスの起動に失敗している可能性があります。`Failed to start.` が表示される場合は、配布フォルダに `_internal` が残っているか確認してください。また、古い単体 exe ではなく `dist\Auto URL Fixer\Auto URL Fixer.exe` を起動してください。

### `Build virtual environment is broken.` と表示される

`.venv` が古い Python インストール先を参照している可能性があります。Python をインストールした上で `.venv` フォルダを削除し、`build_windows_exe.bat` を再実行してください。

### 変換されない URL がある

`config.json` を使っている場合、該当ルールの `enabled` が `true` になっているか確認してください。また、対象ホストが `hosts` または `host_suffix` に含まれている必要があります。
