#!/usr/bin/env bash
# Run in an MSYS2 MINGW32 shell. Outputs are native 32-bit Windows executables.
set -euo pipefail

if [[ ${MSYSTEM:-} != MINGW32 ]]; then
    echo "Use an MSYS2 MINGW32 shell (the i686 compiler is required)." >&2
    exit 1
fi
if [[ $(gcc -dumpmachine) != i686-w64-mingw32 ]]; then
    echo "Expected i686-w64-mingw32 GCC on PATH." >&2
    exit 1
fi

cd "$(dirname "$0")/../src"
mkdir -p ../dist/windows
windres -I res res/quickbms.rc -O coff -o ../dist/windows/quickbms-res.o

# Preserve the old source's C dialect under current GCC. -fpermissive retains
# legacy implicit conversions that GCC 14+ otherwise treats as hard errors.
cflags='-m32 -s -O2 -msse2 -std=gnu17 -fpermissive -fstack-protector-all -fno-unit-at-a-time -fno-omit-frame-pointer -w'
cdefs='-DDISABLE_MCRYPT -DDISABLE_TOMCRYPT -DDISABLE_XMEM -DZSTD_DISABLE_ASM'
extras='libs/amiga/amiga.s libs/powzix/*.cpp extra/MemoryModule.c libs/libdeflate/lib/*.c libs/libdeflate/lib/x86/cpu_features.c ../dist/windows/quickbms-res.o'
libraries="-static -lstdc++ -lm -lpthread $(pkg-config --static --libs openssl) -lws2_32 -lwinmm -lcomdlg32 -lgdi32 -ladvapi32 -lshell32 -lcrypt32 -lbcrypt"

for executable in quickbms quickbms_4gb_files; do
    variant_flags=''
    if [[ $executable == quickbms_4gb_files ]]; then
        variant_flags='-DQUICKBMS64'
    fi
    # Reuse the Makefile's full codec list; avoid a second, drifting source list.
    make --no-print-directory -s print-args \
        EXE="../dist/windows/$executable.exe" \
        CFLAGS="$cflags $variant_flags $(pkg-config --cflags openssl) -Ilibs/libdeflate" \
        CDEFS="$cdefs" CLIBS="$libraries" EXTRA_TARGETS="$extras" \
        > "../dist/windows/$executable.rsp"
    gcc "@../dist/windows/$executable.rsp"
    # Record PE architecture and imports for the build log.
    objdump -f "../dist/windows/$executable.exe"
    objdump -p "../dist/windows/$executable.exe" | sed -n '/DLL Name:/p'
done
