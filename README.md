# QuickBMS

This repository preserves **QuickBMS 0.12.0** by Luigi Auriemma and a saved
collection of **2,745 QuickBMS scripts**. QuickBMS is a script-driven tool for
extracting and working with game archives and other binary formats.

The untouched import is tagged [`v0.12.0`](https://github.com/Stankye/QuickBMS/tree/v0.12.0).
Subsequent commits add build support and provide a starting point for this
fork's 0.13 work; they are not a new upstream release.

## Why this copy exists

The original QuickBMS site could no longer be reached when these local backups
were prepared for this repository. On **October 6, 2026**, checks of the
[original QuickBMS homepage](https://aluigi.altervista.org/quickbms.htm) and
[source download](https://aluigi.altervista.org/papers/quickbms-src-0.12.0.zip)
through the web retrieval service returned **HTTP 403 Forbidden**.

This archive keeps the saved source and scripts available independently of the
original site. Those responses document an access failure from that service;
they do not establish that the site has permanently shut down or is inaccessible
to everyone. The cause and duration of the problem are unknown.

This is an unofficial preservation copy, with credit to Luigi Auriemma and the
original contributors. It is a snapshot of the supplied backups, not a claim to
contain the latest release or every script ever published.

## Contents

| Path | Contents |
| --- | --- |
| [`src/`](src/) | 4,327 files from the QuickBMS 0.12.0 source archive, including bundled libraries, build files, and license notices. |
| [`scripts/`](scripts/) | 2,745 `.bms` files from the saved script collection. |
| [`LICENSE`](LICENSE) | The repository's existing GNU GPL version 2 license text. |

At `v0.12.0`, the imported files retain their original bytes. Source archive paths are kept
under `src/`; the flat script collection is placed under `scripts/`. Git does
not track the source ZIP's empty directory entries. The ZIP containers themselves
are not duplicated in the repository.

## Provenance and checksums

The import was made on **October 6, 2026** from these locally saved ZIP files.
Their original download dates are unknown; the import date is not their release
date. The filenames below are the exact supplied backup filenames.

| Archive | Size (bytes) | Extracted files |
| --- | ---: | ---: |
| `quickbms-src-0.12.0(1).zip` | 16,347,106 | 4,327 |
| `quickbms_scripts(1).zip` | 2,458,255 | 2,745 |

SHA-256 of the original ZIP files:

```text
e96794af8369fdcb6dd4744e126cc82bda22329153359c756a4c70b44fd6b328  quickbms-src-0.12.0(1).zip
1dc4bb68dc330aa8623f673c5b0e326cb330696ff2b90f4719590c1bb5b304bd  quickbms_scripts(1).zip
```

## Using the snapshot

With a compatible QuickBMS executable, select the script for the particular
archive format, the input archive, and an output directory. Typical usage is:

```text
quickbms scripts/<matching-script>.bms <input-archive> <output-directory>
```

## Build and run with Docker

The [`Dockerfile`](Dockerfile) builds from the checked-in source using Debian
bookworm, GCC 12, and 32-bit OpenSSL 3 libraries. It does not download QuickBMS
from the unavailable site. Use a Linux Docker engine on an x86-64 host:

```sh
docker build --platform linux/amd64 -t quickbms:local .
docker run --rm quickbms:local --version
docker run --rm --entrypoint quickbms_4gb_files quickbms:local --version
```

Both executables are **32-bit x86 Linux binaries**. `quickbms_4gb_files` enables
`QUICKBMS64` for wider script integers/file offsets; it is not a native 64-bit
port. Native ARM and Windows builds are not covered by this setup.

The image includes the saved scripts in `/opt/quickbms/scripts`. Mount a working
folder at `/data`, then select the script, input, and output paths, for example:

```sh
docker run --rm --network none --mount "type=bind,src=$(pwd),dst=/data" \
  quickbms:local /opt/quickbms/scripts/zip.bms /data/input.zip /data/output
```

In PowerShell, replace `$(pwd)` with `${PWD}` and put the command on one line.
On Linux, add `--user "$(id -u):$(id -g)"` before the image name to create output
with your own user ID. Mount a folder containing your input, rather than the
whole source checkout.

To export the binaries without the runtime image:

```sh
docker build --platform linux/amd64 --target binaries --output dist .
```

Exported binaries require the 32-bit glibc, libstdc++, and OpenSSL 3 runtime libraries;
the container supplies these dependencies. These are not static executables.
The upstream Makefile still disables the optional mcrypt and tomcrypt backends.
The export and image also include `quickbms-source.tar.gz`, containing the
corresponding source and original license notices. In the image it is under
`/usr/share/doc/quickbms/`.

## Automated builds and checks

[`Linux container build`](.github/workflows/build.yml) builds both variants and
the runtime image on pushes and pull requests. Generated fixtures exercise
list-only mode, byte-exact `Log` extraction, zlib `CLog` decompression, paths with
spaces, and unchanged input. The same checks run inside the final image without
network access. They are smoke tests, not coverage of every bundled codec or
game script.

Successful runs upload `quickbms-linux-x86.tar.gz` (both executables, source,
and notices), checksums, and `quickbms-container.tar.gz` as a GitHub Actions
artifact, retained for 14 days. Extract the native bundle with
`tar -xzf quickbms-linux-x86.tar.gz` to retain executable permissions.
Load the downloaded image with `docker load -i quickbms-container.tar.gz`; its
image name is `quickbms:ci`. No container registry publication is configured.

## Build research and compatibility changes

Existing work provides useful starting points:

- [9001/lxc's source-built container](https://github.com/9001/lxc/blob/hovudstraum/static-quickbms/Dockerfile)
  demonstrates a 32-bit build, but is marked unmaintained and fetches the upstream
  ZIP. This setup builds the preserved source instead.
- [Canar's modern GCC fork](https://github.com/Canar/quickbms) and the
  [upstream Linux build discussion](https://github.com/LittleBigBug/QuickBMS/issues/5)
  identify missing x86 sources and toolchain compatibility problems.
- [wilson0x4d's fork](https://github.com/wilson0x4d/quickbms) has a parallel
  LLVM-based 64-bit build, with different compatibility tradeoffs.

This build adds the missing LZMA CPU detection source and enables the existing
Amiga/Kraken x86 sources when building on x86-64. It separates the input source
filename from the output name for the two executable variants. With OpenSSL 3,
the removed SSLv23 RSA padding attempt is skipped; the remaining attempts keep
their original order. Headers that still define it retain the original attempt.

Small follow-ups for 0.13 are reliable Makefile install/clean targets, graceful
handling of malformed update pages, and regressions for reported script-string
matching bugs. The binary version remains 0.12.0 until release work begins.

## Credits and licensing

QuickBMS is by **Luigi Auriemma**. Its source headers specify **GNU GPL version 2
or later**; the supplied text is also preserved in
[`src/gpl-2.0.txt`](src/gpl-2.0.txt). Bundled libraries and individual scripts
retain their original author credits and license notices. Consult the applicable
files for their terms; this mirror does not replace or relicense them.
