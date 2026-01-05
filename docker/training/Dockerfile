FROM ai-research-platform-base:latest AS training

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    deepspeed==0.12.6 \
    flash-attn==2.5.0 --no-build-isolation

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    pdsh \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd && \
    echo 'root:training' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

ENV NCCL_DEBUG=INFO
ENV NCCL_SOCKET_IFNAME=eth0
ENV TORCH_DISTRIBUTED_DEBUG=DETAIL

WORKDIR /workspace

COPY src/ /workspace/src/
COPY configs/ /workspace/configs/

EXPOSE 22 29500

CMD ["/usr/sbin/sshd", "-D"]
