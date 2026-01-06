# Optimization Guide

This guide covers performance optimization techniques for training AI models efficiently.

## 🎯 Optimization Goals

1. **Maximize GPU Utilization**: Keep GPUs busy (target: >85%)
2. **Minimize Training Time**: Faster iterations = more experiments
3. **Reduce Costs**: Efficient resource usage = lower bills
4. **Maintain Quality**: Don't sacrifice model performance

## 🚀 Docker Build Optimization

### Problem: Slow Container Builds

**Before**: 45 minutes per build
**After**: 5 minutes per build
**Improvement**: 9x faster

### Techniques

#### 1. Layer Ordering

```dockerfile
# ❌ BAD: Application code changes invalidate everything
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04
COPY . /workspace
RUN pip install -r requirements.txt

# ✅ GOOD: Separate layers by change frequency
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04

# System deps (rarely change)
RUN apt-get update && apt-get install -y python3.11

# Python deps (moderate changes)
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Application code (frequent changes)
COPY . /workspace
```

#### 2. BuildKit Cache Mounts

```dockerfile
# Persistent pip cache across builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

#### 3. Multi-Stage Builds

```dockerfile
# Build stage
FROM base AS builder
RUN pip install torch==2.1.2

# Runtime stage (smaller)
FROM base AS runtime
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
```

### Measuring Impact

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with timing
time docker build -f docker/base/Dockerfile .

# Check cache usage
docker build --progress=plain -f docker/base/Dockerfile . 2>&1 | grep CACHED
```

## ⚡ Training Speed Optimization

### 1. Mixed Precision Training

**Impact**: 2x speedup on A100 GPUs

```python
# Enable in config
training:
  dtype: "bfloat16"  # or "float16"

# In training loop
scaler = torch.cuda.amp.GradScaler(enabled=(dtype == "float16"))
with torch.amp.autocast(device_type="cuda", dtype=ptdtype):
    logits, loss = model(x, y)
```

**Results**:

- FP32: 50K tokens/sec
- BF16: 100K tokens/sec (2x faster)
- Memory: 40GB → 20GB (2x reduction)

### 2. Flash Attention

**Impact**: 3x faster attention, 50% less memory

```bash
# Install
pip install flash-attn --no-build-isolation

# Use in model
from flash_attn import flash_attn_func

# Replace standard attention
output = flash_attn_func(q, k, v, causal=True)
```

**Benchmarks**:

- Standard attention: 150ms/batch
- Flash attention: 50ms/batch (3x faster)

### 3. Gradient Accumulation

**Impact**: Larger effective batch size without OOM

```yaml
training:
  batch_size: 4  # Per GPU
  gradient_accumulation_steps: 8  # Effective batch size = 32
```

**Memory vs Batch Size**:

- Batch 32: 80GB (OOM on A100)
- Batch 4 + accum 8: 25GB (fits!)

### 4. Efficient Data Loading

```python
# ❌ BAD: CPU bottleneck
train_loader = DataLoader(dataset, batch_size=32, num_workers=0)

# ✅ GOOD: Parallel loading
train_loader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,      # Parallel workers
    pin_memory=True,    # Faster GPU transfer
    prefetch_factor=2   # Prefetch batches
)
```

**Impact**:

- GPU utilization: 40% → 87%
- Training time: 10 hours → 5 hours

### 5. Compiled Models (PyTorch 2.0+)

```python
# Compile model for faster execution
model = torch.compile(model, mode="reduce-overhead")
```

**Results**:

- Inference: 20% faster
- Training: 10-15% faster
- First iteration slower (compilation time)

## 🔧 GPU Utilization Optimization

### Monitoring GPU Usage

```bash
# Real-time monitoring
watch -n 1 nvidia-smi

# Detailed profiling
python -m torch.utils.bottleneck train.py --config config.yaml
```

### Common Issues

#### Issue 1: Low GPU Utilization (<50%)

**Causes**:

- Data loading bottleneck
- Small batch size
- CPU preprocessing

**Solutions**:

```yaml
training:
  num_workers: 8  # Increase workers
  batch_size: 16  # Increase if memory allows
  prefetch_factor: 4  # Prefetch more batches
```

#### Issue 2: GPU Memory Underutilized

**Cause**: Batch size too small

**Solution**: Gradient accumulation

```yaml
training:
  batch_size: 8  # Increase until 90% memory used
  gradient_accumulation_steps: 4
```

#### Issue 3: Frequent CPU-GPU Transfers

**Solution**: Pin memory and async transfers

```python
x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
```

## 📊 Data Pipeline Optimization

### Problem: Slow Tokenization

**Before**: 48 hours for 100GB dataset
**After**: 4 hours
**Improvement**: 12x faster

### Techniques

#### 1. Parallel Processing

```python
# Use all CPU cores
from multiprocessing import cpu_count

dataset.map(
    tokenize_function,
    batched=True,
    num_proc=cpu_count(),  # Parallel workers
    batch_size=1000
)
```

#### 2. Memory-Mapped Files

