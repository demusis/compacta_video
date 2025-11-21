# Compressor de Vídeo

Esta é uma aplicação web simples para comprimir arquivos de vídeo. O backend é construído com Python e Flask, e utiliza o FFmpeg para o processamento de vídeo.

## Funcionalidades

- Upload de arquivos de vídeo.
- Definição do tamanho alvo da compressão através de um controle deslizante (slider).
- Opções de otimização:
    - Apenas comprimir.
    - Comprimir e reduzir a taxa de quadros.
    - Comprimir e reduzir a resolução.
- Feedback de progresso durante o upload e processamento.
- Download automático do vídeo comprimido.

## Tecnologias Utilizadas

- **Backend:** Python, Flask
- **Processamento de Vídeo:** FFmpeg (através da biblioteca `ffmpeg-python`)
- **Frontend:** HTML, CSS, JavaScript

## Como Executar Localmente

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/demusis/compacta_video.git
    cd compacta_video
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    > **Nota:** Você precisa ter o **FFmpeg** instalado no seu sistema para que a aplicação funcione. Consulte a [documentação oficial do FFmpeg](https://ffmpeg.org/download.html) para instruções de instalação adequadas ao seu sistema operacional.

4.  **Execute a aplicação:**
    ```bash
    python main.py
    ```

5.  Abra seu navegador e acesse `http://127.0.0.1:80` (ou a porta que for indicada no terminal).

##  Como Usar

1.  Acesse a página principal da aplicação.
2.  Clique em "Selecione o arquivo de vídeo" para escolher o vídeo que deseja comprimir.
3.  Ajuste o controle deslizante para definir o percentual de compressão desejado. O tamanho final estimado será exibido.
4.  (Opcional) Escolha um tipo de otimização diferente no menu suspenso.
5.  Clique no botão "Comprimir Vídeo".
6.  Aguarde o processo de upload e compressão. O arquivo final será baixado automaticamente pelo seu navegador.
