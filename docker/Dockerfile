FROM nvidia/cuda:12.4.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys sudo https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

# Install Python 3.11 from deadsnakes PPA
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
    git gcc python3.11 python3.11-dev python3.11-venv python3.11-distutils zlib1g-dev libjpeg62-dev curl ca-certificates tree \
    libglib2.0-0 libsm6 libice6 libxrender1 libxext6 libx11-6 libgl1-mesa-dev libtbb-dev libgraphviz-dev && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Set Python 3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

RUN apt-get update -y && apt-get install -y python3-tk sudo libxkbcommon-x11-0
ENV LC_ALL C

# Upgrade pip
RUN python3.11 -m pip install --upgrade pip

# remove system blinker
RUN apt-get update && \
    apt-get remove -y python3-blinker && \
    rm -rf /var/lib/apt/lists/*

# Install PyTorch first (CUDA 12.4 version)
RUN pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 --index-url https://download.pytorch.org/whl/cu124

# Install base requirements
RUN pip install \
    transformers==4.51.3 \
    python-box \
    einops \
    omegaconf \
    pytorch_lightning \
    lightning \
    addict \
    timm \
    fast-simplification \
    trimesh \
    open3d \
    pyrender \
    huggingface_hub \
    wandb \
    psutil \
    ninja

# Install bpy from Blender PyPI
RUN pip install --extra-index-url https://download.blender.org/pypi/ bpy==4.2

# Install torch_scatter and torch_cluster (CUDA 12.4)
RUN pip install torch_scatter torch_cluster -f https://data.pyg.org/whl/torch-2.6.0+cu124.html --no-cache-dir --no-build-isolation

# Install spconv (cu121 version works with CUDA 12.4 due to backward compatibility)
RUN pip install spconv-cu121

# Install flash-attn (requires --no-build-isolation and must be after torch)
RUN pip install flash-attn==2.7.2.post1 --no-build-isolation

# Install numpy 1.26.4 (downgrade)
RUN pip install numpy==1.26.4 

# Add a user that UID:GID will be updated by vscode
ARG USERNAME=developer
ARG GROUPNAME=developer
ARG UID=1000
ARG GID=1000
ARG PASSWORD=developer
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $USERNAME
ENV HOME /home/developer
