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


def get_current_rss_mb() -> float:
    """Read the current process RSS in megabytes cross-platform."""
    try:
        # Fast direct read on Linux (Docker / Render container)
        if os.path.exists("/proc/self/statm"):
            with open("/proc/self/statm", "r") as f:
                fields = f.read().split()
                # 2nd field is resident set size in pages
                page_size_kb = os.sysconf("SC_PAGE_SIZE") / 1024.0
                return (int(fields[1]) * page_size_kb) / 1024.0
        # macOS / BSD fallback via ps
        out = subprocess.check_output(["ps", "-o", "rss=", "-p", str(os.getpid())])
        return int(out.strip()) / 1024.0
    except Exception:
        return 0.0


def log_memory_stage(stage: str) -> float:
    """
    Log current RSS and delta from the previous stage in standard format:
    [MEMORY] <stage>: <RSS> MB (<delta> MB)
    """
    global _last_rss_mb
    current = get_current_rss_mb()
    if _last_rss_mb > 0.0:
        delta = current - _last_rss_mb
        delta_str = f"(+{delta:.1f} MB)" if delta >= 0 else f"({delta:.1f} MB)"
    else:
        delta_str = "(initial)"
    _last_rss_mb = current
    logger.info(f"[MEMORY] {stage}: {current:.1f} MB {delta_str}")
    return current


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
