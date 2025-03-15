#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from pathlib import Path
import config  # Importa primeiro para garantir que as pastas foram criadas
from services.logging_service import setup_logging, get_logger
from services.enhanced_logging_service import logger as enhanced_logger
from ui.app_window import DictationApp

def parse_arguments():
    """
    Processa os argumentos de linha de comando.
    
    Returns:
        Namespace com os argumentos processados
    """
    parser = argparse.ArgumentParser(
        description="Ubuntu Dictation - Um aplicativo de ditado por voz para Ubuntu"
    )
    
    # Argumentos de linha de comando
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Ativa o modo de depuração com logs detalhados"
    )
    parser.add_argument(
        "--no-gui", 
        action="store_true", 
        help="Executa em modo de linha de comando (sem interface gráfica)"
    )
    parser.add_argument(
        "--version", 
        action="store_true", 
        help="Mostra a versão do aplicativo e sai"
    )
    parser.add_argument(
        "--config", 
        metavar="ARQUIVO", 
        help="Especifica um arquivo de configuração alternativo"
    )
    parser.add_argument(
        "--list-devices", 
        action="store_true", 
        help="Lista dispositivos de áudio disponíveis e sai"
    )
    
    return parser.parse_args()


def show_version():
    """Exibe informações de versão do aplicativo."""
    print(f"{config.APP_NAME} v{config.APP_VERSION}")
    print(f"Autor: {config.APP_AUTHOR}")
    print(f"Website: {config.APP_WEBSITE}")


def list_audio_devices():
    """Lista dispositivos de áudio disponíveis no sistema."""
    try:
        # Lazy import para não depender dessas bibliotecas se não for necessário
        import pyaudio
        
        p = pyaudio.PyAudio()
        
        print("\n=== Dispositivos de áudio disponíveis ===")
        print("ID  |  Nome  |  Canais  |  Taxa de amostragem")
        print("-" * 60)
        
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            # Exibe apenas dispositivos de entrada
            if dev_info.get('maxInputChannels') > 0:
                print(f"{i:2d}  |  {dev_info.get('name')[:30]}  |  "
                      f"{dev_info.get('maxInputChannels')}  |  "
                      f"{int(dev_info.get('defaultSampleRate'))} Hz")
        
        print("\nO dispositivo padrão é geralmente adequado para a maioria dos casos.")
        print("Para escolher um dispositivo específico, use a interface de configurações.")
        
        p.terminate()
    except ImportError:
        print("Não foi possível listar dispositivos de áudio. "
              "A biblioteca PyAudio não está instalada.")
        print("Instale-a com: pip install pyaudio")
    except Exception as e:
        print(f"Erro ao listar dispositivos de áudio: {e}")


def main():
    """Função principal que inicia a aplicação."""
    # Processar argumentos
    args = parse_arguments()
    
    # Mostrar versão e sair se solicitado
    if args.version:
        show_version()
        return 0
        
    # Listar dispositivos de áudio e sair se solicitado
    if args.list_devices:
        list_audio_devices()
        return 0
    
    # Configurar o logging
    log_level = logging.DEBUG if args.debug else None
    setup_logging(level=log_level, use_enhanced=True)
    logger = get_logger(__name__)
    
    # Configurar modo debug no logger avançado
    if args.debug:
        enhanced_logger.set_debug_mode(True)
    
    # Log inicial
    logger.info(f"Iniciando {config.APP_NAME} v{config.APP_VERSION}")
    enhanced_logger.log_info("main", f"Iniciando {config.APP_NAME} v{config.APP_VERSION}", "system")
    
    try:
        # Verificar se estamos no ambiente gráfico
        if args.no_gui:
            logger.info("Iniciando em modo CLI (sem interface gráfica)")
            enhanced_logger.log_info("main", "Iniciando em modo CLI (sem interface gráfica)", "system")
            # TODO: Implementar modo CLI para reconhecimento de voz
            print("Modo CLI ainda não implementado.")
            return 1
        else:
            # Verificar se o display X11/Wayland está disponível
            if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                logger.error("Nenhum servidor gráfico (X11/Wayland) detectado!")
                enhanced_logger.log_critical("main", "Nenhum servidor gráfico (X11/Wayland) detectado!", "system")
                print("Erro: Esta aplicação requer um ambiente gráfico para funcionar.")
                print("Se estiver em um servidor remoto, use SSH com encaminhamento X11.")
                return 1
            
            # Iniciar a aplicação com interface gráfica
            logger.info("Iniciando interface gráfica")
            enhanced_logger.log_info("main", "Iniciando interface gráfica", "ui")
            app = DictationApp()
            return app.run()
            
    except Exception as e:
        logger.exception(f"Erro não tratado na aplicação: {e}")
        enhanced_logger.log_critical("main", f"Erro não tratado na aplicação: {str(e)}", "system")
        return 1
    finally:
        logger.info("Aplicação encerrada")
        enhanced_logger.log_info("main", "Aplicação encerrada", "system")


if __name__ == "__main__":
    sys.exit(main())