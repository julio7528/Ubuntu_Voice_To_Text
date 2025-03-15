"""
Serviço de logging avançado para a aplicação Ubuntu Dictation.

Este módulo implementa um sistema de logging com formatação tabular
que escreve registros detalhados em arquivos de texto com alinhamento preciso.
"""
import os
import time
import logging
import datetime
import inspect
import textwrap
from enum import Enum
from pathlib import Path

# Importa a configuração para obter os caminhos
from config import USER_DATA_DIR, APP_NAME, APP_VERSION

# Diretório para armazenar logs
LOG_DIR = USER_DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

class ProcessType(str, Enum):
    """Tipos de processos para categorização nos logs"""
    UI = "ui"
    CORE = "core"
    SYSTEM = "system"
    SPEECH = "speech"
    INPUT = "input"

class LogStatus(str, Enum):
    """Status possíveis para entradas de log"""
    FAILURE = "failure"
    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL = "critical"
    INFO = "information"
    DEBUG = "debug"

class EnhancedLogger:
    """
    Logger avançado com formatação tabular e alinhamento preciso.
    Grava logs em arquivos com formato de tabela alinhada.
    """
    
    def __init__(self, project_name=APP_NAME):
        """
        Inicializa o logger avançado.
        
        Args:
            project_name: Nome do projeto/aplicação para os arquivos de log
        """
        self.project_name = project_name
        self.log_dir = LOG_DIR
        self.log_file = None
        self.debug_mode = True  # Valor padrão
        
        # Formato de colunas - definições de largura
        self.col_widths = {
            'timestamp': 25,    # TIMESTAMP
            'task': 15,         # TASK
            'function': 30,     # FUNCTION
            'file': 25,         # FILE
            'message': 50,      # MESSAGE
            'process_type': 15, # PROCESS_TYPE
            'status': 15        # STATUS
        }
        
        # Largura para wrap de mensagens
        self.message_width = self.col_widths['message']
        
        # Quantidade de espaço entre borda e conteúdo da coluna
        self.padding = 1
        
        # Setup inicial
        self.setup_logging()
        
    def setup_logging(self):
        """Configuração inicial do logging"""
        # Criar pasta de logs se não existir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Criar arquivo de log com timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(self.log_dir, f"{self.project_name}_{timestamp}.log")
        
        # Define codificação UTF-8 para o arquivo de log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            # Escreve o cabeçalho do arquivo de log
            f.write(self._create_header())
        
        # Configurar logging padrão do Python
        logging.basicConfig(
            level=logging.DEBUG if self.debug_mode else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        
        # Registra função para adicionar linha de fechamento ao encerrar programa
        import atexit
        atexit.register(self._add_closing_line)
        
        # Log inicial
        self.log_info("setup_logging", f"Iniciado logger para {self.project_name} v{APP_VERSION}")
        
    def _create_separator_line(self):
        """Cria a linha separadora com + alinhado precisamente com as barras verticais"""
        separator = "+"
        for name, width in self.col_widths.items():
            # Adiciona dois traços extras para compensar o espaço de padding em cada lado
            separator += "-" * (width + self.padding * 2) + "+"
        return separator
        
    def _create_header(self):
        """Cria o cabeçalho com alinhamento preciso e títulos melhor centralizados"""
        # Títulos das colunas com um espaço adicional em cada lado para melhor centralização
        headers = {
            'timestamp': " TIMESTAMP ",
            'task': " TASK ",
            'function': " FUNCTION ",
            'file': " FILE ",
            'message': " MESSAGE ",
            'process_type': " PROCESS_TYPE ",
            'status': " STATUS "
        }
        
        # Criar linha separadora
        separator = self._create_separator_line()
        
        # Criar linha de cabeçalho
        header_line = "|"
        for name, width in self.col_widths.items():
            # Centraliza o título na coluna
            title = headers[name]
            padding_left = self.padding + (width - len(title) + 1) // 2  # +2 para compensar os espaços adicionados
            padding_right = width - (len(title) - 1) - padding_left + self.padding  # -2 para compensar os espaços adicionados
            header_line += " " * padding_left + title + " " * padding_right + "|"
        
        # Monta o cabeçalho completo
        full_header = separator + "\n" + header_line + "\n" + separator + "\n"
        return full_header

    def _get_caller_info(self, depth=3):
        """Obtém informações sobre o chamador (arquivo, função)
        
        Args:
            depth (int): Quão longe na pilha de chamadas olhar para o chamador
                    2 = chamador direto deste método
                    3 = chamador do método de logging (padrão)
                    4 ou mais = mais longe na pilha de chamadas
        
        Returns:
            tuple: (nome_arquivo, nome_função)
        """
        try:
            # Pega a stack de chamadas até o depth desejado
            frame = inspect.currentframe()
            for _ in range(depth):
                if frame.f_back is None:
                    break
                frame = frame.f_back
            
            # Extrai informações do frame
            if frame:
                frame_info = inspect.getframeinfo(frame)
                filename = os.path.basename(frame_info.filename)
                function_name = frame_info.function
                return filename, function_name
        except Exception:
            pass
        
        return "unknown.py", "unknown"
        
    def log_entry(self, function_name, log_message, process_type=ProcessType.SYSTEM, status=LogStatus.INFO, task_name=None):
        """Registra uma nova entrada no arquivo de log com alinhamento preciso"""
        # Obtém data e hora atuais
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Usa o nome da aplicação como tarefa se não for fornecido
        if task_name is None:
            task_name = self.project_name
        
        # Obtém informações do chamador (arquivo)
        source_file, _ = self._get_caller_info(depth=3)
        
        # Valida valores de enum
        if not isinstance(process_type, ProcessType):
            try:
                process_type = ProcessType(process_type.lower())
            except ValueError:
                process_type = ProcessType.SYSTEM
                
        if not isinstance(status, LogStatus):
            try:
                status = LogStatus(status.lower())
            except ValueError:
                status = LogStatus.INFO
        
        # Formato do status
        status_str = status.value
        
        # Quebra a mensagem em múltiplas linhas se necessário
        message_lines = textwrap.wrap(log_message, width=self.message_width)
        if not message_lines:
            message_lines = [""]
            
        # Prepara valores para cada coluna (truncando se necessário)
        values = {
            'timestamp': timestamp[:self.col_widths['timestamp']],
            'task': task_name[:self.col_widths['task']],
            'function': function_name[:self.col_widths['function']],
            'file': source_file[:self.col_widths['file']],
            'message': message_lines[0],
            'process_type': process_type.value[:self.col_widths['process_type']],
            'status': status_str[:self.col_widths['status']]
        }
        
        # Formata a linha usando o mesmo padrão de padding que o cabeçalho
        log_line = "|"
        for name, width in self.col_widths.items():
            content = values[name]
            padding_right = width - len(content) + self.padding
            log_line += " " * self.padding + content + " " * padding_right + "|"
            
        # Escreve no arquivo de log com codificação UTF-8
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + "\n")
            
            # Se houver mais linhas na mensagem, adiciona-as com alinhamento preciso
            if len(message_lines) > 1:
                # Cria linha de continuação para cada linha adicional da mensagem
                for i in range(1, len(message_lines)):
                    cont_line = "|"
                    for name, width in self.col_widths.items():
                        if name == 'message':
                            # A coluna de mensagem tem conteúdo
                            content = message_lines[i]
                            padding_right = width - len(content) + self.padding
                            cont_line += " " * self.padding + content + " " * padding_right + "|"
                        else:
                            # Outras colunas ficam vazias
                            cont_line += " " * (width + self.padding * 2) + "|"
                    f.write(cont_line + "\n")
            
            # Adiciona separador após erros críticos para ênfase
            if status == LogStatus.CRITICAL:
                f.write(self._create_separator_line() + "\n")
        
        # Log para console
        log_level = self._get_log_level(status)
        logging.log(log_level, f"{task_name} - {function_name}: {log_message}")
    
    def _add_closing_line(self):
        """Adiciona linha de fechamento ao arquivo de log quando o programa encerra"""
        if hasattr(self, 'log_file') and self.log_file and os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    # Adiciona linha com data/hora de encerramento
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(self._create_separator_line() + "\n")
                    f.write(f"| Log encerrado em: {now}" + " " * 150 + "|\n")
                    f.write(self._create_separator_line() + "\n")
            except Exception:
                pass  # Falha silenciosamente se não puder escrever no arquivo
                
    def _get_log_level(self, status):
        """Mapeia status de log para nível de logging do Python"""
        status_map = {
            LogStatus.CRITICAL: logging.CRITICAL,
            LogStatus.FAILURE: logging.ERROR,
            LogStatus.WARNING: logging.WARNING,
            LogStatus.INFO: logging.INFO,
            LogStatus.SUCCESS: logging.INFO,
            LogStatus.DEBUG: logging.DEBUG
        }
        return status_map.get(status, logging.INFO)
    
    def log_info(self, function_name, message, process_type=ProcessType.SYSTEM):
        """Registra mensagem informativa"""
        self.log_entry(function_name, message, process_type, LogStatus.INFO)
    
    def log_debug(self, function_name, message, process_type=ProcessType.SYSTEM):
        """Registra mensagem de depuração"""
        if self.debug_mode:
            self.log_entry(function_name, message, process_type, LogStatus.DEBUG)
    
    def log_success(self, function_name, message, process_type=ProcessType.SYSTEM):
        """Registra mensagem de sucesso"""
        self.log_entry(function_name, message, process_type, LogStatus.SUCCESS)
    
    def log_warning(self, function_name, message, process_type=ProcessType.SYSTEM):
        """Registra mensagem de aviso"""
        self.log_entry(function_name, message, process_type, LogStatus.WARNING)
    
    def log_error(self, function_name, message, process_type=ProcessType.SYSTEM):
        """Registra mensagem de erro"""
        self.log_entry(function_name, message, process_type, LogStatus.FAILURE)
    
    def log_critical(self, function_name, message, process_type=ProcessType.SYSTEM):
        """Registra mensagem de erro crítico"""
        self.log_entry(function_name, message, process_type, LogStatus.CRITICAL)
    
    def set_debug_mode(self, enabled=True):
        """Ativa ou desativa o modo de depuração"""
        self.debug_mode = enabled
        # Atualiza o nível de logging
        logging.getLogger().setLevel(logging.DEBUG if enabled else logging.INFO)
        self.log_info("set_debug_mode", f"Modo de depuração {'ativado' if enabled else 'desativado'}")


