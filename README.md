# Mercedes F1 (OpenGL/Pygame)

Simulação simples de um carro de F1 (Mercedes W16) renderizado em OpenGL via Pygame. Inclui cena, pista infinita, DRS, animação das rodas e texturas básicas (nariz, pneus, logos e capa do motor).

## Requisitos
- Python 3.9+ instalado e no PATH
- Pip para instalar dependências
- Aceleração 3D disponível (GPU/driver OpenGL)
- (WSL/Linux) Servidor gráfico ativo (`$DISPLAY` definido) e biblioteca SDL disponível

<<<<<<< HEAD
## Instalação (Windows)
1. Instale o Python 3.10+ pelo [python.org](https://www.python.org/downloads/) marcando a opção “Add Python to PATH”.
2. No prompt (ou PowerShell), dentro da pasta do projeto:
   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install pygame PyOpenGL PyOpenGL_accelerate
   ```
   Se ocorrer “access violation” ao abrir a janela, teste removendo o acelerador:
   ```powershell
   python -m pip uninstall -y PyOpenGL_accelerate
   ```
3. Rodar o app:
   ```powershell
   python new_W16.py
   ```
=======
## Instalação rápida
```bash
# dentro da pasta do projeto
python3 -m venv .venv
Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install pygame PyOpenGL PyOpenGL_accelerate
```
>>>>>>> 4de986fd18d3edcfce442cd9f71835909fdbdb08

### Observação (WSL)
Requer servidor X (VcXsrv/Xming) ativo e variável `DISPLAY` setada.

## Controles
- `Espaço`: acelerar/retomar
- `Ctrl`: frear
- `D`: abrir/fechar DRS
- `Setas` ou `W/S`: mover a câmera (distância e pitch)
- `Esquerda/Direita`: girar a câmera
- `Esc`: sair

## Texturas e arquivos
- `nose_texture.png`: textura do nariz/asa dianteira
- `pneu_texture.jpg`: textura do pneu
- `logo_side.png`: logo aplicada nas laterais do corpo
- `engine_cover_atlas.png`: atlas aplicado na capa do motor
- `new_W16.py`: código principal (lógica, desenho e entrada)

Para trocar qualquer textura, substitua o arquivo mantendo o mesmo nome e rode novamente.

## Problemas comuns
- **Janela não abre no WSL**: faltando servidor X ou variável `DISPLAY`.
- **ImportError para pygame/OpenGL**: instale com `pip install pygame PyOpenGL PyOpenGL_accelerate` dentro do venv correto.
- **Desempenho baixo**: confirme se a renderização está usando a GPU e feche outros apps que usem GL.
