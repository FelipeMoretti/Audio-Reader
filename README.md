# Audio Reader

Ferramenta de ditado por voz para Windows. Segure um atalho, fale, e o texto transcrito é digitado automaticamente no aplicativo ativo.

Inspirado no [Wispr Flow](https://wispr.com/flow). Usa o modelo Whisper da OpenAI via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) para transcrever localmente, sem depender de nuvem.

## Como Funciona

1. **Segure Ctrl+Alt** para iniciar a gravação
2. **Solte** para parar
3. O áudio é transcrito localmente pelo Whisper
4. O texto é colado automaticamente no aplicativo ativo (via clipboard + Ctrl+V)

Um indicador colorido aparece na tela durante a gravação (vermelho) e transcrição (laranja). O ícone na bandeja do sistema também muda de cor conforme o estado.

## Requisitos

- Windows 10/11
- Python 3.10+
- Microfone

## Instalação

```bash
git clone https://github.com/your-username/Audio-Reader.git
cd Audio-Reader
pip install -r requirements.txt
```

> **GPU:** Para aceleração via CUDA, instale a versão CUDA do `ctranslate2` e configure `device` como `"cuda"` nas configurações.

## Uso

```bash
python run.py
```

O app inicia na bandeja do sistema. Aguarde o modelo carregar (ícone cinza fica azul), depois segure Ctrl+Alt para gravar.

Clique com botão direito no ícone da bandeja para acessar **Configurações** ou **Sair**.

## Configuração

Salvas em `%APPDATA%\AudioReader\config.json`. Editáveis pela janela de configurações ou diretamente no arquivo.

| Opção | Padrão | Descrição |
|-------|--------|-----------|
| `model_size` | `"base"` | Modelo Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `device` | `"cpu"` | Dispositivo: `cpu` ou `cuda` |
| `compute_type` | `"int8"` | Quantização: `int8`, `float16`, `float32` |
| `language` | `null` | Código ISO 639-1 (`"pt"`, `"en"`) ou `null` para auto |
| `restore_clipboard` | `true` | Restaurar clipboard original após injeção |
| `vad_filter` | `true` | Filtrar segmentos sem fala |

> **Nota:** Alterar modelo, dispositivo ou tipo de computação exige reiniciar o app.

## Estrutura

```
Audio-Reader/
├── run.py                         # Ponto de entrada
├── requirements.txt
└── audio_reader/
    ├── app.py                     # Máquina de estados (orquestrador)
    ├── config.py                  # Gerenciamento de config (%APPDATA%)
    ├── recorder.py                # Gravação de áudio (sounddevice)
    ├── transcription.py           # Wrapper do Whisper (faster-whisper)
    ├── hotkey.py                  # Detecção de push-to-talk (keyboard)
    ├── injector.py                # Injeção de texto (clipboard + Ctrl+V)
    └── ui/
        ├── tray.py                # Ícone na bandeja (pystray)
        ├── overlay.py             # Indicador flutuante (tkinter)
        └── settings.py            # Janela de configurações (customtkinter)
```

## Dependências

[faster-whisper](https://github.com/SYSTRAN/faster-whisper) | [sounddevice](https://python-sounddevice.readthedocs.io/) | [numpy](https://numpy.org/) | [keyboard](https://github.com/boppreh/keyboard) | [pystray](https://github.com/moses-palmer/pystray) | [Pillow](https://python-pillow.org/) | [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | [pyperclip](https://github.com/asweigart/pyperclip)
