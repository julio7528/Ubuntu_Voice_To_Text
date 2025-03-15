"""
Serviço de logging para a aplicação Ubuntu Dictation.

Este módulo fornece funções para configurar e utilizar o sistema de logging,
incluindo dois tipos de logs:
1. Logs padrão do Python (para console e arquivos simples)
2. Logs avançados com formato tabular (através do EnhancedLogger)

O módulo permite escolher qual sistema usar ou usar ambos simultaneamente.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Importações do projeto
from config import USER_DATA_DIR, APP_NAME, APP_VERSION

# Diretório para armazenar logs
LOG_DIR = USER_DATA_DIR / "logs"
DEFAULT_LOG_LEVEL = logging.INFO
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Manter 3 arquivos de backup

# Garantir que o diretório de logs exista
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Nome do arquivo de log baseado na data
LOG_FILE = LOG_DIR / f"ubuntu-dictation-{datetime.now().strftime('%Y-%m-%d')}.log"

# Referência para o logger avançado
enhanced_logger = None

def setup_logging(level=None, log_to_console=True, log_to_file=True, use_enhanced=False):
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              Se None, será utilizado o nível DEFAULT_LOG_LEVEL
        log_to_console: Se True, logs serão exibidos no console
        log_to_file: Se True, logs serão gravados em arquivo
        use_enhanced: Se True, também inicializa o logger avançado com formato tabular
    
    Returns:
        O logger configurado
    """
    global enhanced_logger
    
    # Definir nível de logging
    log_level = level or DEFAULT_LOG_LEVEL
    
    # Obter logger raiz
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Limpar handlers existentes (caso a função seja chamada múltiplas vezes)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Criar formatador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Adicionar handler de console se solicitado
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Adicionar handler de arquivo se solicitado
    if log_to_file:
        try:
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=MAX_LOG_SIZE,
                backupCount=BACKUP_COUNT
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            # Se não puder criar o arquivo de log, pelo menos avisar no console
            logging.error(f"Não foi possível configurar o log em arquivo: {e}")
    
    # Log inicial para confirmar configuração
    logger.info(f"Logging iniciado: nível={logging.getLevelName(log_level)}, "
               f"arquivo={LOG_FILE if log_to_file else 'Desativado'}")
    
    # Inicializar logger avançado se solicitado
    if use_enhanced:
        try:
            # Importação adiada para evitar ciclos de importação
            from services.enhanced_logging_service import setup
            enhanced_logger = setup(APP_NAME)
            logger.info("Enhanced logging ativado")
        except ImportError as e:
            logger.warning(f"Não foi possível inicializar o enhanced logger: {e}")
    
    return logger


def get_logger(name):
    """
    Obtém um logger para um módulo específico.
    
    Args:
        name: Nome do módulo (usar __name__ é recomendado)
    
    Returns:
        Logger configurado para o módulo
    """
    return logging.getLogger(name)


