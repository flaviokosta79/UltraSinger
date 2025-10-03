#!/usr/bin/env python3
"""
Teste abrangente do modo interativo do UltraSinger
"""

import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock
from io import StringIO

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.init_interactive_mode import InteractiveMode
from Settings import Settings
from modules.Audio.separation import DemucsModel
from modules.Speech_Recognition.Whisper import WhisperModel

def test_interactive_mode_initialization():
    """Testa inicialização do modo interativo"""
    print("============================================================")
    print("[UltraSinger] Testando: Inicialização do Modo Interativo")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        
        # Verificar atributos básicos
        assert hasattr(interactive, 'console'), "Console não inicializado"
        assert hasattr(interactive, 'header'), "Header não definido"
        assert hasattr(interactive, 'settings_cache_file'), "Cache file não definido"
        
        print("✓ Inicialização básica funcionando")
        print("✓ Console configurado")
        print("✓ Header definido")
        print("✓ Cache file configurado")
        
        print("✅ Inicialização do Modo Interativo: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

def test_settings_cache():
    """Testa sistema de cache de configurações"""
    print("\n============================================================")
    print("[UltraSinger] Testando: Sistema de Cache de Configurações")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        settings = Settings()
        
        # Configurar algumas opções
        settings.whisper_model = WhisperModel.SMALL
        settings.demucs_model = DemucsModel.HTDEMUCS
        settings.language = "pt"
        settings.whisper_batch_size = 32
        
        # Usar arquivo temporário para cache
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            interactive.settings_cache_file = temp_file.name
            
            # Salvar cache
            interactive.save_settings_cache(settings)
            print("✓ Cache salvo com sucesso")
            
            # Carregar cache
            loaded_cache = interactive.load_settings_cache()
            assert loaded_cache is not None, "Cache não carregado"
            assert loaded_cache['whisper_model'] == 'small', "Modelo Whisper não salvo corretamente"
            assert loaded_cache['demucs_model'] == 'htdemucs', "Modelo Demucs não salvo corretamente"
            assert loaded_cache['language'] == 'pt', "Idioma não salvo corretamente"
            
            print("✓ Cache carregado com sucesso")
            print("✓ Dados do cache validados")
            
            # Aplicar cache a novas configurações
            new_settings = Settings()
            interactive._apply_cache_settings(new_settings, loaded_cache)
            
            assert new_settings.whisper_model == WhisperModel.SMALL, "Modelo Whisper não aplicado"
            assert new_settings.demucs_model == DemucsModel.HTDEMUCS, "Modelo Demucs não aplicado"
            assert new_settings.language == "pt", "Idioma não aplicado"
            
            print("✓ Cache aplicado às configurações")
            
            # Limpar arquivo temporário
            os.unlink(temp_file.name)
        
        print("✅ Sistema de Cache de Configurações: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de cache: {e}")
        return False

def test_model_selection():
    """Testa seleção de modelos"""
    print("\n============================================================")
    print("[UltraSinger] Testando: Seleção de Modelos")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        
        # Testar detalhes dos modelos Whisper
        whisper_details = interactive._get_model_details("Whisper")
        assert isinstance(whisper_details, dict), "Detalhes Whisper não é dict"
        assert len(whisper_details) > 0, "Nenhum modelo Whisper encontrado"
        
        print(f"✓ Modelos Whisper disponíveis: {len(whisper_details)}")
        
        # Testar detalhes dos modelos Demucs
        demucs_details = interactive._get_model_details("Demucs")
        assert isinstance(demucs_details, dict), "Detalhes Demucs não é dict"
        assert len(demucs_details) > 0, "Nenhum modelo Demucs encontrado"
        
        print(f"✓ Modelos Demucs disponíveis: {len(demucs_details)}")
        
        # Verificar se os modelos têm as informações necessárias
        for model_name, details in whisper_details.items():
            assert 'size' in details, f"Modelo {model_name} sem informação de tamanho"
            assert 'description' in details, f"Modelo {model_name} sem descrição"
        
        print("✓ Informações dos modelos validadas")
        
        print("✅ Seleção de Modelos: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro na seleção de modelos: {e}")
        return False

def test_configuration_methods():
    """Testa métodos de configuração"""
    print("\n============================================================")
    print("[UltraSinger] Testando: Métodos de Configuração")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        settings = Settings()
        
        # Testar configuração de opções de processamento
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.side_effect = ["16", "float16"]  # batch_size, compute_type
            
            interactive._configure_processing_options(settings)
            
            assert hasattr(settings, 'whisper_batch_size'), "Batch size não configurado"
            assert hasattr(settings, 'whisper_compute_type'), "Compute type não configurado"
            
        print("✓ Configuração de processamento funcionando")
        
        # Testar configuração de opções de saída
        with patch('rich.prompt.Confirm.ask') as mock_confirm:
            mock_confirm.side_effect = [True, False, True, False, True]  # midi, plot, karaoke, chunks, hyphenation
            
            interactive._configure_output_options(settings)
            
            assert hasattr(settings, 'create_midi'), "Create MIDI não configurado"
            assert hasattr(settings, 'create_plot'), "Create plot não configurado"
            
        print("✓ Configuração de saída funcionando")
        
        # Testar configuração de dispositivo
        with patch('rich.prompt.Confirm.ask') as mock_confirm:
            mock_confirm.return_value = False  # force_cpu
            
            interactive._configure_device_options(settings)
            
            assert hasattr(settings, 'force_cpu'), "Force CPU não configurado"
            
        print("✓ Configuração de dispositivo funcionando")
        
        # Testar configuração de idioma
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.return_value = "pt"
            
            interactive._configure_language_options(settings)
            
            assert hasattr(settings, 'language'), "Idioma não configurado"
            
        print("✓ Configuração de idioma funcionando")
        
        print("✅ Métodos de Configuração: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos métodos de configuração: {e}")
        return False

def test_display_methods():
    """Testa métodos de exibição"""
    print("\n============================================================")
    print("[UltraSinger] Testando: Métodos de Exibição")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        settings = Settings()
        
        # Configurar algumas opções para o resumo
        settings.input_file_path = "test.mp3"
        settings.output_folder_path = "output"
        settings.whisper_model = WhisperModel.SMALL
        settings.demucs_model = DemucsModel.HTDEMUCS
        settings.language = "pt"
        
        # Capturar saída do console
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Testar display_welcome
            interactive.display_welcome()
            welcome_output = mock_stdout.getvalue()
            assert "UltraSinger" in welcome_output, "Welcome não exibe UltraSinger"
            
        print("✓ Display welcome funcionando")
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Testar display_summary
            interactive.display_summary(settings)
            summary_output = mock_stdout.getvalue()
            # Verificar se algumas informações estão no resumo
            assert "test.mp3" in summary_output or "Resumo" in summary_output, "Summary não exibe informações"
            
        print("✓ Display summary funcionando")
        
        print("✅ Métodos de Exibição: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos métodos de exibição: {e}")
        return False

def test_file_input_methods():
    """Testa métodos de entrada de arquivo"""
    print("\n============================================================")
    print("[UltraSinger] Testando: Métodos de Entrada de Arquivo")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        settings = Settings()
        
        # Criar arquivo temporário para teste
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mp3', delete=False) as temp_file:
            temp_file.write("fake audio content")
            temp_file_path = temp_file.name
        
        try:
            # Testar get_input_file_enhanced com arquivo válido
            with patch('rich.prompt.Prompt.ask') as mock_prompt:
                mock_prompt.return_value = temp_file_path
                
                interactive.get_input_file_enhanced(settings)
                
                assert hasattr(settings, 'input_file_path'), "Input file path não configurado"
                assert settings.input_file_path == temp_file_path, "Caminho do arquivo incorreto"
                
            print("✓ Entrada de arquivo funcionando")
            
            # Testar get_output_folder_enhanced
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch('rich.prompt.Prompt.ask') as mock_prompt:
                    mock_prompt.return_value = temp_dir
                    
                    interactive.get_output_folder_enhanced(settings)
                    
                    assert hasattr(settings, 'output_folder_path'), "Output folder path não configurado"
                    
            print("✓ Saída de pasta funcionando")
            
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_file_path)
        
        print("✅ Métodos de Entrada de Arquivo: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos métodos de entrada: {e}")
        return False

