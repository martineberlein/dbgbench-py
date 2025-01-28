#!/usr/bin/env bash
set -e

apt-get update
apt-get --yes --force-yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" upgrade

pushd /root/Desktop/
# install openssl
wget --no-check-certificate https://www.openssl.org/source/openssl-1.1.1g.tar.gz
tar -xzvf openssl-1.1.1g.tar.gz
pushd openssl-1.1.1g
./config
make install
if [ ! -e /usr/bin/openssl ]; then
  ln -sf /usr/local/ssl/bin/openssl /usr/bin/openssl
fi
if [ ! -e /usr/lib/libcrypto.so.1.1 ]; then
  ln -s /usr/local/lib/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1
fi
if [ ! -e /usr/lib/libssl.so.1.1 ]; then
  ln -s /usr/local/lib/libssl.so.1.1 /usr/lib/libssl.so.1.1
fi
popd

# install python
apt-get install -y --no-install-recommends libffi-dev zlib1g zlib1g-dev uuid-dev libbz2-dev liblzma-dev
wget --no-check-certificate https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
tar xf Python-3.8.2.tgz
cd Python-3.8.2
# rewrite setup file (activate non-standard ssl path)
sed -i '/ _socket socketmodule.c /s/^#//' Modules/Setup
sed -i '/SSL=/s/^#//' Modules/Setup
sed -i '/_ssl/s/^#//' Modules/Setup
sed -i '/-DUSE_SSL/s/^#//' Modules/Setup
sed -i '/-lssl/s/^#//' Modules/Setup

# does not compile with optimizations: https://groups.google.com/forum/#!topic/comp.lang.python/npv-wzmytzo
./configure --with-openssl=/usr/local/ssl
make
make install
popd

python3 -m pip install -U pip
python3 -m pip install numpy
python3 -m pip install pandas

mkdir -p /root/Desktop/alhazen_scripts/
mkdir -p /root/Desktop/alhazen_scripts/alhazen/
mkdir -p /root/Desktop/alhazen_samples/

printf '#!/bin/bash\nwhile [ 1 ]; do\n/bin/bash\ndone\n' > /startup.sh
