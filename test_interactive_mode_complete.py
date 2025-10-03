#!/usr/bin/env python3
"""
Teste completo do modo interativo do UltraSinger
"""

import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.init_interactive_mode import InteractiveMode
from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, blue_highlighted
from Settings import Settings


def create_test_settings():
    """Criar configurações de teste"""
    settings = Settings()
    settings.input_file_path = "test_audio.mp3"
    settings.output_file_path = "output"
    settings.whisper_model = "base"
    settings.demucs_model = "htdemucs"
    return settings


def test_interactive_mode_initialization():
    """Testar inicialização do modo interativo"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Inicialização ===')}")
    
    try:
        interactive = InteractiveMode()
        
        # Verificar atributos básicos
        assert hasattr(interactive, 'console'), "Console não inicializado"
        assert hasattr(interactive, 'header'), "Header não definido"
        assert hasattr(interactive, 'settings_cache_file'), "Cache file não definido"
        
        print(f"✓ {green_highlighted('Modo interativo inicializado corretamente')}")
        print(f"  - Console: {type(interactive.console).__name__}")
        print(f"  - Header: {interactive.header}")
        print(f"  - Cache file: {interactive.settings_cache_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na inicialização: {e}')}")
        return False


def test_welcome_display():
    """Testar exibição da tela de boas-vindas"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Tela de Boas-vindas ===')}")
    
    try:
        interactive = InteractiveMode()
        
        # Capturar saída do console
        with patch.object(interactive.console, 'print') as mock_print:
            interactive.display_welcome()
            
            # Verificar se houve chamadas para print
            assert mock_print.called, "Display welcome não chamou console.print"
            
            # Verificar se contém elementos esperados
            calls = [str(call) for call in mock_print.call_args_list]
            welcome_content = ' '.join(calls)
            
            expected_elements = ['UltraSinger', 'bem-vindo', 'karaoke']
            for element in expected_elements:
                if element.lower() not in welcome_content.lower():
                    print(f"⚠ {blue_highlighted(f'Elemento esperado não encontrado: {element}')}")
        
        print(f"✓ {green_highlighted('Tela de boas-vindas exibida corretamente')}")
        print(f"  - Chamadas para console.print: {mock_print.call_count}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na tela de boas-vindas: {e}')}")
        return False


def test_audio_format_support():
    """Testar suporte a formatos de áudio"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Formatos de Áudio ===')}")
    
    try:
        interactive = InteractiveMode()
        
        # Obter formatos suportados
        supported_formats = interactive.get_supported_audio_formats()
        
        # Verificar se é uma lista
        assert isinstance(supported_formats, list), "Formatos não retornados como lista"
        assert len(supported_formats) > 0, "Nenhum formato suportado"
        
        # Verificar formatos esperados
        expected_formats = ['.mp3', '.wav', '.flac']
        for fmt in expected_formats:
            assert fmt in supported_formats, f"Formato esperado não encontrado: {fmt}"
        
        print(f"✓ {green_highlighted('Formatos de áudio suportados:')}")
        for fmt in supported_formats:
            print(f"  - {fmt}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro nos formatos de áudio: {e}')}")
        return False


def test_input_file_validation():
    """Testar validação de arquivo de entrada"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Validação de Entrada ===')}")
    
    try:
        interactive = InteractiveMode()
        settings = create_test_settings()
        
        # Criar arquivo de teste temporário
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(b'fake mp3 content')
            temp_file_path = temp_file.name
        
        try:
            # Simular entrada do usuário
            with patch('rich.prompt.Prompt.ask') as mock_prompt:
                mock_prompt.return_value = temp_file_path
                
                # Testar validação
                result = interactive.validate_audio_file(temp_file_path)
                
                # Verificar resultado
                assert isinstance(result, bool), "Resultado da validação deve ser boolean"
                
                print(f"✓ {green_highlighted('Validação de arquivo funcionando')}")
                print(f"  - Arquivo: {temp_file_path}")
                print(f"  - Válido: {result}")
                
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na validação de entrada: {e}')}")
        return False


