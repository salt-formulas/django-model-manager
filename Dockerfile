FROM ubuntu:16.04
MAINTAINER Ales Komarek "ales.komarek@mirantis.com"
RUN apt-get -qq update
RUN apt-get install -y python-django git-core
RUN (cd /opt && git clone git@git.tcpcloud.eu:python-apps/devops-portal.git app)
EXPOSE 8000
CMD ["/opt/app/devops_portal/manage.py", "runserver", "0.0.0.0:8000"]