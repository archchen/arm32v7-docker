FROM alpine
MAINTAINER LaoGao <noreply@phpgao.com>


ARG SS_VER=3.0.8
ARG SS_URL=https://github.com/shadowsocks/shadowsocks-libev/releases/download/v$SS_VER/shadowsocks-libev-$SS_VER.tar.gz
ARG KCP_VER=20170904
ARG KCP_URL=https://github.com/xtaci/kcptun/releases/download/v$KCP_VER/kcptun-linux-amd64-$KCP_VER.tar.gz


RUN set -ex && \
    apk add --no-cache --virtual .build-deps \
                                autoconf \
                                build-base \
                                curl \
                                libev-dev \
                                libtool \
                                linux-headers \
                                udns-dev \
                                libsodium-dev \
                                mbedtls-dev \
                                pcre-dev \
                                tar \
                                tzdata \
                                udns-dev && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    cd /tmp && \
    curl -sSL $KCP_URL | tar xz server_linux_amd64 && \
    mv server_linux_amd64 /usr/bin/ && \
    curl -sSL $SS_URL | tar xz --strip 1 && \
    ./configure --prefix=/usr --disable-documentation && \
    make install && \
    cd .. && \
    runDeps="$( \
        scanelf --needed --nobanner /usr/bin/ss-* \
            | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
            | xargs -r apk info --installed \
            | sort -u \
    )" && \
    apk add --no-cache --virtual .run-deps $runDeps && \
    apk del .build-deps && \
    
    rm -rf /tmp/*


ENV SERVER_PORT=19980 \
    KCP_LISTEN=4000 \
    SS_ARG='-m chacha220 -k this@mysite! -u -d 8.8.8.8 -d 8.8.4.4 --fast-open'  \
    KCP_ARG='--key this@mysite! --mode fast2 --crypt salsa20 --mtu 1350 --nocomp --dscp 46 '

EXPOSE $SERVER_PORT/tcp $SERVER_PORT/udp
EXPOSE $KCP_LISTEN/udp

CMD ss-server -p $SERVER_PORT SS_ARG -a nobody -f /tmp/ss.pid\
                && server_linux_amd64 -t "127.0.0.1:$SERVER_PORT" \
                 -l ":$KCP_LISTEN" \
                 KCP_ARG
