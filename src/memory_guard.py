"""
Memory Profiling and Guard Subsystem for Agentic Research PRO.
Tracks resident set size (RSS), bounds thread allocations, and coordinates
strategic memory release across pipeline stages.
"""

import os
import gc
import logging
import subprocess

logger = logging.getLogger("MemoryGuard")

_last_rss_mb: float = 0.0


def get_detailed_memory_stats() -> dict:
    """
    Read detailed memory telemetry:
    - Python RSS
    - Total RSS of Python process + all child processes (Chromium, Node driver)
    - Number of child processes & Chromium/Node processes
    - Linux cgroup memory.current and memory.max
    """
    py_rss_mb = 0.0
    try:
        if os.path.exists("/proc/self/statm"):
            with open("/proc/self/statm", "r") as f:
                fields = f.read().split()
                page_size_kb = os.sysconf("SC_PAGE_SIZE") / 1024.0
                py_rss_mb = (int(fields[1]) * page_size_kb) / 1024.0
        else:
            out = subprocess.check_output(["ps", "-o", "rss=", "-p", str(os.getpid())])
            py_rss_mb = int(out.strip()) / 1024.0
    except Exception:
        pass

    # Process tree scan via /proc (Linux container)
    child_count = 0
    chromium_count = 0
    total_rss_mb = py_rss_mb
    try:
        current_pid = str(os.getpid())
        for entry in os.listdir("/proc"):
            if entry.isdigit() and entry != current_pid:
                try:
                    with open(f"/proc/{entry}/statm", "r") as f:
                        rss_pages = int(f.read().split()[1])
                        proc_rss = (rss_pages * os.sysconf("SC_PAGE_SIZE")) / (1024 * 1024)
                        total_rss_mb += proc_rss
                    child_count += 1
                    with open(f"/proc/{entry}/cmdline", "rb") as f:
                        cmd = f.read().decode("utf-8", errors="ignore").lower()
                        if "chrome" in cmd or "chromium" in cmd or "node" in cmd:
                            chromium_count += 1
                except Exception:
                    pass
    except Exception:
        pass

    # Linux cgroup v2 / v1 memory limits
    cg_current_mb = 0.0
    cg_max_mb = 0.0
    try:
        if os.path.exists("/sys/fs/cgroup/memory.current"):
            with open("/sys/fs/cgroup/memory.current", "r") as f:
                cg_current_mb = int(f.read().strip()) / (1024 * 1024)
        elif os.path.exists("/sys/fs/cgroup/memory/memory.usage_in_bytes"):
            with open("/sys/fs/cgroup/memory/memory.usage_in_bytes", "r") as f:
                cg_current_mb = int(f.read().strip()) / (1024 * 1024)

        if os.path.exists("/sys/fs/cgroup/memory.max"):
            with open("/sys/fs/cgroup/memory.max", "r") as f:
                val = f.read().strip()
                cg_max_mb = (int(val) / (1024 * 1024)) if val != "max" else 0.0
        elif os.path.exists("/sys/fs/cgroup/memory/memory.limit_in_bytes"):
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
                val = f.read().strip()
                cg_max_mb = int(val) / (1024 * 1024)
    except Exception:
        pass

    return {
        "py_rss": py_rss_mb,
        "total_rss": total_rss_mb,
        "children": child_count,
        "chromium_procs": chromium_count,
        "cgroup_current": cg_current_mb,
        "cgroup_max": cg_max_mb,
    }


def log_memory_stage(stage: str, session_id: str = "") -> float:
    """
    Log comprehensive process RSS, child process RSS, and container cgroup memory:
    [MEM] session=<id> stage=<stage> py_rss=<X>MB total_rss=<Y>MB children=<N> (chrom=<M>) cgroup=<C>MB/<Limit>MB
    """
    global _last_rss_mb
    stats = get_detailed_memory_stats()
    current = stats["py_rss"]
    sess_str = f"session={session_id} " if session_id else ""
    cg_str = f" cgroup={stats['cgroup_current']:.1f}MB/{stats['cgroup_max']:.0f}MB" if stats["cgroup_current"] > 0 else ""
    child_str = f" total_rss={stats['total_rss']:.1f}MB children={stats['children']} (chrom={stats['chromium_procs']})" if stats["children"] > 0 else ""
    logger.info(f"[MEM] {sess_str}stage={stage} py_rss={current:.1f}MB{child_str}{cg_str}")
    _last_rss_mb = current
    return current


def get_current_rss_mb() -> float:
    """Read the current process RSS in megabytes cross-platform."""
    return get_detailed_memory_stats()["py_rss"]


def trigger_garbage_collection(stage_name: str = "") -> float:
    """
    Explicitly trigger Python garbage collection and log before/after memory.
    """
    before = get_current_rss_mb()
    gc.collect()
    after = get_current_rss_mb()
    freed = before - after
    if freed > 1.0:
        logger.info(f"[MEMORY] GC ({stage_name}): freed {freed:.1f} MB (now {after:.1f} MB)")
    return after


def configure_low_memory_environment() -> None:
    """
    Configure thread limits and glibc memory arena settings for
    constrained Linux container environments (Render 512 MB plan).
    """
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    # Reduce glibc malloc arena fragmentation in Docker
    os.environ.setdefault("MALLOC_ARENA_MAX", "2")
