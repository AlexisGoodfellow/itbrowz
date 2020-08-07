# This is the base docker-image for itbrowz
FROM centos:latest

USER root

# Grab dependencies
RUN yum -y groupinstall "Development Tools"
RUN yum -y install zlib-devel bzip2 bzip2-devel readline-devel sqlite \
sqlite-devel openssl-devel xz xz-devel libffi-devel \
&& yum clean all && rm -rf /var/cache/yum

# Updates to glibc destroy the localedef, so we fix it by hand
# RUN localedef -i en_US -f UTF-8 en_US.UTF-8

RUN curl -s https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz | tar -xvzf -

# Build Python from source and symlink 3 -> 2
# No need to worry about virtual environments this way
WORKDIR Python-3.8.5

RUN ./configure --enable-loadable-sqlite-extensions --enable-optimizations && make install
RUN ln -fs /usr/local/bin/python3 /usr/local/bin/python
RUN ln -fs /usr/local/bin/pip3 /usr/local/bin/pip
RUN pip install --upgrade pip setuptools wheel

WORKDIR /app

COPY . .

RUN pip install -r requirements.lock -r requirements-test.txt
