#!/usr/bin/env python3
"""
Script de instalação automática de dependências do UltraSinger
Permite escolher entre diferentes versões de bibliotecas como pyannote.audio
"""

import os
import sys
import argparse
from pathlib import Path

# Adicionar o diretório src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from modules.version_manager import VersionManager
    from modules.console_colors import (
        ULTRASINGER_HEAD,
        blue_highlighted,
        gold_highlighted,
        red_highlighted,
        green_highlighted,
        cyan_highlighted,
    )
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que está executando este script do diretório raiz do UltraSinger")
    sys.exit(1)


def print_and_log(message: str) -> None:
    """Função simples para imprimir mensagens"""
    print(message)


def show_welcome():
    """Exibe mensagem de boas-vindas"""
    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== UltraSinger Dependency Manager ===')}")
    print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted('Gerenciador de dependências e versões')}")
    print_and_log("")


def interactive_mode():
    """Modo interativo para gerenciamento de versões"""
    vm = VersionManager()
    
    while True:
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('Opções disponíveis:')}")
        print_and_log("1. Listar pacotes gerenciados")
        print_and_log("2. Mostrar informações de uma versão")
        print_and_log("3. Verificar compatibilidade")
        print_and_log("4. Instalar versão específica")
        print_and_log("5. Verificar versões instaladas")
        print_and_log("6. Sair")
        print_and_log("")
        
        try:
            choice = input("Escolha uma opção (1-6): ").strip()
        except KeyboardInterrupt:
            print_and_log(f"\n{ULTRASINGER_HEAD} {cyan_highlighted('Saindo...')}")
            break
        
        if choice == "1":
            vm.list_packages()
            
        elif choice == "2":
            package = input("Nome do pacote: ").strip()
            version = input("Versão: ").strip()
            if package and version:
                vm.show_version_info(package, version)
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Nome do pacote e versão são obrigatórios')}")
                
        elif choice == "3":
            package = input("Nome do pacote: ").strip()
            version = input("Versão: ").strip()
            if package and version:
                compatible, problems = vm.check_compatibility(package, version)
                if compatible:
                    print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Versão compatível!')}")
                else:
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('✗ Versão incompatível:')}")
                    for problem in problems:
                        print_and_log(f"  - {problem}")
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Nome do pacote e versão são obrigatórios')}")
                
        elif choice == "4":
            package = input("Nome do pacote: ").strip()
            version = input("Versão: ").strip()
            if package and version:
                # Verificar compatibilidade primeiro
                compatible, problems = vm.check_compatibility(package, version)
                if not compatible:
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Versão incompatível:')}")
                    for problem in problems:
                        print_and_log(f"  - {problem}")
                    
                    force = input("Deseja instalar mesmo assim? (s/N): ").strip().lower()
                    if force not in ['s', 'sim', 'y', 'yes']:
                        print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted('Instalação cancelada')}")
                        continue
                
                print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Iniciando instalação...')}")
                success = vm.install_version(package, version, force=not compatible)
                if success:
                    print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Instalação concluída com sucesso!')}")
                else:
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('✗ Falha na instalação')}")
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Nome do pacote e versão são obrigatórios')}")
                
        elif choice == "5":
            print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('Verificando versões instaladas...')}")
            packages = ["pyannote.audio", "speechbrain", "tensorflow", "numpy", "torch", "torchaudio"]
            for package in packages:
                installed = vm.get_installed_version(package)
                if installed:
                    print_and_log(f"  {cyan_highlighted(package)}: {installed}")
                else:
                    print_and_log(f"  {cyan_highlighted(package)}: {red_highlighted('Não instalado')}")
                    
        elif choice == "6":
            print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted('Saindo...')}")
            break
            
        else:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Opção inválida')}")
        
        print_and_log("")  # Linha em branco para separar


