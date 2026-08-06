import torch

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    gpu = torch.cuda.get_device_properties(0)
    print("GPU name:       ", torch.cuda.get_device_name(0))
    print("VRAM total:     ", round(gpu.total_memory / 1024**3, 1), "GB")
    print("CUDA version:   ", torch.version.cuda)
    print("SM count:       ", gpu.multi_processor_count)

    # Run a simple matrix multiply on the GPU
    a = torch.randn(4096, 4096, device="cuda")
    b = torch.randn(4096, 4096, device="cuda")
    c = torch.matmul(a, b)
    torch.cuda.synchronize()
    print("Matrix multiply (4096x4096) on GPU: OK  shape =", tuple(c.shape))
else:
    print("No CUDA-capable GPU found.")
