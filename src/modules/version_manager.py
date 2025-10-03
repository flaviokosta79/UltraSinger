"""
Sistema de gerenciamento de versões para dependências do UltraSinger
Permite alternar facilmente entre diferentes versões de bibliotecas como pyannote.audio
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import importlib.util
from packaging import version

from modules.console_colors import (
    ULTRASINGER_HEAD,
    blue_highlighted,
    gold_highlighted,
    red_highlighted,
    green_highlighted,
    cyan_highlighted,
)


def print_and_log(message: str) -> None:
    """Função simples para imprimir mensagens"""
    print(message)


class VersionManager:
    """Gerenciador de versões para dependências do UltraSinger"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de versões
        
        Args:
            config_path: Caminho para o arquivo de configuração de versões
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "version_config.json"
        )
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Carrega a configuração de versões"""
        default_config = {
            "pyannote.audio": {
                "current": "3.3.2",
                "available": {
                    "3.3.2": {
                        "compatible": True,
                        "description": "Versão estável atual",
                        "dependencies": {
                            "pyannote-core": "5.0.0",
                            "pyannote-database": "5.1.3",
                            "pyannote-metrics": "3.2.1",
                            "pyannote-pipeline": "3.0.1"
                        },
                        "breaking_changes": []
                    },
                    "4.0.0": {
                        "compatible": True,
                        "description": "Nova versão com melhorias significativas",
                        "dependencies": {
                            "pyannote-core": ">=5.0.0",
                            "pyannote-database": ">=5.1.3",
                            "pyannote-metrics": ">=3.2.1",
                            "pyannote-pipeline": ">=3.0.1"
                        },
                        "breaking_changes": [
                            "BREAKING(io): remove support for sox and soundfile audio I/O backends",
                            "BREAKING(setup): drop support to Python < 3.10",
                            "BREAKING(hub): rename use_auth_token to token",
                            "BREAKING(inference): Inference now only supports already instantiated models",
                            "BREAKING(cache): rely on huggingface_hub caching directory"
                        ],
                        "new_features": [
                            "Improved speaker assignment and counting with VBx clustering",
                            "Exclusive speaker diarization feature",
                            "Faster training with metadata caching",
                            "Support for offline (air-gapped) use",
                            "Switch from torchaudio to torchcodec for audio I/O"
                        ]
                    }
                }
            },
            "speechbrain": {
                "current": "1.0.3",
                "available": {
                    "1.0.3": {
                        "compatible": True,
                        "description": "Versão atual com API atualizada",
                        "breaking_changes": [],
                        "new_features": [
                            "speechbrain.inference substitui speechbrain.pretrained"
                        ]
                    }
                }
            },
            "tensorflow": {
                "current": "2.10.0",
                "available": {
                    "2.10.0": {
                        "compatible": True,
                        "description": "Versão estável com suporte GPU no Windows",
                        "dependencies": {
                            "tensorflow-estimator": "2.10.0",
                            "tensorflow-io-gcs-filesystem": "0.31.0"
                        },
                        "breaking_changes": [],
                        "notes": [
                            "Última versão com suporte GPU nativo no Windows",
                            "Recomendada para estabilidade em produção",
                            "Compatível com CREPE e todas as funcionalidades do UltraSinger"
                        ],
                        "gpu_support": {
                            "windows": True,
                            "linux": True,
                            "macos": False
                        }
                    },
                    "2.20.0": {
                        "compatible": True,
                        "description": "Nova versão com melhorias e breaking changes",
                        "dependencies": {
                            "tensorflow-estimator": ">=2.20.0",
                            "tensorflow-io-gcs-filesystem": "optional"
                        },
                        "breaking_changes": [
                            "tensorflow-io-gcs-filesystem agora é opcional",
                            "tf.lite será depreciado em favor do LiteRT",
                            "Possível incompatibilidade com versões antigas do CREPE"
                        ],
                        "new_features": [
                            "tf.data.Options.autotune.min_parallelism para warm-up mais rápido",
                            "Melhorias de performance em pipelines de dados",
                            "Preparação para migração do tf.lite para LiteRT"
                        ],
                        "notes": [
                            "EXPERIMENTAL: Requer testes extensivos com CREPE",
                            "tensorflow-io-gcs-filesystem deve ser instalado separadamente se necessário",
                            "Pode não ter suporte GPU nativo no Windows"
                        ],
                        "gpu_support": {
                            "windows": False,
                            "linux": True,
                            "macos": False
                        },
                        "installation_notes": [
                            "Para GCS filesystem: pip install 'tensorflow[gcs-filesystem]'",
                            "Verificar compatibilidade com CREPE antes de usar em produção"
                        ]
                    }
                }
            },
            "numpy": {
                "current": "1.23.5",
                "available": {
                    "1.23.5": {
                        "compatible": True,
                        "description": "Versão compatível com TensorFlow 2.10.0",
                        "dependencies": {},
                        "breaking_changes": [],
                        "notes": [
                            "Compatível com TensorFlow 2.10.0",
                            "Resolve conflitos _ARRAY_API",
                            "Recomendada para uso com TensorFlow 2.10.0",
                            "Estável para produção"
                        ],
                        "tensorflow_compatibility": {
                            "2.10.0": True,
                            "2.20.0": False
                        },
                        "new_features": []
                    },
                    "1.24.4": {
                        "compatible": True,
                        "description": "Versão compatível com Numba e TensorFlow 2.10.0",
                        "dependencies": {},
                        "breaking_changes": [
                            "Mudanças menores na API em relação ao 1.23.x"
                        ],
                        "notes": [
                            "Compatível com Numba (requisito mínimo)",
                            "Compatível com TensorFlow 2.10.0",
                            "Resolve conflitos _ARRAY_API",
                            "Versão estável para produção",
                            "Suporte completo ao Librosa e outras dependências"
                        ],
                        "tensorflow_compatibility": {
                            "2.10.0": True,
                            "2.20.0": True
                        },
                        "numba_compatibility": True,
                        "new_features": [
                            "Suporte aprimorado para Numba",
                            "Melhor compatibilidade com bibliotecas científicas",
                            "Correções de bugs críticos"
                        ]
                    },
                    "2.3.3": {
                        "compatible": True,
                        "description": "Versão mais recente com suporte Python 3.11-3.14",
                        "dependencies": {},
                        "breaking_changes": [
                            "API changes from NumPy 1.x",
                            "Possível incompatibilidade com TensorFlow 2.10.0",
                            "Mudanças em dtypes e casting behavior"
                        ],
                        "notes": [
                            "Suporte Python 3.11-3.14",
                            "Compatível com TensorFlow 2.20.0+",
                            "Breaking changes significativas do NumPy 1.x",
                            "Requer TensorFlow 2.16.0+ para compatibilidade total"
                        ],
                        "tensorflow_compatibility": {
                            "2.10.0": False,
                            "2.20.0": True
                        },
                        "numba_compatibility": True,
                        "new_features": [
                            "Melhor performance em operações matemáticas",
                            "Suporte aprimorado para Python 3.14",
                            "Correções de bugs em operações de casting",
                            "Melhor integração com bibliotecas modernas"
                        ]
                    }
                }
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge com configuração padrão
                    for package, config in default_config.items():
                        if package not in loaded_config:
                            loaded_config[package] = config
                    return loaded_config
            except Exception as e:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Erro ao carregar configuração: {e}')}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict) -> None:
        """Salva a configuração de versões"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Erro ao salvar configuração: {e}')}")
    
    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Obtém a versão instalada de um pacote"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        except subprocess.CalledProcessError:
            return None
        return None
    
    def list_available_versions(self, package_name: str) -> Dict:
        """Lista as versões disponíveis de um pacote"""
        if package_name not in self.config:
            return {}
        return self.config[package_name]["available"]
    
    def get_current_version(self, package_name: str) -> Optional[str]:
        """Obtém a versão atual configurada de um pacote"""
        if package_name not in self.config:
            return None
        return self.config[package_name]["current"]
    
    def set_current_version(self, package_name: str, version_str: str) -> bool:
        """Define a versão atual de um pacote"""
        if package_name not in self.config:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Pacote {package_name} não encontrado na configuração')}")
            return False
        
        if version_str not in self.config[package_name]["available"]:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Versão {version_str} não disponível para {package_name}')}")
            return False
        
        self.config[package_name]["current"] = version_str
        self._save_config(self.config)
        return True
    
    def install_version(self, package_name: str, version_str: str, force: bool = False) -> bool:
        """
        Instala uma versão específica de um pacote
        
        Args:
            package_name: Nome do pacote
            version_str: Versão a ser instalada
            force: Força a instalação mesmo se não for compatível
        """
        if package_name not in self.config:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Pacote {package_name} não encontrado na configuração')}")
            return False
        
        if version_str not in self.config[package_name]["available"]:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Versão {version_str} não disponível para {package_name}')}")
            return False
        
        version_info = self.config[package_name]["available"][version_str]
        
        # Verificar compatibilidade
        if not version_info.get("compatible", False) and not force:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Versão {version_str} marcada como incompatível')}")
            print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted('Breaking changes:')}")
            for change in version_info.get("breaking_changes", []):
                print_and_log(f"  - {change}")
            print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('Use --force para instalar mesmo assim')}")
            return False
        
        # Verificar compatibilidade TensorFlow + NumPy
        if package_name in ["tensorflow", "numpy"]:
            self._check_tensorflow_numpy_compatibility(package_name, version_str)
        
        try:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted(f'Instalando {package_name}=={version_str}...')}")
            
            # Instalar pacote principal
            cmd = [sys.executable, "-m", "pip", "install", f"{package_name}=={version_str}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Instalar dependências específicas se definidas
            dependencies = version_info.get("dependencies", {})
            for dep_name, dep_version in dependencies.items():
                if dep_version.startswith(">="):
                    dep_spec = f"{dep_name}{dep_version}"
                else:
                    dep_spec = f"{dep_name}=={dep_version}"
                
                print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted(f'Instalando dependência {dep_spec}...')}")
                dep_cmd = [sys.executable, "-m", "pip", "install", dep_spec]
                subprocess.run(dep_cmd, capture_output=True, text=True, check=True)
            
            # Atualizar configuração
            self.set_current_version(package_name, version_str)
            
            print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'{package_name} {version_str} instalado com sucesso!')}")
            return True
            
        except subprocess.CalledProcessError as e:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Erro ao instalar {package_name} {version_str}: {e}')}")
            if e.stdout:
                print_and_log(f"STDOUT: {e.stdout}")
            if e.stderr:
                print_and_log(f"STDERR: {e.stderr}")
            return False
    
    def check_compatibility(self, package_name: str, version_str: str) -> Tuple[bool, List[str]]:
        """
        Verifica a compatibilidade de uma versão
        
        Returns:
            Tuple[bool, List[str]]: (é_compatível, lista_de_problemas)
        """
        if package_name not in self.config:
            return False, [f"Pacote {package_name} não encontrado na configuração"]
        
        if version_str not in self.config[package_name]["available"]:
            return False, [f"Versão {version_str} não disponível para {package_name}"]
        
        version_info = self.config[package_name]["available"][version_str]
        problems = []
        
        # Verificar se está marcada como compatível
        if not version_info.get("compatible", False):
            problems.extend(version_info.get("breaking_changes", []))
        
        # Verificar versão do Python se necessário
        if package_name == "pyannote.audio" and version_str == "4.0.0":
            python_version = sys.version_info
            if python_version < (3, 10):
                problems.append(f"Python {python_version.major}.{python_version.minor} não suportado (requer >= 3.10)")
        
        return len(problems) == 0, problems
    
    def show_version_info(self, package_name: str, version_str: str) -> None:
        """Exibe informações detalhadas sobre uma versão"""
        if package_name not in self.config:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Pacote {package_name} não encontrado')}")
            return
        
        if version_str not in self.config[package_name]["available"]:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Versão {version_str} não disponível')}")
            return
        
        version_info = self.config[package_name]["available"][version_str]
        installed_version = self.get_installed_version(package_name)
        current_version = self.get_current_version(package_name)
        
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted(f'Informações da versão {package_name} {version_str}:')}")
        print_and_log(f"  Descrição: {version_info.get('description', 'N/A')}")
        print_and_log(f"  Compatível: {green_highlighted('Sim') if version_info.get('compatible', False) else red_highlighted('Não')}")
        print_and_log(f"  Versão instalada: {installed_version or 'Não instalada'}")
        print_and_log(f"  Versão configurada: {current_version or 'N/A'}")
        
        if version_info.get("breaking_changes"):
            print_and_log(f"  {red_highlighted('Breaking Changes:')}")
            for change in version_info["breaking_changes"]:
                print_and_log(f"    - {change}")
        
        if version_info.get("new_features"):
            print_and_log(f"  {green_highlighted('Novos Recursos:')}")
            for feature in version_info["new_features"]:
                print_and_log(f"    - {feature}")
        
        if version_info.get("dependencies"):
            print_and_log(f"  {blue_highlighted('Dependências:')}")
            for dep_name, dep_version in version_info["dependencies"].items():
                print_and_log(f"    - {dep_name}: {dep_version}")
    
    def _check_tensorflow_numpy_compatibility(self, package_name: str, version_str: str) -> None:
        """Verifica compatibilidade entre TensorFlow e NumPy"""
        if package_name == "tensorflow":
            current_numpy = self.get_installed_version("numpy")
            if current_numpy:
                tf_config = self.config["tensorflow"]["available"][version_str]
                numpy_compat = tf_config.get("numpy_compatibility", {})
                
                if version_str == "2.10.0" and current_numpy and version.parse(current_numpy) >= version.parse("1.24.0"):
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('⚠️  AVISO: Conflito detectado!')}")
                    print_and_log(f"{ULTRASINGER_HEAD} TensorFlow 2.10.0 + NumPy {current_numpy} pode causar erro '_ARRAY_API not found'")
                    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('Recomendação: NumPy < 1.24.0')}")
                elif version_str == "2.20.0" and current_numpy and version.parse(current_numpy) < version.parse("2.0.0"):
                    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('💡 SUGESTÃO: NumPy 2.3.3 recomendado para TensorFlow 2.20.0')}")
        
        elif package_name == "numpy":
            current_tf = self.get_installed_version("tensorflow")
            if current_tf:
                if current_tf == "2.10.0" and version.parse(version_str) >= version.parse("1.24.0"):
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('⚠️  AVISO: Conflito detectado!')}")
                    print_and_log(f"{ULTRASINGER_HEAD} NumPy {version_str} + TensorFlow 2.10.0 pode causar erro '_ARRAY_API not found'")
                    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('Considere usar NumPy 1.23.5 ou atualizar TensorFlow')}")
                elif current_tf == "2.20.0" and version.parse(version_str) < version.parse("2.0.0"):
                    print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('💡 SUGESTÃO: NumPy 2.3.3 recomendado para TensorFlow 2.20.0')}")

    def list_packages(self) -> None:
        """Lista todos os pacotes gerenciados"""
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('Pacotes gerenciados:')}")
        
        for package_name, package_config in self.config.items():
            current_version = package_config["current"]
            installed_version = self.get_installed_version(package_name)
            available_versions = list(package_config["available"].keys())
            
            print_and_log(f"  {cyan_highlighted(package_name)}:")
            print_and_log(f"    Versão atual: {current_version}")
            print_and_log(f"    Versão instalada: {installed_version or 'Não instalada'}")
            print_and_log(f"    Versões disponíveis: {', '.join(available_versions)}")


