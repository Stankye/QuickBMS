# QuickBMS preservation archive

This repository preserves **QuickBMS 0.12.0** by Luigi Auriemma and a saved
collection of **2,745 QuickBMS scripts**. QuickBMS is a script-driven tool for
extracting and working with game archives and other binary formats.

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

The imported files retain their original bytes. Source archive paths are kept
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

The source archive includes the upstream [`src/Makefile`](src/Makefile). Its
default configuration targets a 32-bit build and requires the corresponding
compiler and libraries. This import has been checked for file integrity; it has
not been built, and the scripts have not been functionally tested.

## Credits and licensing

QuickBMS is by **Luigi Auriemma**. Its source headers specify **GNU GPL version 2
or later**; the supplied text is also preserved in
[`src/gpl-2.0.txt`](src/gpl-2.0.txt). Bundled libraries and individual scripts
retain their original author credits and license notices. Consult the applicable
files for their terms; this mirror does not replace or relicense them.
