"""Portable direct process launch and Windows descendant lifetime control."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def process_is_alive(pid):
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True
    # os.kill(pid, 0) terminates Windows processes; query a handle instead.
    import ctypes
    from ctypes import wintypes
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    api.OpenProcess.restype = wintypes.HANDLE
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    handle = api.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
    if not handle:
        error = ctypes.get_last_error()
        if error == 87:  # ERROR_INVALID_PARAMETER: no process with this PID
            return False
        if error == 5:  # Access denied does not establish a dead process.
            return True
        raise ctypes.WinError(error)
    try:
        status = api.WaitForSingleObject(handle, 0)
        if status == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        return status == 0x00000102  # WAIT_TIMEOUT
    finally:
        api.CloseHandle(handle)


def executable_argv(argv):
    """Windows does not execute Python shebang scripts through CreateProcess."""
    result = list(argv)
    if os.name != "nt" or not result:
        return result
    path = Path(result[0])
    if path.suffix.lower() == ".py":
        return [sys.executable, *result]
    if path.is_file() and path.suffix.lower() not in {".exe", ".com", ".bat", ".cmd"}:
        with path.open("rb") as handle:
            first = handle.readline(1024).lower()
        if first.startswith(b"#!") and b"python" in first:
            return [sys.executable, *result]
    return result


def attach_windows_job(process):
    """Keep descendants in a kill-on-close Job, including after leader exit."""
    if os.name != "nt":
        return
    import ctypes
    from ctypes import wintypes

    class BASIC_LIMIT(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong),
                    ("PerJobUserTimeLimit", ctypes.c_longlong),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in
                    ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                     "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class EXTENDED_LIMIT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC_LIMIT), ("IoInfo", IO_COUNTERS),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    api.CreateJobObjectW.restype = wintypes.HANDLE
    api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    api.SetInformationJobObject.restype = wintypes.BOOL
    api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    api.AssignProcessToJobObject.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    job = api.CreateJobObjectW(None, None)
    if not job:
        process.kill()
        process.wait(timeout=5)
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        limits = EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not api.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not api.AssignProcessToJobObject(job, int(process._handle)):
            error = ctypes.get_last_error()
            if process.poll() is None:
                raise ctypes.WinError(error)
            api.CloseHandle(job)
            return
        process._codex_job = (api, job)
    except BaseException:
        api.CloseHandle(job)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        raise


def close_windows_job(process):
    job = getattr(process, "_codex_job", None)
    if job is not None:
        process._codex_job = None
        api, handle = job
        api.CloseHandle(handle)


def stop_windows_tree(process):
    if os.name != "nt":
        return False
    job = getattr(process, "_codex_job", None)
    close_windows_job(process)
    if job is None and process.poll() is None:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=5, check=False)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    return True
