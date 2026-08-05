import torch
import time

DURATION_SEC = 60
SIZE = 8192  # large matrix to maximize GPU utilization

print(f"Stressing GPU for {DURATION_SEC} seconds — check Task Manager > Performance > GPU")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Matrix size: {SIZE}x{SIZE}\n")

a = torch.randn(SIZE, SIZE, device="cuda")
b = torch.randn(SIZE, SIZE, device="cuda")

start = time.time()
iterations = 0

while True:
    elapsed = time.time() - start
    if elapsed >= DURATION_SEC:
        break

    c = torch.matmul(a, b)
    torch.cuda.synchronize()
    iterations += 1

    remaining = int(DURATION_SEC - elapsed)
    print(f"\r  {remaining:3d}s remaining  |  {iterations} iterations done", end="", flush=True)

print(f"\n\nDone. {iterations} matrix multiplies completed in {DURATION_SEC}s.")
