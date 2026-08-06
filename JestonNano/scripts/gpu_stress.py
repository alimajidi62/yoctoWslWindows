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
    c1 = torch.matmul(c, b)
    c2 = torch.matmul(c1, b)
    c3 = torch.matmul(c2, b)
    c4 = torch.matmul(c3, b)
    c5 = torch.matmul(c4, b)
    c6 = torch.matmul(c5, b)
    c7 = torch.matmul(c6, b)
    c8 = torch.matmul(c7, b)
    c9 = torch.matmul(c8, b)
    c10 = torch.matmul(c9, b)
    c11 = torch.matmul(c10, b)
    torch.cuda.synchronize()
    iterations += 1

    remaining = int(DURATION_SEC - elapsed)
    print(f"\r  {remaining:3d}s remaining  |  {iterations} iterations done", end="", flush=True)

print(f"\n\nDone. {iterations} matrix multiplies completed in {DURATION_SEC}s.")