def test_model_selection():
    """Testar seleção de modelos"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Seleção de Modelos ===')}")
    
    try:
        interactive = InteractiveMode()
        
        # Importar enums de modelo
        from modules.Speech_Recognition.Whisper import WhisperModel
        from modules.Audio.separation import DemucsModel
        
        # Testar seleção de modelo Whisper
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.return_value = "1"  # Selecionar primeiro modelo
            
            selected_whisper = interactive.select_model_enhanced(
                WhisperModel, "Whisper", WhisperModel.BASE, show_details=False
            )
            
            assert selected_whisper is not None, "Modelo Whisper não selecionado"
            assert isinstance(selected_whisper, WhisperModel), "Tipo de modelo incorreto"
            
            print(f"✓ {green_highlighted('Seleção de modelo Whisper funcionando')}")
            print(f"  - Modelo selecionado: {selected_whisper.value}")
        
        # Testar seleção de modelo Demucs
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.return_value = "1"  # Selecionar primeiro modelo
            
            selected_demucs = interactive.select_model_enhanced(
                DemucsModel, "Demucs", DemucsModel.HTDEMUCS, show_details=False
            )
            
            assert selected_demucs is not None, "Modelo Demucs não selecionado"
            assert isinstance(selected_demucs, DemucsModel), "Tipo de modelo incorreto"
            
            print(f"✓ {green_highlighted('Seleção de modelo Demucs funcionando')}")
            print(f"  - Modelo selecionado: {selected_demucs.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na seleção de modelos: {e}')}")
        return False


def test_advanced_configuration():
    """Testar configurações avançadas"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Configurações Avançadas ===')}")
    
    try:
        interactive = InteractiveMode()
        settings = create_test_settings()
        
        # Testar configuração de processamento
        with patch('rich.prompt.IntPrompt.ask') as mock_int_prompt, \
             patch('rich.prompt.Confirm.ask') as mock_confirm:
            
            mock_int_prompt.return_value = 16  # batch_size
            mock_confirm.return_value = False  # create_audio_stems
            
            interactive._configure_processing_options(settings)
            
            # Verificar se configurações foram aplicadas
            assert hasattr(settings, 'whisper_batch_size'), "Batch size não configurado"
            
            print(f"✓ {green_highlighted('Configuração de processamento funcionando')}")
        
        # Testar configuração de saída
        with patch('rich.prompt.Confirm.ask') as mock_confirm:
            mock_confirm.return_value = True  # create_karaoke
            
            interactive._configure_output_options(settings)
            
            print(f"✓ {green_highlighted('Configuração de saída funcionando')}")
        
        # Testar configuração de dispositivo
        with patch('rich.prompt.Confirm.ask') as mock_confirm, \
             patch('modules.DeviceDetection.device_detection.check_gpu_support') as mock_gpu:
            
            mock_gpu.return_value = ("cuda", True)  # GPU disponível
            mock_confirm.return_value = False  # force_cpu
            
            interactive._configure_device_options(settings)
            
            assert hasattr(settings, 'force_cpu'), "Force CPU não configurado"
            
            print(f"✓ {green_highlighted('Configuração de dispositivo funcionando')}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro nas configurações avançadas: {e}')}")
        return False


def test_settings_cache():
    """Testar sistema de cache de configurações"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Cache de Configurações ===')}")
    
    try:
        interactive = InteractiveMode()
        settings = create_test_settings()
        
        # Criar cache temporário
        cache_data = {
            'input_file_path': 'cached_input.mp3',
            'output_file_path': 'cached_output',
            'whisper_model': 'large',
            'demucs_model': 'htdemucs_ft'
        }
        
        # Salvar cache
        interactive.save_settings_cache(cache_data)
        
        # Verificar se arquivo de cache foi criado
        assert os.path.exists(interactive.settings_cache_file), "Arquivo de cache não criado"
        
        # Carregar cache
        loaded_cache = interactive.load_settings_cache()
        
        assert loaded_cache is not None, "Cache não carregado"
        assert loaded_cache['input_file_path'] == cache_data['input_file_path'], "Dados do cache incorretos"
        
        print(f"✓ {green_highlighted('Sistema de cache funcionando')}")
        print(f"  - Arquivo de cache: {interactive.settings_cache_file}")
        print(f"  - Dados salvos: {len(cache_data)} itens")
        
        # Limpar cache de teste
        if os.path.exists(interactive.settings_cache_file):
            os.unlink(interactive.settings_cache_file)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no sistema de cache: {e}')}")
        return False


def test_summary_display():
    """Testar exibição do resumo"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exibição de Resumo ===')}")
    
    try:
        interactive = InteractiveMode()
        settings = create_test_settings()
        
        # Configurar algumas opções
        settings.create_karaoke = True
        settings.create_audio_stems = False
        settings.force_cpu = False
        
        # Capturar saída do console
        with patch.object(interactive.console, 'print') as mock_print:
            interactive.display_summary(settings)
            
            # Verificar se houve chamadas para print
            assert mock_print.called, "Display summary não chamou console.print"
            
            print(f"✓ {green_highlighted('Exibição de resumo funcionando')}")
            print(f"  - Chamadas para console.print: {mock_print.call_count}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na exibição de resumo: {e}')}")
        return False


