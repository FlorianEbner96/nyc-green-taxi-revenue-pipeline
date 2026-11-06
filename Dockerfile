FROM ghcr.io/astral-sh/uv:0.13.5 AS uv
FROM python:3.13.17-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

COPY --from=uv /uv /uvx /bin/

# Install the dependencies first: this layer is only rebuilt when pyproject.toml / uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Then install the pipeline package itself.
COPY src ./src
RUN uv sync --locked --no-dev

# data/ is not copied into the image: mount it at run time so the downloads
# and the result stay on the host (see README).
ENTRYPOINT ["uv", "run", "--no-sync", "python", "-m", "data_pipeline.flow"]
