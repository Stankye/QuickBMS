# syntax=docker/dockerfile:1

# Keep the upstream 32-bit ABI, even on an amd64 build host.
FROM debian:bookworm-slim AS build-base
RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc g++ gcc-multilib g++-multilib make libssl-dev:i386 python3 file \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ src/
COPY tests/smoke.py tests/smoke.py

FROM build-base AS standard
RUN make -C src \
    && file src/quickbms \
    && src/quickbms --version \
    && python3 tests/smoke.py src/quickbms

FROM build-base AS large-files
# QUICKBMS64 widens script integers/file offsets; this is still an x86 binary.
RUN make -C src EXE=quickbms_4gb_files CC="gcc -DQUICKBMS64" \
    && file src/quickbms_4gb_files \
    && src/quickbms_4gb_files --version \
    && python3 tests/smoke.py src/quickbms_4gb_files

# Include corresponding source and all original notices with binary distributions.
FROM build-base AS source-archive
COPY Dockerfile LICENSE README.md ./
COPY scripts/ scripts/
COPY tools/ tools/
RUN tar -czf /quickbms-source.tar.gz src scripts tests tools Dockerfile LICENSE README.md

# Export just the tested Linux binaries: docker build --target binaries --output dist .
FROM scratch AS binaries
COPY --from=standard /build/src/quickbms /quickbms
COPY --from=large-files /build/src/quickbms_4gb_files /quickbms_4gb_files
COPY --from=source-archive /quickbms-source.tar.gz /quickbms-source.tar.gz

FROM debian:bookworm-slim AS runtime
RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       libc6:i386 libstdc++6:i386 libssl3:i386 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=standard /build/src/quickbms /usr/local/bin/quickbms
COPY --from=large-files /build/src/quickbms_4gb_files /usr/local/bin/quickbms_4gb_files
COPY --from=source-archive /quickbms-source.tar.gz /usr/share/doc/quickbms/quickbms-source.tar.gz
COPY scripts/ /opt/quickbms/scripts/
COPY LICENSE /usr/share/doc/quickbms/LICENSE
COPY README.md /usr/share/doc/quickbms/README.md
WORKDIR /data
ENTRYPOINT ["quickbms"]
CMD ["--help"]
