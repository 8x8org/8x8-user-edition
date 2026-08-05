# MSG197-AIRLLM-001 External GPU Feasibility Plan

## Verdict

`EXTERNAL_CUDA_ONLY_PHONE_AND_ACTIVE_NODE_REJECTED`

AirLLM can stream model layers or sparse experts to reduce GPU memory pressure, but that does not remove disk, model-download, dependency, latency, power or thermal requirements. The upstream explicitly requires additional disk for layer-wise model decomposition and may require gated-model credentials.

The pinned Kimi K3 path requires `compressed-tensors`, `flash-attn`, a CUDA 12 build of PyTorch and Transformers 4.56.x. Those requirements exclude the active Samsung Termux and Ubuntu PRoot node.

## Required external canary

The canary must run on a separately approved CUDA 12 Linux node with:

- immutable OS, driver, CUDA, Python, package and model pins;
- verified model license and access terms;
- pre-download disk and cache budget;
- no private 8x8 data;
- fixed synthetic prompt set;
- cold and warm latency, GPU memory, host RAM, disk I/O, cache growth, power and failure measurements;
- complete environment, Hugging Face cache, transformed shard and temporary-file removal proof.

## Decision boundary

No model acquisition, package installation or benchmark was performed. The issue remains open until exact external-node evidence exists. This packet makes the rejected-device rationale and execution contract explicit.
