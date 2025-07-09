FROM nvidia/cuda:11.8.0-base-ubuntu22.04

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    git \
    python3-pip \
    python3-venv \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Клонирование ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /app/ComfyUI

# Установка Python-зависимостей
RUN pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir -r requirements.txt

# Копирование конфигов и моделей
COPY sd_server/config/ /app/ComfyUI/
COPY sd_server/models/ /app/models/

# Создание симлинков для моделей
RUN mkdir -p /app/ComfyUI/models/checkpoints \
    && mkdir -p /app/ComfyUI/models/loras \
    && ln -s /app/models/checkpoints /app/ComfyUI/models/checkpoints \
    && ln -s /app/models/loras /app/ComfyUI/models/loras

VOLUME /app/models /app/ComfyUI/output

EXPOSE 8188

CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]