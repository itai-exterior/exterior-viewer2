# 外構3Dデータ QR公開 自動化スターター

GLBファイルを `models/` フォルダに置くだけで、以下が **全自動** で行われます。

1. スマホ閲覧用URLのQRコード生成(`qr/モデル名.png`)
2. モデル一覧ページの更新(`index.html`)
3. GitHub Pages への公開

詳しい手順は同梱の **手順書(Word)** を参照してください。

## フォルダ構成

```
├── viewer.html               3Dビューア本体(model-viewer使用)
├── index.html                モデル一覧ページ(自動生成・初回は空)
├── models/                   ★ GLBファイルをここに入れる
├── qr/                       QRコードPNG(自動生成)
├── models.json               モデル一覧データ(自動生成)
├── scripts/generate_qr.py    生成スクリプト
└── .github/workflows/publish.yml   自動実行の設定
```

## 初回セットアップ(要点のみ)

1. このフォルダの中身を GitHub リポジトリのルートにアップロード
2. Settings > Pages で「Deploy from a branch / main / (root)」を設定
3. Settings > Actions > General > Workflow permissions を
   **Read and write permissions** に変更
4. `models/` に GLB を1つアップロードして動作確認

## 日常運用(1案件あたり2〜3分)

1. RIKCAD からエクスポート → GLB に変換
2. GitHub の `models/` フォルダに「Add file > Upload files」でアップロード
3. 1〜2分待つと `qr/` にQRコードが自動生成される
4. QR画像をダウンロードして図面・提案書に貼付

## 注意事項

- ファイル名は **半角英数字とハイフン** 推奨(例: `tanaka-tei_v2.glb`)。
  日本語名でも動作しますがURLが長くなりQRが読み取りにくくなります。
- 1ファイル **30MB以下** 推奨(スマホ回線での読み込み速度のため)。
  GitHubの上限は100MB/ファイルです。
- 公開URLはリポジトリ名から自動判定されます。独自ドメイン等を使う場合は
  Settings > Secrets and variables > Actions > **Variables** に
  `BASE_URL` を登録してください(例: `https://example.com/viewer/`)。
- 施主名など個人情報をファイル名に含めない運用を推奨します
  (公開リポジトリの場合、URLは誰でもアクセス可能です)。
