#!/usr/bin/env python3
"""
Script de teste para verificar avisos de deprecação do SpeechBrain
Testa diferentes versões do pyannote.audio para ver se resolvem os avisos
"""

import os
import sys
import warnings
import subprocess
from typing import List, Tuple

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


class DeprecationTester:
    """Testador de avisos de deprecação"""
    
    def __init__(self):
        self.vm = VersionManager()
        self.warnings_captured = []
    
    def capture_warnings(self, message, category, filename, lineno, file=None, line=None) -> None:
        """Captura avisos de deprecação"""
        self.warnings_captured.append({
            'category': category.__name__,
            'message': str(message),
            'filename': filename,
            'lineno': lineno,
            'module': 'unknown'
        })
    
    def test_import_with_warnings(self, module_name: str) -> Tuple[bool, List[dict]]:
        """
        Testa importação de um módulo capturando avisos
        
        Returns:
            Tuple[bool, List[dict]]: (sucesso, lista_de_avisos)
        """
        self.warnings_captured = []
        
        # Configurar captura de avisos
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.showwarning = self.capture_warnings
            
            try:
                # Tentar importar o módulo
                if module_name == "pyannote.audio.pipelines":
                    import pyannote.audio.pipelines
                elif module_name == "speechbrain.inference":
                    import speechbrain.inference
                elif module_name == "speechbrain.pretrained":
                    import speechbrain.pretrained
                else:
                    __import__(module_name)
                
                # Capturar avisos do warnings.catch_warnings
                for warning in w:
                    self.warnings_captured.append({
                        'category': warning.category.__name__,
                        'message': str(warning.message),
                        'filename': warning.filename,
                        'lineno': warning.lineno,
                        'module': getattr(warning, 'module', 'unknown')
                    })
                
                return True, self.warnings_captured
                
            except Exception as e:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Erro ao importar {module_name}: {e}')}")
                return False, self.warnings_captured
    
    def filter_speechbrain_warnings(self, warnings_list: List[dict]) -> List[dict]:
        """Filtra apenas avisos relacionados ao SpeechBrain"""
        speechbrain_warnings = []
        
        for warning in warnings_list:
            message = warning['message'].lower()
            filename = warning['filename'].lower()
            
            # Verificar se o aviso está relacionado ao SpeechBrain
            if any(keyword in message for keyword in ['speechbrain', 'pretrained']):
                speechbrain_warnings.append(warning)
            elif any(keyword in filename for keyword in ['speechbrain']):
                speechbrain_warnings.append(warning)
        
        return speechbrain_warnings
    
    def test_current_setup(self) -> None:
        """Testa a configuração atual"""
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== Testando Configuração Atual ===')}")
        
        # Verificar versões instaladas
        pyannote_version = self.vm.get_installed_version("pyannote.audio")
        speechbrain_version = self.vm.get_installed_version("speechbrain")
        
        print_and_log(f"{ULTRASINGER_HEAD} pyannote.audio: {pyannote_version or 'Não instalado'}")
        print_and_log(f"{ULTRASINGER_HEAD} speechbrain: {speechbrain_version or 'Não instalado'}")
        print_and_log("")
        
        # Testar importações
        modules_to_test = [
            "pyannote.audio.pipelines",
            "speechbrain.inference",
        ]
        
        for module in modules_to_test:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted(f'Testando importação: {module}')}")
            success, warnings_list = self.test_import_with_warnings(module)
            
            if success:
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Importação bem-sucedida')}")
                
                # Filtrar avisos do SpeechBrain
                sb_warnings = self.filter_speechbrain_warnings(warnings_list)
                
                if sb_warnings:
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'⚠ {len(sb_warnings)} avisos do SpeechBrain encontrados:')}")
                    for warning in sb_warnings:
                        print_and_log(f"  - {warning['category']}: {warning['message']}")
                        print_and_log(f"    Arquivo: {warning['filename']}:{warning['lineno']}")
                else:
                    print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Nenhum aviso do SpeechBrain encontrado')}")
                
                # Mostrar outros avisos se houver
                other_warnings = [w for w in warnings_list if w not in sb_warnings]
                if other_warnings:
                    print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted(f'ℹ {len(other_warnings)} outros avisos encontrados:')}")
                    for warning in other_warnings[:3]:  # Mostrar apenas os primeiros 3
                        print_and_log(f"  - {warning['category']}: {warning['message'][:100]}...")
                    if len(other_warnings) > 3:
                        print_and_log(f"  ... e mais {len(other_warnings) - 3} avisos")
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('✗ Falha na importação')}")
            
            print_and_log("")
    
    def test_with_version(self, package: str, version: str) -> dict:
        """
        Testa uma versão específica de um pacote
        
        Returns:
            dict: Resultados do teste
        """
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted(f'=== Testando {package} {version} ===')}")
        
        # Verificar se a versão está disponível
        available_versions = self.vm.list_available_versions(package)
        if version not in available_versions:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Versão {version} não disponível')}")
            return {"success": False, "reason": "version_not_available"}
        
        # Verificar compatibilidade
        compatible, problems = self.vm.check_compatibility(package, version)
        if not compatible:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('Versão marcada como incompatível:')}")
            for problem in problems:
                print_and_log(f"  - {problem}")
            
            choice = input("Deseja testar mesmo assim? (s/N): ").strip().lower()
            if choice not in ['s', 'sim', 'y', 'yes']:
                return {"success": False, "reason": "user_cancelled"}
        
        # Salvar versão atual
        current_version = self.vm.get_installed_version(package)
        
        try:
            # Instalar versão de teste
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted(f'Instalando {package} {version}...')}")
            success = self.vm.install_version(package, version, force=True)
            
            if not success:
                return {"success": False, "reason": "installation_failed"}
            
            # Testar importações
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Testando importações...')}")
            
            results = {}
            modules_to_test = ["pyannote.audio.pipelines", "speechbrain.inference"]
            
            for module in modules_to_test:
                success, warnings_list = self.test_import_with_warnings(module)
                sb_warnings = self.filter_speechbrain_warnings(warnings_list)
                
                results[module] = {
                    "import_success": success,
                    "total_warnings": len(warnings_list),
                    "speechbrain_warnings": len(sb_warnings),
                    "warnings_details": sb_warnings
                }
            
            return {
                "success": True,
                "results": results,
                "version_tested": version
            }
            
        except Exception as e:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Erro durante o teste: {e}')}")
            return {"success": False, "reason": f"test_error: {e}"}
        
        finally:
            # Restaurar versão original se necessário
            if current_version and current_version != version:
                print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted(f'Restaurando versão original {current_version}...')}")
                self.vm.install_version(package, current_version, force=True)
    
    def run_comprehensive_test(self) -> None:
        """Executa teste abrangente de todas as versões"""
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== Teste Abrangente de Versões ===')}")
        print_and_log("")
        
        # Testar configuração atual
        self.test_current_setup()
        
        # Testar pyannote.audio 4.0.0 se disponível
        available_versions = self.vm.list_available_versions("pyannote.audio")
        if "4.0.0" in available_versions:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted('Testando pyannote.audio 4.0.0...')}")
            result = self.test_with_version("pyannote.audio", "4.0.0")
            
            if result["success"]:
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ Teste da versão 4.0.0 concluído')}")
                
                # Analisar resultados
                total_sb_warnings = sum(
                    r["speechbrain_warnings"] for r in result["results"].values()
                )
                
                if total_sb_warnings == 0:
                    print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('🎉 pyannote.audio 4.0.0 resolve os avisos do SpeechBrain!')}")
                else:
                    print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'pyannote.audio 4.0.0 ainda apresenta {total_sb_warnings} avisos do SpeechBrain')}")
            else:
                reason = result.get("reason", "unknown")
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Teste da versão 4.0.0 falhou: {reason}')}")
        
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== Teste Concluído ===')}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Testador de avisos de deprecação do SpeechBrain")
    parser.add_argument("--current", action="store_true", 
                       help="Testa apenas a configuração atual")
    parser.add_argument("--comprehensive", action="store_true", 
                       help="Executa teste abrangente de todas as versões")
    parser.add_argument("--package", type=str, 
                       help="Pacote específico para testar")
    parser.add_argument("--version", type=str, 
                       help="Versão específica para testar")
    
    args = parser.parse_args()
    
    tester = DeprecationTester()
    
    if args.current:
        tester.test_current_setup()
    elif args.comprehensive:
        tester.run_comprehensive_test()
    elif args.package and args.version:
        result = tester.test_with_version(args.package, args.version)
        if result["success"]:
            print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('Teste concluído com sucesso')}")
        else:
            reason = result.get("reason", "unknown")
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Teste falhou: {reason}')}")
    else:
        # Teste padrão - configuração atual
        tester.test_current_setup()


if __name__ == "__main__":
    main()