```python
# Efficient random access for large datasets
data = np.memmap("data.bin", dtype=np.uint16, mode="r")
chunk = data[start:end]  # Fast, no full load
```

#### 3. Streaming Processing

```python
# Process data without loading all into memory
from datasets import load_dataset

dataset = load_dataset("openwebtext", streaming=True)
for batch in dataset.iter(batch_size=1000):
    process(batch)
```

## 🌐 Distributed Training Optimization

### Multi-GPU (Single Node)

```bash
# Distributed Data Parallel
torchrun --nproc_per_node=8 train.py --config config.yaml
```

**Optimization**:

```python
# Efficient gradient communication
model = DDP(
    model,
    device_ids=[local_rank],
    gradient_as_bucket_view=True,  # Faster gradients
    static_graph=True  # If model structure doesn't change
)
```

### Multi-Node (Kubernetes)

**Network Optimization**:

```yaml
env:
  - name: NCCL_IB_DISABLE
    value: "0"  # Enable InfiniBand
  - name: NCCL_NET_GDR_LEVEL
    value: "5"  # GPU Direct RDMA
  - name: NCCL_SOCKET_IFNAME
    value: "eth0"  # Network interface
```

**Results**:

- 8 GPUs (1 node): 100K tokens/sec
- 32 GPUs (4 nodes): 380K tokens/sec (95% scaling efficiency)

## 💰 Cost Optimization

### 1. Spot Instances

**Savings**: 60-70% cost reduction

```yaml
# Kubernetes tolerations for spot instances
tolerations:
- key: "node.kubernetes.io/spot"
  operator: "Exists"
  effect: "NoSchedule"
```

**Preemption Handling**:

```python
# Frequent checkpointing
if iter_num % 500 == 0:
    save_checkpoint(model, optimizer, iter_num)
```

### 2. GPU Time-Slicing

**Use Case**: Development and debugging

```yaml
# Share GPU among multiple pods
resources:
  limits:
    nvidia.com/gpu: 0.25  # 1/4 of GPU
```

**Savings**: 4x more users per GPU

### 3. Auto-Scaling

```yaml
# Scale down when idle
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: training-autoscaler
spec:
  minReplicas: 0
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: gpu
      target:
        type: Utilization
        averageUtilization: 80
```

## 📈 Benchmarking

### Training Speed

```bash
# Measure tokens/sec
python scripts/benchmark_training.py \
  --config configs/train-small.yaml \
  --steps 100
```

### Data Loading

```bash
# Measure data loading overhead
python scripts/benchmark_dataloader.py \
  --data-dir data/train \
  --batch-size 32 \
  --num-workers 8
```

### GPU Utilization

```bash
# Profile GPU usage
nsys profile -o profile.qdrep python train.py --config config.yaml
nsys stats profile.qdrep
```

## 🎓 Optimization Checklist

### Before Training

- [ ] Enable mixed precision (bfloat16)
- [ ] Tune batch size (maximize GPU memory usage)
- [ ] Set num_workers for data loading
- [ ] Enable gradient checkpointing if OOM
- [ ] Compile model with torch.compile()

### During Training

- [ ] Monitor GPU utilization (target: >85%)
- [ ] Check data loading time (should be <5% of step time)
- [ ] Verify gradient norms (detect instability)
- [ ] Track tokens/sec (compare to baseline)

### After Training

- [ ] Profile with PyTorch Profiler
- [ ] Analyze bottlenecks
- [ ] Document optimizations
- [ ] Update benchmarks

## 📚 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| GPU Utilization | >85% | During training |
| Data Loading Overhead | <5% | Of total step time |
| Tokens/sec (8xA100) | >100K | For GPT-small |
| Build Time | <10 min | Docker images |
| CI Pipeline | <15 min | Full pipeline |

## 🔍 Debugging Performance Issues

### Step 1: Identify Bottleneck

```python
import time

# Measure each component
t0 = time.time()
x, y = next(dataloader)
data_time = time.time() - t0

t0 = time.time()
loss = model(x, y)
forward_time = time.time() - t0

t0 = time.time()
loss.backward()
backward_time = time.time() - t0

print(f"Data: {data_time:.3f}s, Forward: {forward_time:.3f}s, Backward: {backward_time:.3f}s")
```

### Step 2: Apply Targeted Optimization

- **Data loading slow**: Increase num_workers
- **Forward pass slow**: Enable mixed precision, use Flash Attention
- **Backward pass slow**: Enable gradient checkpointing
- **All slow**: Check GPU utilization, may need bigger batch

### Step 3: Measure Impact

```bash
# Before optimization
Tokens/sec: 50K
GPU Util: 45%

# After optimization
Tokens/sec: 100K
GPU Util: 87%
```

## 🎯 Summary

Key optimizations by impact:

1. **Mixed Precision**: 2x speedup (easy)
2. **Flash Attention**: 3x faster attention (medium)
3. **Data Loading**: 2x speedup (easy)
4. **Distributed Training**: Nx speedup (hard)
5. **Spot Instances**: 70% cost savings (easy)

Start with easy wins, then tackle harder optimizations as needed.
