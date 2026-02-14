# Audio Reader

Ferramenta de ditado por voz para Windows. Segure um atalho, fale, e o texto transcrito é digitado automaticamente no aplicativo ativo. Transcrição 100% local via [faster-whisper](https://github.com/SYSTRAN/faster-whisper), sem depender de nuvem.

## Como Funciona

1. **Segure Ctrl+Alt** (configurável) para iniciar a gravação
2. **Solte** para parar
3. O texto é colado automaticamente no aplicativo ativo

## Instalação

Baixe o instalador na página de [Releases](https://github.com/FelipeMoretti/Audio-Reader/releases).

### Via código-fonte

```bash
git clone https://github.com/FelipeMoretti/Audio-Reader.git
cd Audio-Reader
pip install -r requirements.txt
python run.py
```

**Requisitos:** Windows 10/11, Python 3.10+, microfone.

## GPU (opcional)

Detectada automaticamente. Se uma GPU NVIDIA for encontrada, usa CUDA com float16. Caso contrário, usa CPU com int8.

> GPUs AMD não são compatíveis com faster-whisper/CTranslate2.

## Configuração

Salvas em `%APPDATA%\AudioReader\config.json`. Editáveis pela janela de configurações ou diretamente no arquivo.

| Opção | Padrão | Descrição |
|-------|--------|-----------|
| `model_size` | `"base"` | Modelo Whisper: `tiny`, `base`, `small`, `medium`, `large-v3-turbo` |
| `device` | auto | `cpu` ou `cuda` (auto-detectado) |
| `compute_type` | auto | `int8` (CPU) ou `float16` (CUDA) |
| `language` | `null` | Código ISO 639-1 (`"pt"`, `"en"`) ou `null` para auto |
| `restore_clipboard` | `true` | Restaurar clipboard original após injeção |
| `vad_filter` | `true` | Filtrar segmentos sem fala |
| `hotkey` | `"ctrl+alt"` | Atalho push-to-talk (2+ teclas com modificador) |
| `start_with_windows` | `false` | Iniciar com o Windows |

> Alterar modelo, dispositivo ou compute_type exige reiniciar o app. Demais opções aplicam em tempo real.

## Build

```bash
python build.py
```

Gera o executável e o instalador em `dist/`. Requer [Inno Setup](https://jrsoftware.org/isdl.php) para o instalador.
