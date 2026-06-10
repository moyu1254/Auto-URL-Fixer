# Auto URL Fixer

クリップボードにコピーされた URL を監視し、Discord などで展開しやすい fixer 系 URL に自動変換する小さなツールです。

## できること

- クリップボード内のテキストから URL を検出
- 対応サービスのホスト名だけを変換
- 複数 URL を含むテキストにも対応
- 変換ルールは `config.example.json` で変更可能
- 追加候補のルールは初期状態では無効化

## 使い方

Python 3.10 以上を想定しています。外部ライブラリは不要です。

```powershell
py -m auto_url_fixer
```

起動後、たとえば次の URL をコピーすると:

```text
https://twitter.com/example/status/123
```

クリップボード内容が自動で次のように置き換わります:

```text
https://fxtwitter.com/example/status/123
```

停止するにはターミナルで `Ctrl+C` を押してください。

## 設定ファイルを使う

まずサンプル設定をコピーします。

```powershell
Copy-Item config.example.json config.json
```

設定を指定して起動します。

```powershell
py -m auto_url_fixer --config config.json
```

各ルールは次のような形式です。

```json
{
  "name": "X / Twitter to FxTwitter",
  "enabled": true,
  "hosts": ["twitter.com", "www.twitter.com", "mobile.twitter.com"],
  "target_host": "fxtwitter.com"
}
```

`enabled` を `false` にすると、そのルールは使われません。

## 既定で有効な主な変換

| 対象 | 変換例 |
| --- | --- |
| X / Twitter | `twitter.com` -> `fxtwitter.com`, `x.com` -> `fixupx.com` |
| pixiv | `pixiv.net` -> `phixiv.net` |
| Instagram | `instagram.com` -> `ddinstagram.com` |
| TikTok | `tiktok.com` -> `tnktok.com` |
| Reddit | `reddit.com` -> `rxddit.com` |
| Tumblr | `tumblr.com` -> `tpmblr.com` |
| Bluesky | `bsky.app` -> `fxbsky.app` |

追加候補として `tfxktok.com`, `tiktokez.com`, `rxyddit.com`, `instagramez.com`, `fixthreads.net`, `fxtwitch.tv` などのルールもサンプル設定に入っていますが、状態が不安定または closed source とされるものがあるため初期状態では無効にしています。

## テスト

```powershell
py -m unittest discover -s tests
```

## ダブルクリックで起動

`start_auto_url_fixer.bat` をダブルクリックすると、既定ルールで監視を開始します。
