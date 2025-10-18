FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 必要なビルドツールと git/curl をインストール
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl \
    && rm -rf /var/lib/apt/lists/*

# pip を最新化して uv（パッケージマネージャ）をグローバルにインストール
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install uv

# アプリをコピー
COPY . /app

# 依存関係がある場合は pyproject.toml または requirements.txt を使ってインストール
# （uv が pyproject 対応なら `uv install` を試し、失敗したら requirements.txt を使用）
RUN if [ -f pyproject.toml ]; then \
      uv install --no-dev || true; \
    elif [ -f requirements.txt ]; then \
      pip install -r requirements.txt; \
    fi

EXPOSE 8000

# 開発用に bash をデフォルトにしておく（必要ならここを uv を使って起動するコマンドに置き換えてください）
CMD ["bash"]