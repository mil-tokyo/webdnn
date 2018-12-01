FROM ubuntu:bionic

RUN apt update && apt install -y python3 python3-pip wget git && ln -s python3 /usr/bin/python
RUN /bin/bash -c 'source $HOME/.bashrc ;\
cd /usr/local ;\
git clone https://github.com/juj/emsdk.git ;\
cd emsdk ;\
./emsdk install latest ;\
./emsdk activate latest ;\
echo "source /usr/local/emsdk/emsdk_env.sh" >> $HOME/.bashrc ;\
cd /usr/local ;\
wget -O - "http://bitbucket.org/eigen/eigen/get/3.3.3.tar.bz2" | tar jxf - ;\
ln -s /usr/local/eigen-eigen-67e894c6cd8f/Eigen /usr/local/emsdk/emscripten/*/system/local/include'
RUN /bin/bash -c 'source $HOME/.bashrc ; pip3 install webdnn'
CMD /bin/bash