# Instância global para uso em toda a aplicação
logger = EnhancedLogger()

# Funções de conveniência para chamar os métodos do logger global
def setup(project_name=APP_NAME):
    """Configura o logger com um nome de projeto específico"""
    global logger
    logger = EnhancedLogger(project_name)
    return logger

def info(function_name, message, process_type=ProcessType.SYSTEM):
    """Registra mensagem informativa"""
    logger.log_info(function_name, message, process_type)

def debug(function_name, message, process_type=ProcessType.SYSTEM):
    """Registra mensagem de depuração"""
    logger.log_debug(function_name, message, process_type)

def success(function_name, message, process_type=ProcessType.SYSTEM):
    """Registra mensagem de sucesso"""
    logger.log_success(function_name, message, process_type)

def warning(function_name, message, process_type=ProcessType.SYSTEM):
    """Registra mensagem de aviso"""
    logger.log_warning(function_name, message, process_type)

def error(function_name, message, process_type=ProcessType.SYSTEM):
    """Registra mensagem de erro"""
    logger.log_error(function_name, message, process_type)

def critical(function_name, message, process_type=ProcessType.SYSTEM):
    """Registra mensagem de erro crítico"""
    logger.log_critical(function_name, message, process_type)

def set_debug(enabled=True):
    """Ativa ou desativa o modo de depuração"""
    logger.set_debug_mode(enabled)

def get_log_file():
    """Retorna o caminho do arquivo de log atual"""
    return logger.log_file

# Teste do módulo
if __name__ == "__main__":
    # Configurar logger
    setup("ubuntu_dictation_test")
    
    # Testar diferentes tipos de log
    info("main", "Aplicação inicializada com sucesso")
    debug("main", "Valor da variável x=42")
    success("process_audio", "Áudio processado com sucesso", ProcessType.SPEECH)
    warning("check_microphone", "Qualidade do microfone abaixo do ideal", ProcessType.INPUT)
    error("connect_device", "Falha ao conectar ao dispositivo", ProcessType.SYSTEM)
    critical("main", "Falha crítica no sistema de reconhecimento", ProcessType.CORE)
    
    # Teste de mensagem longa com quebra automática
    info("test_wrapping", "Esta é uma mensagem muito longa que deverá ser quebrada automaticamente " +
         "em múltiplas linhas para garantir a formatação adequada da tabela. " +
         "O sistema deve alinhar corretamente cada linha adicional.")