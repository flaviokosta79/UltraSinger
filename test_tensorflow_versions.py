#!/usr/bin/env python3
"""
Teste de compatibilidade para diferentes versões do TensorFlow
Valida funcionalidade do CREPE e outras dependências com TensorFlow 2.10.0 e 2.20.0
"""

import os
import sys
import subprocess
import importlib.util
from typing import Dict, List, Tuple, Optional

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from modules.console_colors import (
        ULTRASINGER_HEAD,
        blue_highlighted,
        gold_highlighted,
        red_highlighted,
        green_highlighted,
        cyan_highlighted,
    )
except ImportError:
    # Fallback se não conseguir importar
    ULTRASINGER_HEAD = "[UltraSinger]"
    def blue_highlighted(text): return f"\033[94m{text}\033[0m"
    def gold_highlighted(text): return f"\033[93m{text}\033[0m"
    def red_highlighted(text): return f"\033[91m{text}\033[0m"
    def green_highlighted(text): return f"\033[92m{text}\033[0m"
    def cyan_highlighted(text): return f"\033[96m{text}\033[0m"


def print_and_log(message: str) -> None:
    """Função para imprimir mensagens"""
    print(message)


class TensorFlowVersionTester:
    """Testador de compatibilidade para versões do TensorFlow"""
    
    def __init__(self):
        self.test_results = {}
        
    def get_tensorflow_version(self) -> Optional[str]:
        """Obtém a versão atual do TensorFlow"""
        try:
            import tensorflow as tf
            return tf.__version__
        except ImportError:
            return None
        except Exception as e:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'Erro ao obter versão do TensorFlow: {e}')}")
            return None
    
    def test_tensorflow_import(self) -> Tuple[bool, str]:
        """Testa importação básica do TensorFlow"""
        try:
            import tensorflow as tf
            version = tf.__version__
            print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'✓ TensorFlow {version} importado com sucesso')}")
            return True, f"TensorFlow {version} funcional"
        except ImportError as e:
            error_msg = f"Falha na importação do TensorFlow: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro inesperado no TensorFlow: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg
    
    def test_tensorflow_gpu_support(self) -> Tuple[bool, str]:
        """Testa suporte a GPU do TensorFlow"""
        try:
            import tensorflow as tf
            
            # Verificar se há GPUs disponíveis
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                gpu_info = f"GPUs detectadas: {len(gpus)}"
                for i, gpu in enumerate(gpus):
                    gpu_info += f"\n  GPU {i}: {gpu.name}"
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'✓ {gpu_info}')}")
                return True, gpu_info
            else:
                msg = "Nenhuma GPU detectada (usando CPU)"
                print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted(f'ℹ {msg}')}")
                return True, msg
                
        except Exception as e:
            error_msg = f"Erro ao verificar suporte GPU: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg
    
    def test_crepe_compatibility(self) -> Tuple[bool, str]:
        """Testa compatibilidade com CREPE"""
        try:
            # Tentar importar crepe
            import crepe
            
            # Verificar se consegue criar um modelo básico
            import numpy as np
            
            # Criar dados de teste (1 segundo de áudio a 16kHz)
            test_audio = np.random.randn(16000).astype(np.float32)
            
            # Tentar executar predição básica do CREPE
            time, frequency, confidence, activation = crepe.predict(
                test_audio, 
                sr=16000, 
                model_capacity='tiny',  # Usar modelo menor para teste
                verbose=0
            )
            
            if len(frequency) > 0:
                msg = f"CREPE funcional (predição: {len(frequency)} frames)"
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'✓ {msg}')}")
                return True, msg
            else:
                error_msg = "CREPE não retornou resultados válidos"
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
                return False, error_msg
                
        except ImportError as e:
            error_msg = f"CREPE não instalado: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted(f'ℹ {error_msg}')}")
            return True, error_msg  # Não é erro crítico se CREPE não estiver instalado
        except Exception as e:
            error_msg = f"Erro no CREPE: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg
    
    def test_tensorflow_io_gcs(self) -> Tuple[bool, str]:
        """Testa disponibilidade do tensorflow-io-gcs-filesystem"""
        try:
            import tensorflow_io_gcs_filesystem
            version = getattr(tensorflow_io_gcs_filesystem, '__version__', 'unknown')
            msg = f"tensorflow-io-gcs-filesystem {version} disponível"
            print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'✓ {msg}')}")
            return True, msg
        except ImportError:
            msg = "tensorflow-io-gcs-filesystem não instalado (opcional no TF 2.20+)"
            print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted(f'ℹ {msg}')}")
            return True, msg  # Não é erro no TF 2.20+
        except Exception as e:
            error_msg = f"Erro no tensorflow-io-gcs-filesystem: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg
    
    def test_numpy_compatibility(self) -> Tuple[bool, str]:
        """Testa compatibilidade entre TensorFlow e NumPy"""
        try:
            import tensorflow as tf
            import numpy as np
            
            # Verificar versões
            tf_version = tf.__version__
            numpy_version = np.__version__
            
            # Teste de conversão TensorFlow <-> NumPy
            tf_tensor = tf.constant([1.0, 2.0, 3.0, 4.0])
            numpy_array = tf_tensor.numpy()
            
            # Teste de operações mistas
            np_array = np.array([5.0, 6.0, 7.0, 8.0])
            tf_from_numpy = tf.constant(np_array)
            
            # Operação mista
            result = tf.add(tf_tensor, tf_from_numpy)
            expected = np.array([6.0, 8.0, 10.0, 12.0])
            
            if np.allclose(result.numpy(), expected):
                msg = f"TensorFlow {tf_version} + NumPy {numpy_version} compatíveis"
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'✓ {msg}')}")
                return True, msg
            else:
                error_msg = f"Incompatibilidade TensorFlow {tf_version} + NumPy {numpy_version}"
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Erro na compatibilidade TF+NumPy: {str(e)}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg

    def test_basic_operations(self) -> Tuple[bool, str]:
        """Testa operações básicas do TensorFlow"""
        try:
            import tensorflow as tf
            
            # Teste básico de operações
            a = tf.constant([1, 2, 3])
            b = tf.constant([4, 5, 6])
            c = tf.add(a, b)
            
            result = c.numpy()
            expected = [5, 7, 9]
            
            if list(result) == expected:
                msg = f"Operações básicas funcionais: {result}"
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted(f'✓ {msg}')}")
                return True, msg
            else:
                error_msg = f"Resultado inesperado: {result} != {expected}"
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Erro em operações básicas: {e}"
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            return False, error_msg
    
    def run_all_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Executa todos os testes de compatibilidade"""
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== TESTE DE COMPATIBILIDADE TENSORFLOW ===')}")
        
        tf_version = self.get_tensorflow_version()
        if tf_version:
            print_and_log(f"{ULTRASINGER_HEAD} Testando TensorFlow {cyan_highlighted(tf_version)}")
        else:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('TensorFlow não detectado')}")
        
        print_and_log("")
        
        tests = [
            ("Importação TensorFlow", self.test_tensorflow_import),
            ("Compatibilidade NumPy", self.test_numpy_compatibility),
            ("Operações Básicas", self.test_basic_operations),
            ("Suporte GPU", self.test_tensorflow_gpu_support),
            ("TensorFlow IO GCS", self.test_tensorflow_io_gcs),
            ("Compatibilidade CREPE", self.test_crepe_compatibility),
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print_and_log(f"{ULTRASINGER_HEAD} {blue_highlighted(f'Testando: {test_name}')}")
            try:
                success, message = test_func()
                results[test_name] = (success, message)
                if success:
                    passed += 1
            except Exception as e:
                error_msg = f"Erro inesperado no teste: {e}"
                results[test_name] = (False, error_msg)
                print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ {error_msg}')}")
            
            print_and_log("")
        
        # Resumo dos resultados
        print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('=== RESUMO DOS TESTES ===')}")
        print_and_log(f"{ULTRASINGER_HEAD} Testes aprovados: {green_highlighted(f'{passed}/{total}')}")
        
        if tf_version:
            if tf_version.startswith("2.10"):
                print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ TensorFlow 2.10.x - Versão estável recomendada')}")
            elif tf_version.startswith("2.20"):
                print_and_log(f"{ULTRASINGER_HEAD} {gold_highlighted('⚠ TensorFlow 2.20.x - Versão experimental')}")
            else:
                print_and_log(f"{ULTRASINGER_HEAD} {cyan_highlighted(f'ℹ TensorFlow {tf_version} - Versão não testada especificamente')}")
        
        # Verificar problemas críticos
        critical_tests = ["Importação TensorFlow", "Operações Básicas"]
        critical_failed = [name for name in critical_tests if not results.get(name, (False, ""))[0]]
        
        if critical_failed:
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted(f'✗ TESTES CRÍTICOS FALHARAM: {critical_failed}')}")
            print_and_log(f"{ULTRASINGER_HEAD} {red_highlighted('TensorFlow não está funcional!')}")
        else:
            print_and_log(f"{ULTRASINGER_HEAD} {green_highlighted('✓ TensorFlow está funcional para uso básico')}")
        
        return results


def main():
    """Função principal"""
    tester = TensorFlowVersionTester()
    results = tester.run_all_tests()
    
    # Código de saída baseado nos resultados
    critical_tests = ["Importação TensorFlow", "Operações Básicas"]
    critical_failed = [name for name in critical_tests if not results.get(name, (False, ""))[0]]
    
    if critical_failed:
        sys.exit(1)  # Falha crítica
    else:
        sys.exit(0)  # Sucesso


if __name__ == "__main__":
    main()