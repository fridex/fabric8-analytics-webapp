FROM registry.centos.org/centos/centos:7
MAINTAINER Fridolin Pokorny <fridolin@redhat.com>

ENV LANG=en_US.UTF-8 \
    F8A_WORKER_VERSION=78fd5f3

RUN useradd coreapi

RUN yum install -y epel-release git gcc && \
    yum install -y python34-devel python34-pip && \
    yum clean all

COPY ./ /tmp/webapp_install/
RUN pushd /tmp/webapp_install &&\
  pip3 install . &&\
  pip3 install git+https://github.com/fabric8-analytics/fabric8-analytics-worker.git@${F8A_WORKER_VERSION} &&\
  popd &&\
  rm -rf /tmp/jobs_install

COPY hack/run_webapp.sh /usr/bin/

USER coreapi
CMD ["/usr/bin/run_webapp.sh"]
