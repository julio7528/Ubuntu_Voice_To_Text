"""
Configurações globais para a aplicação Ubuntu Dictation.

Este módulo define caminhos de diretórios, configurações padrão,
e constantes utilizadas por toda a aplicação.
"""
import sys
import json
from pathlib import Path

# =========== Diretórios da aplicação ===========
# Obtém o diretório de instalação
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Diretórios de usuário
USER_CONFIG_DIR = Path.home() / ".config" / "ubuntu-dictation"
USER_CACHE_DIR = Path.home() / ".cache" / "ubuntu-dictation"
USER_DATA_DIR = Path.home() / ".local" / "share" / "ubuntu-dictation"
LOG_DIR = USER_DATA_DIR / "logs"
MODELS_DIR = USER_CACHE_DIR / "models"

# Cria os diretórios necessários
for directory in [USER_CONFIG_DIR, USER_CACHE_DIR, USER_DATA_DIR, LOG_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =========== Arquivos de configuração ===========
CONFIG_FILE = USER_CONFIG_DIR / "settings.json"
LOG_FILE_TEMPLATE = LOG_DIR / "ubuntu-dictation-{date}.log"

# =========== Configurações padrão ===========
DEFAULT_SETTINGS = {
    # Configurações gerais
    "general": {
        "startup_with_system": False,
        "minimize_to_tray": True,
        "notification_sounds": True,
        "save_dictation_history": True,
        "max_history_items": 100,
        "theme": "system",  # "light", "dark", "system"
        "log_level": "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    },
    
    # Atalhos de teclado
    "hotkeys": {
        "toggle_dictation": "super+h",  # Atalho para ativar/desativar o ditado (similar ao Win+H)
        "pause_dictation": "ctrl+space",
        "cancel_dictation": "escape"
    },
    
    # Configurações de reconhecimento de voz
    "speech_recognition": {
        "engine": "vosk",  # "vosk", "whisper", "google", "system"
        "language": "pt-BR",
        "auto_punctuation": True,
        "sensitivity": 0.6,  # 0.0 a 1.0
        "timeout": 5,  # segundos
        "auto_stop_after_silence": 2.0,  # segundos, 0 = desabilitado
        "capitalize_sentences": True
    },
    
    # Configurações de interface do usuário
    "ui": {
        "floating_panel": True,
        "panel_width": 500,
        "panel_height": 200,
        "opacity": 0.9,  # 0.0 a 1.0
        "show_confidence": False,
        "font_size": 12
    },
    
    # Configurações avançadas
    "advanced": {
        "audio_device": "default",
        "sample_rate": 16000,
        "debug_mode": False,
        "keep_logs_days": 30,
        "max_log_size_mb": 5,
        "keyboard_backend": "auto"  # "pynput", "xdotool", "pyautogui", "auto"
    }
}

# =========== Constantes da aplicação ===========
APP_NAME = "Ubuntu Dictation"
APP_ID = "com.github.ubuntu-dictation"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Júlio Gomes"
APP_WEBSITE = "https://github.com/usuario/ubuntu-dictation"
APP_ICON_NAME = "microphone"  # Nome do ícone no tema


def load_settings():
    """
    Carrega as configurações do arquivo. Se o arquivo não existir,
    cria um novo com as configurações padrão.
    
    Returns:
        dict: Configurações carregadas
    """
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                user_settings = json.load(f)
            
            # Combina as configurações do usuário com os padrões
            # para garantir que novas configurações sejam adicionadas
            merged_settings = DEFAULT_SETTINGS.copy()
            
            # Atualiza de forma recursiva, preservando novas opções padrão
            _update_nested_dict(merged_settings, user_settings)
            
            return merged_settings
        else:
            # Arquivo não existe, cria com configurações padrão
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    Salva as configurações no arquivo.
    
    Args:
        settings (dict): Configurações a serem salvas
    
    Returns:
        bool: True se as configurações foram salvas com sucesso
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False


def get_setting(path, default=None):
    """
    Obtém uma configuração específica pelo caminho de acesso.
    
    Args:
        path (str): Caminho para a configuração (ex: "speech_recognition.language")
        default: Valor padrão caso a configuração não exista
    
    Returns:
        Valor da configuração ou valor padrão
    """
    settings = load_settings()
    
    # Divide o caminho em partes
    parts = path.split('.')
    
    # Navega pelo dicionário
    current = settings
    for part in parts:
        if part in current:
            current = current[part]
        else:
            return default
    
    return current


def set_setting(path, value):
    """
    Define uma configuração específica pelo caminho de acesso.
    
    Args:
        path (str): Caminho para a configuração (ex: "speech_recognition.language")
        value: Valor a ser definido
    
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    settings = load_settings()
    
    # Divide o caminho em partes
    parts = path.split('.')
    
    # Navega pelo dicionário até o penúltimo nível
    current = settings
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Define o valor
    current[parts[-1]] = value
    
    # Salva as configurações atualizadas
    return save_settings(settings)


def _update_nested_dict(base_dict, new_dict):
    """
    Atualiza recursivamente um dicionário aninhado.
    
    Args:
        base_dict (dict): Dicionário base a ser atualizado
        new_dict (dict): Dicionário com novos valores
    """
    for key, value in new_dict.items():
        if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
            _update_nested_dict(base_dict[key], value)
        else:
            base_dict[key] = value


def reset_settings():
    """
    Restaura todas as configurações para os valores padrão.
    
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    return save_settings(DEFAULT_SETTINGS.copy())


# Carrega as configurações quando o módulo é importado
SETTINGS = load_settings()

# Para uso simplificado em outros módulos
get = get_setting
set = set_setting
reset = reset_settings