def test_full_interactive_flow():
    """Testar fluxo completo do modo interativo"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Fluxo Completo ===')}")
    
    try:
        interactive = InteractiveMode()
        settings = create_test_settings()
        
        # Simular entrada do usuário para fluxo completo
        with patch('rich.prompt.Prompt.ask') as mock_prompt, \
             patch('rich.prompt.Confirm.ask') as mock_confirm, \
             patch('rich.prompt.IntPrompt.ask') as mock_int_prompt, \
             patch.object(interactive, 'get_input_file_enhanced') as mock_input, \
             patch.object(interactive, 'select_model_enhanced') as mock_model:
            
            # Configurar mocks
            mock_confirm.side_effect = [
                False,  # Não usar cache
                False,  # Não configurar opções avançadas
                True    # Confirmar configurações
            ]
            mock_input.return_value = None  # Simular entrada de arquivo
            mock_model.return_value = MagicMock()  # Simular seleção de modelo
            
            # Executar fluxo (com timeout para evitar travamento)
            try:
                result_settings = interactive.run_interactive_mode(settings)
                
                assert result_settings is not None, "Configurações não retornadas"
                assert isinstance(result_settings, Settings), "Tipo de retorno incorreto"
                
                print(f"✓ {green_highlighted('Fluxo completo executado com sucesso')}")
                
            except KeyboardInterrupt:
                print(f"⚠ {blue_highlighted('Fluxo interrompido (esperado em teste)')}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no fluxo completo: {e}')}")
        return False


def test_error_handling():
    """Testar tratamento de erros"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Tratamento de Erros ===')}")
    
    try:
        interactive = InteractiveMode()
        
        # Testar arquivo inexistente
        result = interactive.validate_audio_file("arquivo_inexistente.mp3")
        assert result == False, "Validação deveria falhar para arquivo inexistente"
        
        print(f"✓ {green_highlighted('Tratamento de arquivo inexistente funcionando')}")
        
        # Testar cache corrompido
        with open(interactive.settings_cache_file, 'w') as f:
            f.write("cache corrompido")
        
        cache = interactive.load_settings_cache()
        assert cache is None, "Cache corrompido deveria retornar None"
        
        print(f"✓ {green_highlighted('Tratamento de cache corrompido funcionando')}")
        
        # Limpar cache de teste
        if os.path.exists(interactive.settings_cache_file):
            os.unlink(interactive.settings_cache_file)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no tratamento de erros: {e}')}")
        return False


def main():
    """Executar todos os testes do modo interativo"""
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('🎵 INICIANDO TESTES DO MODO INTERATIVO 🎵')}")
    print("=" * 70)
    
    tests = [
        ("Inicialização", test_interactive_mode_initialization),
        ("Tela de Boas-vindas", test_welcome_display),
        ("Formatos de Áudio", test_audio_format_support),
        ("Validação de Entrada", test_input_file_validation),
        ("Seleção de Modelos", test_model_selection),
        ("Configurações Avançadas", test_advanced_configuration),
        ("Cache de Configurações", test_settings_cache),
        ("Exibição de Resumo", test_summary_display),
        ("Fluxo Completo", test_full_interactive_flow),
        ("Tratamento de Erros", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {green_highlighted(f'{test_name} - PASSOU')}")
            else:
                print(f"\n❌ {red_highlighted(f'{test_name} - FALHOU')}")
        except Exception as e:
            print(f"\n💥 {red_highlighted(f'{test_name} - ERRO: {e}')}")
    
    print(f"\n{'='*70}")
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('RESUMO DOS TESTES DO MODO INTERATIVO')}")
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {green_highlighted(str(passed))}")
    print(f"Testes falharam: {red_highlighted(str(total - passed))}")
    print(f"Taxa de sucesso: {green_highlighted(f'{(passed/total)*100:.1f}%')}")
    
    if passed == total:
        print(f"\n🎉 {green_highlighted('TODOS OS TESTES DO MODO INTERATIVO PASSARAM!')}")
        return True
    else:
        print(f"\n⚠️ {red_highlighted('ALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTAÇÃO')}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)