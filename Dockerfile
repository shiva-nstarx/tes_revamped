FROM python:3.11-slim

WORKDIR /usr/src/app
COPY . .

ENV STATE_PATH /usr/src/app/pz-data
RUN mkdir -p $STATE_PATH

## Install required dependencies
RUN apt-get update && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common && \
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    curl https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | tee /usr/share/keyrings/helm.gpg > /dev/null && \
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list && \
    apt-get update && \
    apt-get install -y kubectl terraform jq helm awscli unzip

# Install kustomize
RUN curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash && \
    mv ./kustomize /usr/bin/

# Unzip the kubeflow directory
RUN unzip _ts-kubeflow.zip

# Install required Python packages
RUN pip install --quiet --no-cache-dir -U pip setuptools && \
    pip install --quiet --no-cache-dir -r requirements.txt

# Remove the zip file
RUN rm _ts-kubeflow.zip

EXPOSE 8000

CMD ["python", "api.py"]