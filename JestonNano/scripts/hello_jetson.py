import platform
import socket
import datetime
import ctypes
import time

# PTX kernel: element-wise float32 addition, compiled at runtime by the CUDA driver.
# sm_53 = Maxwell (Jetson Nano), PTX 6.4 = CUDA 10.2 compatible.
_PTX = b""".version 6.4
.target sm_53
.address_size 64
.visible .entry vadd(
    .param .u64 pa, .param .u64 pb, .param .u64 pc, .param .u32 pn
) {
    .reg .pred %p0;
    .reg .f32  %f<3>;
    .reg .u32  %r<4>;
    .reg .u64  %rd<7>;
    ld.param.u64 %rd0,[pa]; ld.param.u64 %rd1,[pb];
    ld.param.u64 %rd2,[pc]; ld.param.u32 %r0,[pn];
    mov.u32 %r1,%ctaid.x;  mov.u32 %r2,%ntid.x;
    mad.lo.u32 %r3,%r1,%r2,%tid.x;
    setp.ge.u32 %p0,%r3,%r0; @%p0 bra DONE;
    mul.wide.u32 %rd3,%r3,4;
    add.u64 %rd4,%rd0,%rd3; add.u64 %rd5,%rd1,%rd3; add.u64 %rd6,%rd2,%rd3;
    ld.global.f32 %f0,[%rd4]; ld.global.f32 %f1,[%rd5];
    add.f32 %f2,%f0,%f1;    st.global.f32 [%rd6],%f2;
DONE: ret;
}\0"""

N       = 1024 * 1024       # 1 M float32 elements (~4 MB per array)
THREADS = 256
BLOCKS  = (N + THREADS - 1) // THREADS

print("=" * 48)
print("  Hello from Jetson Nano!")
print("=" * 48)
print(f"  Hostname : {socket.gethostname()}")
print(f"  OS       : {platform.system()} {platform.release()}")
print(f"  Machine  : {platform.machine()}")
print(f"  Python   : {platform.python_version()}")
print(f"  Time     : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 48)

print("\n[GPU — CUDA Driver API via ctypes]")
try:
    cuda = ctypes.CDLL("libcuda.so.1")

    if cuda.cuInit(0) != 0:
        raise RuntimeError("cuInit failed")

    dev = ctypes.c_int(0)
    cuda.cuDeviceGet(ctypes.byref(dev), 0)
    name_buf = ctypes.create_string_buffer(128)
    cuda.cuDeviceGetName(name_buf, 128, dev)

    ctx = ctypes.c_void_p()
    if cuda.cuCtxCreate_v2(ctypes.byref(ctx), 0, dev) != 0:
        raise RuntimeError("cuCtxCreate failed")

    mod = ctypes.c_void_p()
    if cuda.cuModuleLoadData(ctypes.byref(mod), _PTX) != 0:
        raise RuntimeError("cuModuleLoadData failed — PTX rejected by driver")

    fn = ctypes.c_void_p()
    cuda.cuModuleGetFunction(ctypes.byref(fn), mod, b"vadd")

    sz  = N * ctypes.sizeof(ctypes.c_float)
    h_a = (ctypes.c_float * N)(*range(N))       # 0.0, 1.0, 2.0, ...
    h_b = (ctypes.c_float * N)(*([2.0] * N))    # 2.0, 2.0, 2.0, ...
    h_c = (ctypes.c_float * N)()

    d_a = ctypes.c_uint64(); d_b = ctypes.c_uint64(); d_c = ctypes.c_uint64()
    for d in (d_a, d_b, d_c):
        cuda.cuMemAlloc_v2(ctypes.byref(d), sz)
    cuda.cuMemcpyHtoD_v2(d_a, h_a, sz)
    cuda.cuMemcpyHtoD_v2(d_b, h_b, sz)

    n_arg = ctypes.c_uint32(N)
    args  = (ctypes.c_void_p * 4)(
        ctypes.cast(ctypes.byref(d_a),   ctypes.c_void_p),
        ctypes.cast(ctypes.byref(d_b),   ctypes.c_void_p),
        ctypes.cast(ctypes.byref(d_c),   ctypes.c_void_p),
        ctypes.cast(ctypes.byref(n_arg), ctypes.c_void_p),
    )

    # warm-up: forces JIT compilation so it doesn't skew the timed run
    cuda.cuLaunchKernel(fn, BLOCKS, 1, 1, THREADS, 1, 1, 0, None, args, None)
    cuda.cuCtxSynchronize()

    t0 = time.perf_counter()
    if cuda.cuLaunchKernel(fn, BLOCKS, 1, 1, THREADS, 1, 1, 0, None, args, None) != 0:
        raise RuntimeError("cuLaunchKernel failed")
    cuda.cuCtxSynchronize()
    gpu_ms = (time.perf_counter() - t0) * 1e3

    cuda.cuMemcpyDtoH_v2(h_c, d_c, sz)
    ok = all(abs(h_c[i] - (i + 2.0)) < 1e-3 for i in range(0, N, N // 8))

    # CPU reference for speedup comparison
    t0 = time.perf_counter()
    _ = [i + 2.0 for i in range(N)]
    cpu_ms = (time.perf_counter() - t0) * 1e3

    for d in (d_a, d_b, d_c):
        cuda.cuMemFree_v2(d)
    cuda.cuModuleUnload(mod)
    cuda.cuCtxDestroy_v2(ctx)

    print(f"  Device   : {name_buf.value.decode()}")
    print(f"  Kernel   : vadd  ({N:,} × float32)")
    print(f"  GPU time : {gpu_ms:.2f} ms")
    print(f"  CPU time : {cpu_ms:.2f} ms  (Python list comprehension)")
    print(f"  Speedup  : {cpu_ms / gpu_ms:.1f}×")
    print(f"  Verify   : {'PASS ✓' if ok else 'FAIL ✗'}")

except Exception as e:
    print(f"  CUDA unavailable: {e}")
    print("  --> To enable CUDA, add to local.conf and rebuild:")
    print("      IMAGE_INSTALL:append = \" tegra-libraries\"")

# GPU hardware info from sysfs — works without CUDA
print("\n[GPU — Hardware Info (sysfs/debugfs)]")

def _sysfs(path):
    try:
        return open(path).read().strip()
    except OSError:
        return None

cur_hz  = _sysfs("/sys/kernel/debug/clk/gm20b.gbus/clk_rate")
max_hz  = _sysfs("/sys/kernel/debug/clk/cap.gbus/clk_rate")
edp_hz  = _sysfs("/sys/kernel/debug/clk/edp.gbus/clk_rate")
enables = _sysfs("/sys/kernel/debug/clk/gm20b.gbus/clk_enable_count")

def hz_to_mhz(val):
    return f"{int(val) // 1_000_000} MHz" if val and val.isdigit() else "unknown"

print(f"  Model    : NVIDIA GM20B (Maxwell, 128 CUDA cores)")
print(f"  Cur freq : {hz_to_mhz(cur_hz)}  (0 = idle/gated)")
print(f"  Max freq : {hz_to_mhz(max_hz)}")
print(f"  EDP cap  : {hz_to_mhz(edp_hz)}")
print(f"  Enabled  : {'yes' if enables and enables != '0' else 'no (powered down)'}")

print("=" * 48)
