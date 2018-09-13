FROM debian:jessie
MAINTAINER Ales Komarek "akomarek@mirantis.com"

RUN apt-get -qq update && apt-get install -y python-django git-core

RUN (cd /opt && git config --global http.sslVerify false && git clone https://git.tcpcloud.eu/python-apps/devops-portal.git app && chmod +x /opt/app/manage.py)

EXPOSE 8000

CMD ["/opt/app/manage.py", "runserver", "0.0.0.0:8000"]
