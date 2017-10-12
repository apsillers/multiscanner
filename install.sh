#!/bin/bash
#This script attempts to install the required packages for MultiScanner and its modules

CWD=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#Install requirements for Redhat derivatives
if [ -e /etc/redhat-release ]; then
  yum install -y epel-release
  yum install -y autoconf automake curl gcc libffi-devel libtool make python-devel ssdeep-devel tar git unzip openssl-devel file-devel
fi

#Install requirements for Debian derivatives
if [ -e /etc/debian_version ]; then
  apt-get update
  apt-get install -y build-essential curl dh-autoreconf gcc libffi-dev libfuzzy-dev python-dev git libssl-dev unzip libmagic-dev
fi

#Install requirements for Python
curl -k https://bootstrap.pypa.io/get-pip.py | python
pip install --upgrade -r $DIR/requirements.txt


#Code to compile and install yara
YARA_VER=3.5.0
read -p "Compile yara $YARA_VER? <y/N> " prompt
if [[ $prompt == "y" ]]; then
  #Because apparently the one in the repos does not work...
  curl -L https://github.com/akheron/jansson/archive/v2.10.tar.gz | tar -xz
  cd jansson-2.10
  autoreconf -fi
  ./configure --prefix=/usr
  make install
  cd ..
  rm -rf jansson-2.10
  ln -s /usr/lib/libjansson.so.4 /lib64/libjansson.so.4
  #We get yara-python as well
  git clone -b v$YARA_VER https://github.com/VirusTotal/yara-python.git
  cd yara-python
  git clone -b v$YARA_VER https://github.com/VirusTotal/yara.git
  cd yara
  ./bootstrap.sh
  ./configure --prefix=/usr --enable-magic --enable-cuckoo --with-crypto
  make && make install
  cd ../
  python setup.py build --dynamic-linking
  python setup.py install
  cd ../
  rm -rf yara-python
  ln -s /usr/lib/libyara.so.3 /lib64/libyara.so.3
fi

read -p "Download TrID? <y/N> " prompt
if [[ $prompt == "y" ]]; then
  mkdir -p /opt/trid
  cd /opt/trid
  curl -f --retry 3 http://mark0.net/download/trid_linux_64.zip > trid.zip
  if [[ $? -ne 0 ]]; then
    echo -e "\nFAILED\nTrying alternative mirror ..."
    curl -f --retry 3 https://web.archive.org/web/20170711171339/http://mark0.net/download/trid_linux_64.zip > trid.zip
  fi
  unzip trid.zip
  rm -f trid.zip
  curl -f --retry 3 http://mark0.net/download/triddefs.zip > triddefs.zip
  if [[ $? -ne 0 ]]; then
    echo -e "\nFAILED\nTrying alternative mirror ..."
    curl -f --retry 3 https://web.archive.org/web/20170827141200/http://mark0.net/download/triddefs.zip > triddefs.zip
  fi
  unzip triddefs.zip
  rm -f triddefs.zip
  chmod 755 trid
  cd $CWD
fi

read -p "Download FLOSS? <y/N> " prompt
if [[ $prompt == "y" ]]; then
  curl -f --retry 3 https://s3.amazonaws.com/build-artifacts.floss.flare.fireeye.com/travis/linux/dist/floss > /opt/floss
  chmod 755 /opt/floss
fi

read -p "Download yararules.com signatures? <y/N> " prompt
if [[ $prompt == "y" ]]; then
  git clone --depth 1 https://github.com/Yara-Rules/rules.git $DIR/etc/yarasigs/Yara-Rules
  echo You can update these signatures by running cd $DIR/etc/yarasigs/Yara-Rules \&\& git pull
fi

read -p "Download SupportIntelligence's Icewater yara signatures? <y/N> " prompt
if [[ $prompt == "y" ]]; then
  git clone --depth 1 https://github.com/SupportIntelligence/Icewater.git $DIR/etc/yarasigs/Icewater
  echo You can update these signatures by running cd $DIR/etc/yarasigs/Icewater \&\& git pull
fi

read -p "Would you like to install MultiScanner as a system library? <y/N> " prompt
if [[ $prompt == "y" ]]; then
  pip install -e $DIR
  echo "Make sure users have access to $DIR"
fi