def create_version_manager() -> VersionManager:
    """Factory function para criar um VersionManager"""
    return VersionManager()


# CLI para gerenciamento de versões
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciador de versões do UltraSinger")
    parser.add_argument("--list", action="store_true", help="Lista todos os pacotes gerenciados")
    parser.add_argument("--package", type=str, help="Nome do pacote")
    parser.add_argument("--version", type=str, help="Versão do pacote")
    parser.add_argument("--install", action="store_true", help="Instala a versão especificada")
    parser.add_argument("--info", action="store_true", help="Mostra informações da versão")
    parser.add_argument("--force", action="store_true", help="Força instalação mesmo se incompatível")
    parser.add_argument("--check", action="store_true", help="Verifica compatibilidade")
    
    args = parser.parse_args()
    
    vm = VersionManager()
    
    if args.list:
        vm.list_packages()
    elif args.package and args.version:
        if args.install:
            vm.install_version(args.package, args.version, args.force)
        elif args.info:
            vm.show_version_info(args.package, args.version)
        elif args.check:
            compatible, problems = vm.check_compatibility(args.package, args.version)
            if compatible:
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('Versão compatível!')}")
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Versão incompatível:')}")
                for problem in problems:
                    print_and_log(f"  - {problem}")
    else:
        parser.print_help()