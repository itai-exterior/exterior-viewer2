#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
models/ フォルダ内の GLB/GLTF を走査し、
  1. 各モデルの閲覧URL用QRコード (qr/<モデル名>.png)
  2. モデル一覧ページ (index.html)
  3. モデル一覧データ (models.json)
を自動生成するスクリプト。GitHub Actions から呼び出される想定。

ローカルで試す場合:
  pip install "qrcode[pil]"
  BASE_URL="https://itai-exterior.github.io/exterior-viewer2/" python scripts/generate_qr.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote

import qrcode

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"
QR_DIR = ROOT / "qr"
JST = timezone(timedelta(hours=9))


def resolve_base_url() -> str:
    """公開ベースURLを決定する。優先順: 環境変数 BASE_URL > GITHUB_REPOSITORY から自動推定"""
    env = os.environ.get("BASE_URL", "").strip()
    if env:
        return env if env.endswith("/") else env + "/"

    repo = os.environ.get("GITHUB_REPOSITORY", "")  # 例: "itai-exterior/exterior-viewer2"
    if "/" in repo:
        owner, name = repo.split("/", 1)
        if name.lower() == f"{owner.lower()}.github.io":
            return f"https://{owner}.github.io/"
        return f"https://{owner}.github.io/{name}/"

    print("ERROR: BASE_URL 環境変数か GITHUB_REPOSITORY が必要です", file=sys.stderr)
    sys.exit(1)


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n} GB"


def make_qr(url: str, out_path: Path) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)


def main() -> None:
    base_url = resolve_base_url()
    QR_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)

    models = sorted(
        [p for p in MODELS_DIR.iterdir() if p.suffix.lower() in (".glb", ".gltf")],
        key=lambda p: p.name.lower(),
    )

    entries = []
    for p in models:
        rel = f"models/{p.name}"
        viewer_url = f"{base_url}viewer.html?model={quote(rel, safe='/')}"
        qr_path = QR_DIR / (p.stem + ".png")
        make_qr(viewer_url, qr_path)
        entries.append(
            {
                "name": p.stem,
                "file": rel,
                "size": human_size(p.stat().st_size),
                "viewer_url": viewer_url,
                "qr": f"qr/{qr_path.name}",
            }
        )
        print(f"OK: {p.name} -> {qr_path.name}")

    # models.json
    (ROOT / "models.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(JST).isoformat(timespec="seconds"),
                "base_url": base_url,
                "models": entries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # index.html(一覧ページ)
    cards = []
    for e in entries:
        cards.append(f"""
    <div class="card">
      <h2>{e['name']}</h2>
      <a href="{e['viewer_url']}"><img class="qr" src="{e['qr']}" alt="QR: {e['name']}"></a>
      <p class="meta">{e['size']}</p>
      <p><a class="btn" href="{e['viewer_url']}">3Dビューアで開く</a></p>
      <p class="url">{e['viewer_url']}</p>
    </div>""")

    updated = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>外構3Dモデル一覧</title>
<style>
  body {{ margin: 0; font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif; background: #f4f5f7; color: #222; }}
  header {{ background: #24282e; color: #fff; padding: 16px 20px; }}
  header h1 {{ margin: 0; font-size: 18px; }}
  header p {{ margin: 4px 0 0; font-size: 12px; color: #9aa3ad; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; padding: 20px; max-width: 1200px; margin: 0 auto; }}
  .card {{ background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); text-align: center; }}
  .card h2 {{ font-size: 15px; margin: 0 0 10px; word-break: break-all; }}
  .qr {{ width: 180px; height: 180px; }}
  .meta {{ font-size: 12px; color: #777; margin: 6px 0; }}
  .btn {{ display: inline-block; background: #2f6fed; color: #fff; text-decoration: none; padding: 8px 18px; border-radius: 6px; font-size: 13px; }}
  .url {{ font-size: 10px; color: #aaa; word-break: break-all; }}
  .empty {{ padding: 60px 20px; text-align: center; color: #888; grid-column: 1 / -1; }}
</style>
</head>
<body>
<header>
  <h1>外構3Dモデル一覧</h1>
  <p>最終更新: {updated}(自動生成)</p>
</header>
<main>
{''.join(cards) if cards else '<div class="empty">models/ フォルダに .glb ファイルを追加すると、ここに自動で表示されます。</div>'}
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"生成完了: モデル {len(entries)} 件 / index.html / models.json")


if __name__ == "__main__":
    main()
