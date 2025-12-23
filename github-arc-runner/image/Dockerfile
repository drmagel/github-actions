FROM ghcr.io/actions/actions-runner:2.330.0
# https://github.com/actions/runner/pkgs/container/actions-runner/versions

ARG ARCH="dpkg --print-architecture"
ARG PYTHON312_VERSION=3.12.12
ARG PYTHON314_VERSION=3.14.1
ARG KUBECTL_VERSION=1.35.0
ARG HELM_VERSION=4.0.1
ARG ARGO_CD_VERSION=3.0.6

ENV HOME=/home/runner
ENV LBIN="${HOME}/.local/bin"
ENV PYENV_ROOT=${HOME}/.pyenv
ENV NVM_DIR=${HOME}/.nvm
ENV PATH=$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH

USER root
RUN add-apt-repository ppa:rmescandon/yq -y
RUN apt-get update
RUN apt-get install -y \
    software-properties-common \
    wget \
    jq \
    yq \
    vim \
    python3-launchpadlib \
    python3-pip \
    python3-openssl \
    libssl-dev

### kubernetes
RUN curl -k -s -S -o /usr/local/bin/kubectl -L https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/$(eval ${ARCH})/kubectl && \
    chmod +x /usr/local/bin/kubectl
RUN curl -k -s -S -o /usr/local/bin/kubectl-argo-rollouts -L https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-$(eval ${ARCH}) && \
    chmod +x /usr/local/bin/kubectl-argo-rollouts
RUN curl -k -s -S -o /usr/local/bin/argocd -L https://github.com/argoproj/argo-cd/releases/download/v${ARGO_CD_VERSION}/argocd-linux-$(eval ${ARCH}) && \
    chmod +x /usr/local/bin/argocd
RUN curl -k -s -S -L https://get.helm.sh/helm-v${HELM_VERSION:?}-linux-$(eval ${ARCH}).tar.gz |\
    tar xvzf - linux-$(eval ${ARCH})/helm && \
    install -m 755 linux-$(eval ${ARCH})/helm /usr/local/bin/helm

USER runner
WORKDIR ${HOME}

### pyenv
ENV PYENV_INSTALLER_FORCE_BINARY=1
RUN curl -k -s -S -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash \
    && printf '\neval "$(pyenv init -)"\n' >> ${HOME}/.bashrc
## python3.12 (default)
RUN pyenv install ${PYTHON312_VERSION} \
    && pyenv global ${PYTHON312_VERSION}
COPY --chown=runner requirements-312.txt .
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements-312.txt
RUN rm -f requirements-312.txt
## python3.14
RUN pyenv install ${PYTHON314_VERSION} \
    && pyenv virtualenv ${PYTHON314_VERSION} 3.14
COPY --chown=runner requirements-314.txt .
RUN eval "$(pyenv init -)" \
    && pyenv activate 3.14 \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements-314.txt \
    && pyenv deactivate
RUN rm -f requirements-314.txt

### nvm
RUN curl -k -s -S -L https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
##+ node 20
RUN . ${NVM_DIR}/nvm.sh \
    && nvm install 20
##+ node 18 (default)
RUN . ${NVM_DIR}/nvm.sh \
    && nvm install 18 \
    && nvm alias default 18

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/home/runner/run.sh"]