def quick_setup():
    """Configuração rápida com versões recomendadas"""
    vm = VersionManager()
    
    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== Configuração Rápida ===')}")
    print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted('Instalando versões recomendadas...')}")
    print_and_log("")
    
    # Verificar versão do Python
    python_version = sys.version_info
    print_and_log(f"{ULTRASINGER_HEAD} Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Configuração do TensorFlow
    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== Configuração do TensorFlow ===')}")
    current_tf = vm.get_installed_version("tensorflow")
    if current_tf:
        print_and_log(f"{ULTRASINGER_HEAD} TensorFlow atual: {cyan_highlighted(current_tf)}")
    
    print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Versões disponíveis:')}")
    print_and_log(f"  1. TensorFlow 2.10.0 - {green_highlighted('Estável com GPU no Windows')}")
    print_and_log(f"  2. TensorFlow 2.20.0 - {gold_highlighted('Nova versão (EXPERIMENTAL)')}")
    print_and_log(f"  3. Manter versão atual")
    
    tf_choice = input("Escolha a versão do TensorFlow (1-3): ").strip()
    
    if tf_choice == "1":
        print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando TensorFlow 2.10.0...')}")
        vm.install_version("tensorflow", "2.10.0")
        # Instalar NumPy compatível automaticamente
        print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando NumPy 1.23.5 (compatível)...')}")
        vm.install_version("numpy", "1.23.5")
    elif tf_choice == "2":
        print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('ATENÇÃO: TensorFlow 2.20.0 é experimental!')}")
        print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Pode não ter suporte GPU no Windows')}")
        confirm = input("Deseja continuar? (s/N): ").strip().lower()
        if confirm in ['s', 'sim', 'y', 'yes']:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando TensorFlow 2.20.0...')}")
            vm.install_version("tensorflow", "2.20.0", force=True)
            # Instalar NumPy compatível automaticamente
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando NumPy 2.3.3 (compatível)...')}")
            vm.install_version("numpy", "2.3.3")
        else:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Mantendo versão atual do TensorFlow')}")
    else:
        print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Mantendo versão atual do TensorFlow')}")
    
    print_and_log("")
    
    # Configuração do pyannote.audio
    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== Configuração do pyannote.audio ===')}")
    
    if python_version >= (3, 10):
        print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Python >= 3.10 detectado')}")
        print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Você pode usar pyannote.audio 4.0.0')}")
        
        choice = input("Deseja instalar pyannote.audio 4.0.0? (s/N): ").strip().lower()
        if choice in ['s', 'sim', 'y', 'yes']:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando pyannote.audio 4.0.0...')}")
            success = vm.install_version("pyannote.audio", "4.0.0", force=True)
            if success:
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ pyannote.audio 4.0.0 instalado!')}")
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('✗ Falha na instalação, usando versão 3.3.2')}")
                vm.install_version("pyannote.audio", "3.3.2")
        else:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando pyannote.audio 3.3.2 (versão estável)...')}")
            vm.install_version("pyannote.audio", "3.3.2")
    else:
        print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Python < 3.10 detectado')}")
        print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Instalando pyannote.audio 3.3.2 (compatível)...')}")
        vm.install_version("pyannote.audio", "3.3.2")
    
    print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Configuração rápida concluída!')}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="UltraSinger Dependency Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python install_dependencies.py --interactive    # Modo interativo
  python install_dependencies.py --quick-setup    # Configuração rápida
  python install_dependencies.py --list           # Listar pacotes
  python install_dependencies.py --package pyannote.audio --version 4.0.0 --install
  python install_dependencies.py --package pyannote.audio --version 4.0.0 --info
  python install_dependencies.py --package pyannote.audio --version 4.0.0 --check
        """
    )
    
    parser.add_argument("--interactive", action="store_true", 
                       help="Modo interativo")
    parser.add_argument("--quick-setup", action="store_true", 
                       help="Configuração rápida com versões recomendadas")
    parser.add_argument("--list", action="store_true", 
                       help="Lista todos os pacotes gerenciados")
    parser.add_argument("--package", type=str, 
                       help="Nome do pacote")
    parser.add_argument("--version", type=str, 
                       help="Versão do pacote")
    parser.add_argument("--install", action="store_true", 
                       help="Instala a versão especificada")
    parser.add_argument("--info", action="store_true", 
                       help="Mostra informações da versão")
    parser.add_argument("--check", action="store_true", 
                       help="Verifica compatibilidade")
    parser.add_argument("--force", action="store_true", 
                       help="Força instalação mesmo se incompatível")
    
    args = parser.parse_args()
    
    show_welcome()
    
    if args.interactive:
        interactive_mode()
    elif args.quick_setup:
        quick_setup()
    elif args.list:
        vm = VersionManager()
        vm.list_packages()
    elif args.package and args.version:
        vm = VersionManager()
        if args.install:
            success = vm.install_version(args.package, args.version, args.force)
            sys.exit(0 if success else 1)
        elif args.info:
            vm.show_version_info(args.package, args.version)
        elif args.check:
            compatible, problems = vm.check_compatibility(args.package, args.version)
            if compatible:
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Versão compatível!')}")
                sys.exit(0)
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('✗ Versão incompatível:')}")
                for problem in problems:
                    print_and_log(f"  - {problem}")
                sys.exit(1)
    else:
        # Modo interativo por padrão se nenhum argumento for fornecido
        interactive_mode()


if __name__ == "__main__":
    main()