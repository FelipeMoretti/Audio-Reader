# Audio Reader

Ferramenta de ditado por voz para Windows. Segure um atalho, fale, e o texto transcrito é digitado automaticamente no aplicativo ativo.

Inspirado no [Wispr Flow](https://wispr.com/flow). Usa o modelo Whisper da OpenAI via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) para transcrever localmente, sem depender de nuvem.

## Como Funciona

1. **Segure Ctrl+Alt** (configurável) para iniciar a gravação
2. **Solte** para parar
3. O áudio é transcrito localmente pelo Whisper
4. O texto é colado automaticamente no aplicativo ativo (via clipboard + Ctrl+V)

Um indicador flutuante aparece na tela: vermelho pulsante (gravando), laranja (transcrevendo), verde (injetando).

## Requisitos

- Windows 10/11
- Python 3.10+
- Microfone

## Instalação

```bash
git clone https://github.com/FelipeFcosta/Audio-Reader.git
cd Audio-Reader
pip install -r requirements.txt
```

### GPU (opcional)

A GPU é detectada automaticamente via `nvidia-smi`. Se uma NVIDIA for encontrada, usa CUDA com float16. Caso contrário, usa CPU com int8.

> **Importante:** Apenas GPUs NVIDIA são suportadas (CUDA). GPUs AMD não são compatíveis com faster-whisper/CTranslate2.

## Uso

```bash
python run.py
```

O app inicia na bandeja do sistema. Aguarde o modelo carregar, depois segure **Ctrl+Alt** para gravar.

- **Botão direito** no ícone da bandeja → Configurações ou Sair
- **Duplo clique** no ícone → abre Configurações

## Configuração

Salvas em `%APPDATA%\AudioReader\config.json`. Editáveis pela janela de configurações ou diretamente no arquivo.

| Opção | Padrão | Descrição |
|-------|--------|-----------|
| `model_size` | `"base"` | Modelo Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `device` | auto | `cpu` ou `cuda` (auto-detectado) |
| `compute_type` | auto | `int8` (CPU) ou `float16` (CUDA) |
| `language` | `null` | Código ISO 639-1 (`"pt"`, `"en"`) ou `null` para auto-detectar |
| `restore_clipboard` | `true` | Restaurar clipboard original após injeção |
| `vad_filter` | `true` | Filtrar segmentos sem fala (silero VAD) |
| `hotkey` | `"ctrl+alt"` | Atalho push-to-talk (precisa de 2+ teclas com modificador) |
| `start_with_windows` | `false` | Iniciar automaticamente com o Windows (registro) |

> **Nota:** Alterar modelo, dispositivo ou tipo de computação exige reiniciar o app. Hotkey e demais opções aplicam em tempo real.

## Idioma da Interface

A interface suporta Português e Inglês. O idioma segue a configuração de `language`:
- `"pt"` → Português
- `"en"` → Inglês
- `null` → detecta pelo locale do sistema

## Build (executável)

```bash
pip install pyinstaller
python -m PyInstaller AudioReader.spec --noconfirm
```

O executável é gerado em `dist\AudioReader\AudioReader.exe` (~258MB). O modelo Whisper é baixado automaticamente na primeira execução.

> **Importante:** Feche o AudioReader.exe antes de fazer build, ou ocorrerá PermissionError.

## Logs

Os logs ficam em `%APPDATA%\AudioReader\`:

| Arquivo | Conteúdo |
|---------|----------|
| `session.log` | Log completo da sessão atual (sobrescrito a cada execução) |
| `error.log` | Apenas erros, acumulativo entre sessões |

## Estrutura

```
Audio-Reader/
├── run.py                         # Ponto de entrada
├── requirements.txt
├── AudioReader.spec               # Config do PyInstaller
└── audio_reader/
    ├── app.py                     # Máquina de estados (orquestrador)
    ├── config.py                  # Gerenciamento de config (%APPDATA%)
    ├── i18n.py                    # Internacionalização (pt/en)
    ├── recorder.py                # Gravação de áudio (sounddevice)
    ├── transcription.py           # Wrapper do Whisper (faster-whisper)
    ├── hotkey.py                  # Detecção de push-to-talk (keyboard)
    ├── injector.py                # Injeção de texto (clipboard + Ctrl+V)
    ├── assets/
    │   ├── icon.png               # Ícone do app (632x632)
    │   └── icon.ico               # Ícone do exe (múltiplos tamanhos)
    └── ui/
        ├── tray.py                # Ícone na bandeja (pystray)
        ├── overlay.py             # Indicador flutuante (tkinter + PIL)
        └── settings.py            # Janela de configurações (customtkinter)
```

## Dependências

[faster-whisper](https://github.com/SYSTRAN/faster-whisper) | [sounddevice](https://python-sounddevice.readthedocs.io/) | [numpy](https://numpy.org/) | [keyboard](https://github.com/boppreh/keyboard) | [pystray](https://github.com/moses-palmer/pystray) | [Pillow](https://python-pillow.org/) | [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | [pyperclip](https://github.com/asweigart/pyperclip)
