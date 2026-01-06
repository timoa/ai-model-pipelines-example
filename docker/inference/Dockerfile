FROM ghcr.io/timoa/ai-model-pipelines-example-base:main AS inference

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    vllm==0.2.7 \
    triton==2.1.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnuma-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY src/inference/ /workspace/inference/

ENV VLLM_WORKER_MULTIPROC_METHOD=spawn

EXPOSE 8000

CMD ["python", "-m", "vllm.entrypoints.api_server", "--host", "0.0.0.0", "--port", "8000"]