class LogCapture:
    """
    Captura saídas de stdout/stderr e as redireciona para o logging.
    Útil para capturar saídas de bibliotecas de terceiros.
    """
    
    def __init__(self, logger=None, level=logging.INFO):
        """
        Inicializa o capturador de logs.
        
        Args:
            logger: Logger para redirecionar (se None, usa o logger raiz)
            level: Nível de log para mensagens capturadas
        """
        self.logger = logger or logging.getLogger()
        self.level = level
        self.stdout_original = sys.stdout
        self.stderr_original = sys.stderr
    
    def __enter__(self):
        """Ativa a captura ao entrar no contexto."""
        sys.stdout = self
        sys.stderr = self
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restaura saídas originais ao sair do contexto."""
        sys.stdout = self.stdout_original
        sys.stderr = self.stderr_original
    
    def write(self, message):
        """Redireciona mensagens escritas para o logger."""
        if message and not message.isspace():
            for line in message.rstrip().splitlines():
                self.logger.log(self.level, line)
    
    def flush(self):
        """Implementação de flush para compatibilidade."""
        pass


def list_log_files():
    """
    Lista todos os arquivos de log disponíveis.
    
    Returns:
        Lista de caminhos para arquivos de log
    """
    if not LOG_DIR.exists():
        return []
    
    return sorted(
        [f for f in LOG_DIR.glob("ubuntu-dictation-*.log")],
        key=os.path.getmtime,
        reverse=True
    )


def purge_old_logs(max_age_days=30, max_files=20):
    """
    Remove arquivos de log antigos.
    
    Args:
        max_age_days: Idade máxima em dias para manter logs
        max_files: Número máximo de arquivos a manter
    
    Returns:
        Número de arquivos removidos
    """
    log_files = list_log_files()
    
    # Se não exceder limites, não fazer nada
    if len(log_files) <= max_files:
        return 0
    
    # Manter max_files mais recentes, remover o resto
    files_to_remove = log_files[max_files:]
    
    # Tentativa de remoção
    removed = 0
    for file_path in files_to_remove:
        try:
            file_path.unlink()
            removed += 1
        except (PermissionError, OSError) as e:
            logging.warning(f"Não foi possível remover log antigo {file_path}: {e}")
    
    return removed


# Funções para integração com o enhanced logger
def log_enhanced(function_name, message, level="info", process_type="system"):
    """
    Registra uma mensagem usando o logger avançado.
    
    Args:
        function_name: Nome da função que está gerando o log
        message: Mensagem a ser registrada
        level: Nível do log ('info', 'debug', 'warning', 'error', 'critical', 'success')
        process_type: Tipo de processo ('ui', 'core', 'system', 'speech', 'input')
    
    Returns:
        True se o log foi registrado, False se o logger avançado não está disponível
    """
    if enhanced_logger is None:
        # Log normal se o enhanced logger não estiver ativo
        logging.getLogger().log(
            logging.INFO if level == "success" else getattr(logging, level.upper(), logging.INFO),
            f"{function_name}: {message}"
        )
        return False
        
    # Chama o método correto baseado no nível
    method_name = f"log_{level}"
    if hasattr(enhanced_logger, method_name):
        method = getattr(enhanced_logger, method_name)
        method(function_name, message, process_type)
        return True
    
    # Fallback para log_info se o método não existir
    enhanced_logger.log_info(function_name, message, process_type)
    return True


# Funções de conveniência para o logger avançado
def info(function_name, message, process_type="system"):
    """Registra mensagem informativa no logger avançado"""
    return log_enhanced(function_name, message, "info", process_type)

def debug(function_name, message, process_type="system"):
    """Registra mensagem de depuração no logger avançado"""
    return log_enhanced(function_name, message, "debug", process_type)

def success(function_name, message, process_type="system"):
    """Registra mensagem de sucesso no logger avançado"""
    return log_enhanced(function_name, message, "success", process_type)

def warning(function_name, message, process_type="system"):
    """Registra mensagem de aviso no logger avançado"""
    return log_enhanced(function_name, message, "warning", process_type)

def error(function_name, message, process_type="system"):
    """Registra mensagem de erro no logger avançado"""
    return log_enhanced(function_name, message, "error", process_type)

def critical(function_name, message, process_type="system"):
    """Registra mensagem de erro crítico no logger avançado"""
    return log_enhanced(function_name, message, "critical", process_type)


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging (com enhanced logger)
    setup_logging(level=logging.DEBUG, use_enhanced=True)
    
    # Obter logger para este módulo
    logger = get_logger(__name__)
    
    # Testar diferentes níveis
    logger.debug("Mensagem de depuração")
    logger.info("Mensagem informativa")
    logger.warning("Aviso importante")
    logger.error("Erro ocorrido")
    
    # Testar logger avançado
    info("test_function", "Teste de mensagem informativa")
    success("test_function", "Operação concluída com sucesso")
    warning("test_function", "Atenção necessária")
    error("test_function", "Erro encontrado")
    
    # Exemplo com captura
    print("Esta mensagem será impressa normalmente")
    
    with LogCapture():
        print("Esta mensagem será redirecionada para o log")
    
    print("Voltamos à impressão normal")
    
    # Listar logs existentes
    print(f"Arquivos de log disponíveis: {list_log_files()}")