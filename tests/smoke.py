#!/usr/bin/env python3
"""Exercise a QuickBMS executable with generated, redistributable fixtures.

Usage: python3 tests/smoke.py /path/to/quickbms
       python3 tests/smoke.py quickbms --docker-image quickbms:ci
The same checks support quickbms and quickbms_4gb_files. No game assets,
network access, third-party Python packages, or installed BMS scripts are needed.
"""

import argparse
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import uuid
import zlib


SCRIPT = """\
idstring "QBSM"
endian little
get RAW_SIZE long
get PACKED_SIZE long
get UNPACKED_SIZE long
get XMEM_PACKED_SIZE long
get XMEM_UNPACKED_SIZE long
savepos RAW_OFFSET
log "raw payload.bin" RAW_OFFSET RAW_SIZE
math PACKED_OFFSET = RAW_OFFSET
math PACKED_OFFSET += RAW_SIZE
comtype zlib
clog "compressed payload.bin" PACKED_OFFSET PACKED_SIZE UNPACKED_SIZE
math XMEM_OFFSET = PACKED_OFFSET
math XMEM_OFFSET += PACKED_SIZE
comtype XMemDecompress
clog "xmem payload.bin" XMEM_OFFSET XMEM_PACKED_SIZE XMEM_UNPACKED_SIZE
"""


def run(executable, arguments, directory, timeout, docker_image=None):
    container_name = None
    if docker_image:
        container_name = f"quickbms-smoke-{uuid.uuid4().hex}"
        command = [
            "docker", "run", "--rm", "--name", container_name, "--network", "none",
            "--mount", f"type=bind,source={directory},target=/fixture",
            "--workdir", "/fixture",
        ]
        if sys.platform.startswith("linux"):
            command.extend(["--user", f"{os.getuid()}:{os.getgid()}"])
        command.extend(["--entrypoint", executable.name, docker_image])
        command.extend(
            f"/fixture/{argument.relative_to(directory).as_posix()}"
            if isinstance(argument, Path) else str(argument)
            for argument in arguments
        )
    else:
        command = [str(executable), *map(str, arguments)]
    try:
        result = subprocess.run(
            command,
            cwd=directory,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        if container_name:
            # Killing the Docker client does not stop its container.
            try:
                subprocess.run(
                    ["docker", "rm", "--force", container_name],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                print(f"Could not clean up timed-out container {container_name}", file=sys.stderr)
        output = (error.output or b"").decode("utf-8", errors="replace")
        raise RuntimeError(
            f"QuickBMS timed out after {timeout} seconds: {command!r}\n{output}"
        ) from error
    output = result.stdout.decode("utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(
            f"QuickBMS exited with {result.returncode}: {command!r}\n{output}"
        )
    return output


def verify_outputs(directory, expected, output):
    actual_names = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    }
    if actual_names != set(expected):
        raise RuntimeError(
            f"Unexpected extracted files: {sorted(actual_names)!r}; "
            f"expected {sorted(expected)!r}\n{output}"
        )
    for name, payload in expected.items():
        actual = (directory / name).read_bytes()
        if actual != payload:
            raise RuntimeError(
                f"Extracted bytes differ for {name!r}: got {len(actual)} bytes, "
                f"expected {len(payload)} bytes\n{output}"
            )


def smoke(executable, timeout, docker_image=None):
    raw = bytes(range(256)) * 4 + b"\x00Raw payload\r\n\xff"
    unpacked = b"QuickBMS zlib smoke fixture\x00\r\n" * 128 + bytes(range(255, -1, -1))
    packed = zlib.compress(unpacked)
    xmem_unpacked = bytes(range(32))
    # LZX stores bits in little-endian 16-bit words, most significant bit first:
    # no Intel transform (1 bit), uncompressed block (3), length (24), padding.
    lzx_header = (3 << 28) | (len(xmem_unpacked) << 4)
    lzx_block = (
        struct.pack("<HHIII", lzx_header >> 16, lzx_header & 0xFFFF, 1, 1, 1)
        + xmem_unpacked
    )
    # Xbox framing: marker, big-endian uncompressed and compressed block sizes.
    xmem_packed = b"\xff" + struct.pack(">HH", len(xmem_unpacked), len(lzx_block)) + lzx_block
    archive_bytes = (
        b"QBSM" + struct.pack(
            "<IIIII", len(raw), len(packed), len(unpacked),
            len(xmem_packed), len(xmem_unpacked),
        ) + raw + packed + xmem_packed
    )
    expected = {
        "raw payload.bin": raw,
        "compressed payload.bin": unpacked,
        "xmem payload.bin": xmem_unpacked,
    }

    # Spaces exercise argument passing as well as archive/output path handling.
    with tempfile.TemporaryDirectory(prefix="quickbms smoke ") as temporary:
        directory = Path(temporary)
        script = directory / "smoke script.bms"
        archive = directory / "sample archive.bin"
        listed = directory / "list only output"
        extracted = directory / "extracted output"
        script.write_text(SCRIPT, encoding="ascii")
        archive.write_bytes(archive_bytes)
        listed.mkdir()
        extracted.mkdir()

        output = run(
            executable,
            ["-R", "-Y", "-l", script, archive, listed],
            directory,
            timeout,
            docker_image,
        )
        if any(listed.rglob("*")):
            raise RuntimeError(f"List-only mode created output files\n{output}")
        for name in expected:
            if name not in output:
                raise RuntimeError(f"List-only output did not include {name!r}\n{output}")

        output = run(
            executable,
            ["-R", "-Y", "-o", script, archive, extracted],
            directory,
            timeout,
            docker_image,
        )
        verify_outputs(extracted, expected, output)
        if archive.read_bytes() != archive_bytes:
            raise RuntimeError("Reading/listing the archive changed its contents")

    target = f"{executable.name} in {docker_image}" if docker_image else executable.name
    print(f"PASS: {target}: list-only, Log, zlib/XMem LZX CLog, unchanged input")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path, help="executable path, or executable name with --docker-image")
    parser.add_argument("--docker-image", help="test this Docker image instead of a native executable")
    parser.add_argument("--timeout", type=int, default=30, help="seconds per invocation (default: 30)")
    arguments = parser.parse_args()
    if arguments.timeout <= 0:
        parser.error("--timeout must be positive")
    executable = arguments.executable
    if not arguments.docker_image:
        executable = executable.resolve()
        if not executable.is_file():
            parser.error(f"executable does not exist: {executable}")
    try:
        smoke(executable, arguments.timeout, arguments.docker_image)
    except (OSError, RuntimeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
