#!/usr/bin/env python3
"""
Script para criar a estrutura de diretórios e arquivos vazios para uma aplicação de
reconhecimento de voz para Ubuntu, similar ao recurso de ditado do Windows 11 (Win+H).
"""
import os
import sys

# Definição da estrutura do projeto
PROJECT_NAME = "ubuntu_dictation"
PROJECT_STRUCTURE = {
    "ubuntu_dictation": [
        "__init__.py",
        "main.py",
        "config.py",
        "README.md",
        {
            "ui": [
                "__init__.py",
                "app_window.py",
                "dictation_panel.py",
                "settings_dialog.py",
                "tray_icon.py",
                "resources/README.md"
            ]
        },
        {
            "core": [
                "__init__.py",
                "speech_recognition_engine.py",
                "text_processor.py",
                "keyboard_integration.py",
                "hotkey_manager.py"
            ]
        },
        {
            "utils": [
                "__init__.py",
                "audio_devices.py",
                "language_manager.py",
                "settings_manager.py",
                "system_integration.py"
            ]
        },
        {
            "services": [
                "__init__.py",
                "clipboard_service.py",
                "notification_service.py",
                "logging_service.py"
            ]
        },
        {
            "tests": [
                "__init__.py",
                "test_speech_recognition.py",
                "test_ui.py"
            ]
        },
        {
            "docs": [
                "installation.md",
                "usage.md",
                "development.md"
            ]
        }
    ]
}

def create_directories_and_files(base_path, structure):
    """
    Cria recursivamente os diretórios e arquivos com base na estrutura definida.
    
    Args:
        base_path: Caminho base onde criar a estrutura
        structure: Dicionário ou lista definindo a estrutura
    """
    if isinstance(structure, dict):
        for directory, contents in structure.items():
            dir_path = os.path.join(base_path, directory)
            
            # Criar diretório se não existir
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Criado diretório: {dir_path}")
            
            # Processar conteúdo do diretório
            create_directories_and_files(dir_path, contents)
            
    elif isinstance(structure, list):
        for item in structure:
            if isinstance(item, dict):
                # Se for dicionário, é um subdiretório
                create_directories_and_files(base_path, item)
            else:
                # Se for string, é um arquivo
                file_path = os.path.join(base_path, item)
                
                # Verificar se o caminho contém um subdiretório
                file_dir = os.path.dirname(file_path)
                if file_dir and not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                    print(f"Criado diretório: {file_dir}")
                
                # Criar arquivo vazio se não existir
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        pass  # Arquivo vazio
                    print(f"Criado arquivo: {file_path}")


def main():
    """Função principal para criar a estrutura do projeto."""
    # Determinar o diretório onde criar o projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(script_dir, PROJECT_NAME)
    
    # Criar estrutura
    create_directories_and_files(script_dir, {PROJECT_NAME: PROJECT_STRUCTURE[PROJECT_NAME]})
    
    print(f"\nEstrutura de projeto criada em: {project_dir}")
    print("\nPara desenvolver os arquivos, solicite o conteúdo específico de cada um.")


if __name__ == "__main__":
    main()