FROM python:3.9-slim
ARG workdir=/opt/bg-attack-plan
RUN apt update \
    && apt upgrade -y
RUN apt install -y curl telnet
RUN pip3 install --upgrade pip
RUN mkdir -p $workdir
COPY requirements.txt ${workdir}
RUN pip3 install -r ${workdir}/requirements.txt

COPY src/*.py $workdir
WORKDIR $workdir
CMD ["./main.py"]