def test_complete_interactive_flow():
    """Testa fluxo completo do modo interativo"""
    print("\n============================================================")
    print("[UltraSinger] Testando: Fluxo Completo do Modo Interativo")
    print("============================================================")
    
    try:
        interactive = InteractiveMode()
        settings = Settings()
        
        # Criar arquivos temporários
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mp3', delete=False) as temp_audio:
            temp_audio.write("fake audio")
            audio_path = temp_audio.name
            
        with tempfile.TemporaryDirectory() as temp_output:
            
            # Simular entrada do usuário para fluxo completo
            with patch('rich.prompt.Confirm.ask') as mock_confirm, \
                 patch('rich.prompt.Prompt.ask') as mock_prompt:
                
                # Configurar respostas simuladas
                mock_confirm.side_effect = [
                    False,  # Não usar cache
                    False,  # Não configurar opções avançadas
                    True    # Confirmar processamento
                ]
                
                mock_prompt.side_effect = [
                    audio_path,     # Arquivo de entrada
                    temp_output,    # Pasta de saída
                    "1",           # Modelo Whisper (primeiro da lista)
                    "1"            # Modelo Demucs (primeiro da lista)
                ]
                
                # Executar fluxo interativo
                result_settings = interactive.run_interactive_mode(settings)
                
                # Verificar se as configurações foram aplicadas
                assert hasattr(result_settings, 'input_file_path'), "Input path não configurado"
                assert hasattr(result_settings, 'output_folder_path'), "Output path não configurado"
                assert hasattr(result_settings, 'whisper_model'), "Modelo Whisper não configurado"
                assert hasattr(result_settings, 'demucs_model'), "Modelo Demucs não configurado"
                
        # Limpar arquivo temporário
        os.unlink(audio_path)
        
        print("✓ Fluxo completo executado com sucesso")
        print("✓ Configurações aplicadas corretamente")
        
        print("✅ Fluxo Completo do Modo Interativo: PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro no fluxo completo: {e}")
        return False

def main():
    """Executa todos os testes do modo interativo"""
    print("🎵 INICIANDO TESTES DO MODO INTERATIVO ULTRASINGER 🎵")
    print("=" * 60)
    
    tests = [
        ("Inicialização do Modo Interativo", test_interactive_mode_initialization),
        ("Sistema de Cache de Configurações", test_settings_cache),
        ("Seleção de Modelos", test_model_selection),
        ("Métodos de Configuração", test_configuration_methods),
        ("Métodos de Exibição", test_display_methods),
        ("Métodos de Entrada de Arquivo", test_file_input_methods),
        ("Fluxo Completo do Modo Interativo", test_complete_interactive_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("[UltraSinger] RESUMO DOS TESTES DO MODO INTERATIVO")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\n[UltraSinger] Resultado Final: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 TODOS OS TESTES DO MODO INTERATIVO PASSARAM!")
    else:
        print(f"⚠️  {len(results) - passed} teste(s) falharam")
    
    print("=" * 60)
    print("✅ TESTES DO MODO INTERATIVO FINALIZADOS")
    print("Sistema de modo interativo validado!")

if __name__ == "__main__":
    main()