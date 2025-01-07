# Galeria PicBrand

**Galeria PicBrand** é uma aplicação multifuncional que combina monitoramento, edição, upload e impressão de imagens em um único sistema. Foi desenvolvida em Python com uma interface gráfica amigável, permitindo que usuários gerenciem imagens de forma eficiente, integrada com o Google Drive e dispositivos de impressão.

## Funcionalidades

- **Monitoramento de Imagens**:
  - Monitoramento automático de pastas para detectar novas imagens.
  - Aplicação de efeitos visuais como Blur, Grayscale, Contour, entre outros.

- **Captura de Imagens com Câmera**:
  - Seleção de câmera disponível no sistema.
  - Captura de imagens com temporizador e salvamento em pasta configurável.

- **Upload para o Google Drive**:
  - Upload direto de imagens processadas para uma conta do Google Drive autenticada.

- **Impressão de Imagens**:
  - Integração com impressoras disponíveis no sistema.
  - Impressão da última imagem processada diretamente pelo aplicativo.

## Tecnologias Utilizadas

- **Interface Gráfica**:
  - Tkinter para criação da interface intuitiva.

- **Processamento de Imagens**:
  - `Pillow` para aplicação de efeitos e manipulação de imagens.
  - `opencv-python` para captura e visualização da câmera.

- **Monitoramento de Arquivos**:
  - `watchdog` para monitorar pastas em tempo real.

- **Google Drive API**:
  - `PyDrive` para upload e integração com o Google Drive.

- **Integração com Impressoras**:
  - `pywin32` para acesso a impressoras no Windows.

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/galeria-picbrand.git


## Como Usar
Monitoramento de Imagens:

1.Na aba "Monitoramento", selecione uma pasta para monitoramento e aplique efeitos às imagens detectadas.
Captura de Imagens:

2.Na aba "Câmera", selecione uma câmera e capture imagens que serão adicionadas à lista de processamento.
Upload para o Google Drive:

3.Na aba "Upload", faça upload das imagens processadas para o Google Drive.
Impressão de Imagens:

4.Na aba "Impressão", selecione uma impressora e imprima a última imagem processada.

## Dependências 
As dependências estão listadas no arquivo requirements.txt:

-**plaintext**:
-**Copiar código**
**pillow**
**opencv-python**
**watchdog**
**pywin32**
**pydrive**

## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença
Este projeto está licenciado sob a MIT License. Consulte o arquivo LICENSE para mais informações.

Desenvolvido com dedicação pela equipe da PicBrand. 🌟
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
