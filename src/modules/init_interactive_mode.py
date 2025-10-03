from rich.console import Console  
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from Settings import Settings  
from modules.Audio.separation import DemucsModel
from modules.Speech_Recognition.Whisper import WhisperModel
from modules.DeviceDetection.device_detection import check_gpu_support
from modules.console_colors import green_highlighted, red_highlighted, yellow_highlighted, blue_highlighted

import os
import sys
import time
import urllib.parse
import json
from pathlib import Path
from typing import Optional, Dict, Any  
  
def get_input_file(console, settings, header):  
    while True:  
        input_file = console.input(f"{header} Enter the path to the input file ([green]audio file[/green], [green]Ultrastar txt[/green], or [green]YouTube URL[/green]): ").strip()  
        if input_file:  
            settings.input_file_path = input_file 
            print(settings.input_file_path) 
            break  
        else:  
            console.print(f"{header} [bold red]Error:[/bold red] Input file cannot be empty. Please try again.\n")  
  
def get_output_folder(console, settings, header):  
    output_folder = console.input(f"{header} Enter the output folder path (leave empty for default '[green]output[/green]' folder): ").strip()  
    if output_folder:  
        settings.output_folder_path = output_folder  
    else:  
        dirname = os.getcwd() if settings.input_file_path.startswith("https:") else os.path.dirname(settings.input_file_path)  
        settings.output_folder_path = os.path.join(dirname, "output")  
  
def select_model(console, header, model_enum, model_type, default_model):  
    models = [model.value for model in model_enum]  
    console.print(f"\n{header} [bold underline]Available {model_type} Models:[/bold underline]\n")  
  
    num_columns = 4  
    table = Table(show_header=False, show_edge=False, padding=(0, 2))  
    for _ in range(num_columns):  
        table.add_column()  
  
    items = [f"[bright_green]{idx}.[/bright_green] {model_name}" for idx, model_name in enumerate(models, start=1)]  
    rows = [items[i:i + num_columns] for i in range(0, len(items), num_columns)]  
    for row in rows:  
        row += [""] * (num_columns - len(row))  
        table.add_row(*row)  
    console.print(table)  
  
    while True:  
        choice = console.input(f"\n{header} Enter the [green]{model_type} model[/green] number corresponding to your choice (1-{len(models)}), or leave empty for default ([cyan]{default_model.value}[/cyan]): ").strip()  
        if not choice:  
            return default_model  
        elif choice.isdigit() and 1 <= int(choice) <= len(models):  
            return model_enum(models[int(choice) - 1])  
        else:  
            console.print(f"{header} [bold red]Error:[/bold red] Invalid choice. Please select a valid number.\n")  
  
def configure_additional_options(console, settings, header):  
    additional_options_input = console.input(  
        f"\n{header} Do you want to configure [green]additional options[/green]? "  
        f"([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
    ).strip().lower()  
  
    if additional_options_input == 'y':  
        console.print(f"\n{header} [bold underline]Additional options:[/bold underline]\n")  

        # Whisper Batch Size  
        whipser_batch_size_response = console.input(  
            f"{header} Enter the [green]Whisper batch size[/green] (default [cyan]16[/cyan]): "  
        ).strip()  
        settings.whisper_batch_size = int(whipser_batch_size_response) if whipser_batch_size_response.isdigit() else 16  
  
        # Whisper Compute Type  
        whisper_compute_choice = console.input(
            f"{header} Enter the [green]Whisper compute type[/green] (default '[cyan]float16[/cyan]' for CUDA and '[cyan]int8[/cyan]' for CPU): "  
        ).strip()  
        if whisper_compute_choice:  
            settings.whisper_compute_type = whisper_compute_choice  
  
        # Create Plot  
        settings.create_plot = console.input(  
            f"{header} Create [green]plot[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Create MIDI  
        settings.create_midi = not (console.input(  
            f"{header} Create [green]MIDI file[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_green]y[/bright_green]'): "  
        ).strip().lower() == 'n')  
  
        # Disable Hyphenation  
        settings.hyphenation = not (console.input(  
            f"{header} Disable [green]hyphenation[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y')  
  
        # Disable Vocal Separation  
        settings.use_separated_vocal = not (console.input(  
            f"{header} Disable [green]vocal separation[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y')  
  
        # Disable Karaoke Creation  
        settings.create_karaoke = not (console.input(  
            f"{header} Disable [green]karaoke creation[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y')  
  
        # Create Audio Chunks  
        settings.create_audio_chunks = console.input(  
            f"{header} Create [green]audio chunks[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Ignore Audio  
        settings.ignore_audio = console.input(  
            f"{header} Ignore [green]audio[/green] and use Ultrastar txt only? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Force CPU Usage  
        settings.force_cpu = console.input(  
            f"{header} Force [green]CPU usage[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Device settings based on CPU usage  
        if settings.force_cpu:  
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  
        else:  
            settings.tensorflow_device, settings.pytorch_device = check_gpu_support()  
  
        # Force Whisper CPU Usage  
        settings.force_whisper_cpu = console.input(  
            f"{header} Force [green]Whisper CPU usage[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Force Crepe CPU Usage  
        settings.force_crepe_cpu = console.input(  
            f"{header} Force [green]Crepe CPU usage[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Keep Cache  
        settings.keep_cache = console.input(  
            f"{header} Keep [green]cache[/green] after execution? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower() == 'y'  
  
        # Language  
        language = console.input(  
            f"\n{header} Enter the [green]language code[/green] (e.g., '[cyan]en[/cyan]' for English, '[cyan]es[/cyan]' for Spanish) or leave empty for [cyan]auto-detect[/cyan]: "  
        ).strip()  
        if language:  
            settings.language = language  
  
        # Transcribe Numbers as Numerics  
        keep_numbers_input = console.input(  
            f"\n{header} Do you want to transcribe [green]numbers as numerics[/green]? ([bright_green]y[/bright_green]/[bright_red]n[/bright_red], default '[bright_red]n[/bright_red]'): "  
        ).strip().lower()  
        settings.keep_numbers = keep_numbers_input == 'y'  
  
        # MuseScore Path  
        musescore_path = console.input(  
            f"\n{header} Enter the path to [green]MuseScore executable[/green] for sheet generation (leave empty to skip): "  
        ).strip()  
        if musescore_path:  
            settings.musescore_path = musescore_path  
  
        # Cookie File for YouTube Downloads  
        cookie_file = console.input(  
            f"\n{header} Enter the path to [green]cookies.txt[/green] file (if required for YouTube downloads, leave empty otherwise): "  
        ).strip()  
        if cookie_file:  
            settings.cookiefile = cookie_file

        # FFmpeg executable path
        ffmpeg_path = console.input(
            f"\n{header} Enter the path to [green]ffmpeg[/green] executable folder (leave empty for default): "
        ).strip()
        if ffmpeg_path:
            settings.ffmpeg_path = ffmpeg_path
  
class InteractiveMode:
    """Classe para gerenciar o modo interativo do UltraSinger"""
    
    def __init__(self):
        self.console = Console()
        self.header = "[bold green][UltraSinger][/bold green]"
        self.settings_cache_file = "interactive_settings_cache.json"
        
    def display_welcome(self):
        """Exibe a tela de boas-vindas"""
        welcome_text = Text()
        welcome_text.append("🎵 UltraSinger Interactive Mode 🎵\n", style="bold magenta")
        welcome_text.append("Transforme áudio em arquivos UltraStar com IA!", style="cyan")
        
        panel = Panel(
            welcome_text,
            title="Bem-vindo",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(panel)
        
    def validate_file_path(self, file_path: str) -> bool:
        """Valida se o caminho do arquivo existe"""
        if file_path.startswith("http"):
            return True  # URLs são válidas
        return os.path.exists(file_path)
        
    def validate_youtube_url(self, url: str) -> bool:
        """Valida se a URL do YouTube é válida"""
        youtube_domains = ["youtube.com", "youtu.be", "m.youtube.com"]
        try:
            parsed = urllib.parse.urlparse(url)
            return any(domain in parsed.netloc for domain in youtube_domains)
        except:
            return False
            
    def get_supported_audio_formats(self) -> list:
        """Retorna lista de formatos de áudio suportados"""
        return ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma']
        
    def validate_audio_file(self, file_path: str) -> bool:
        """Valida se o arquivo é um formato de áudio suportado"""
        if file_path.startswith("http"):
            return True
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_supported_audio_formats()
        
    def get_input_file_enhanced(self, settings: Settings) -> None:
        """Obtém o arquivo de entrada com validação aprimorada"""
        self.console.print(f"\n{self.header} [bold underline]Seleção do Arquivo de Entrada[/bold underline]\n")
        
        # Mostrar formatos suportados
        formats_text = ", ".join(self.get_supported_audio_formats())
        self.console.print(f"[dim]Formatos suportados: {formats_text}[/dim]")
        self.console.print("[dim]Também aceita: URLs do YouTube, arquivos UltraStar.txt[/dim]\n")
        
        while True:
            input_file = Prompt.ask(
                f"{self.header} Caminho do arquivo",
                default="",
                show_default=False
            ).strip()
            
            if not input_file:
                self.console.print(f"{self.header} [bold red]Erro:[/bold red] Arquivo de entrada é obrigatório.\n")
                continue
                
            # Validar URL do YouTube
            if input_file.startswith("http"):
                if self.validate_youtube_url(input_file):
                    settings.input_file_path = input_file
                    self.console.print(f"{self.header} [green]✓[/green] URL do YouTube válida")
                    break
                else:
                    self.console.print(f"{self.header} [bold red]Erro:[/bold red] URL do YouTube inválida.\n")
                    continue
                    
            # Validar arquivo local
            if not self.validate_file_path(input_file):
                self.console.print(f"{self.header} [bold red]Erro:[/bold red] Arquivo não encontrado: {input_file}\n")
                continue
                
            # Validar formato de áudio
            if input_file.endswith('.txt'):
                settings.input_file_path = input_file
                self.console.print(f"{self.header} [green]✓[/green] Arquivo UltraStar.txt detectado")
                break
            elif self.validate_audio_file(input_file):
                settings.input_file_path = input_file
                self.console.print(f"{self.header} [green]✓[/green] Arquivo de áudio válido")
                break
            else:
                self.console.print(f"{self.header} [bold red]Erro:[/bold red] Formato de arquivo não suportado.\n")
                
    def get_output_folder_enhanced(self, settings: Settings) -> None:
        """Obtém a pasta de saída com validação"""
        self.console.print(f"\n{self.header} [bold underline]Pasta de Saída[/bold underline]\n")
        
        # Sugerir pasta padrão
        if settings.input_file_path.startswith("https:"):
            default_output = os.path.join(os.getcwd(), "output")
        else:
            default_output = os.path.join(os.path.dirname(settings.input_file_path), "output")
            
        output_folder = Prompt.ask(
            f"{self.header} Pasta de saída",
            default=default_output
        ).strip()
        
        # Criar pasta se não existir
        try:
            os.makedirs(output_folder, exist_ok=True)
            settings.output_folder_path = output_folder
            self.console.print(f"{self.header} [green]✓[/green] Pasta de saída: {output_folder}")
        except Exception as e:
            self.console.print(f"{self.header} [bold red]Erro:[/bold red] Não foi possível criar a pasta: {e}")
            settings.output_folder_path = default_output
            os.makedirs(settings.output_folder_path, exist_ok=True)
            
    def select_model_enhanced(self, model_enum, model_type: str, default_model, show_details: bool = True):
        """Seleção de modelo aprimorada com detalhes"""
        models = list(model_enum)
        
        self.console.print(f"\n{self.header} [bold underline]Seleção do Modelo {model_type}[/bold underline]\n")
        
        if show_details:
            # Mostrar detalhes dos modelos
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Nº", style="cyan", width=3)
            table.add_column("Modelo", style="green")
            table.add_column("Qualidade", style="yellow")
            table.add_column("Velocidade", style="blue")
            table.add_column("Memória", style="red")
            
            model_details = self._get_model_details(model_type)
            
            for idx, model in enumerate(models, 1):
                details = model_details.get(model.value, {})
                table.add_row(
                    str(idx),
                    model.value,
                    details.get("quality", "N/A"),
                    details.get("speed", "N/A"),
                    details.get("memory", "N/A")
                )
                
            self.console.print(table)
        else:
            # Mostrar lista simples
            for idx, model in enumerate(models, 1):
                self.console.print(f"[bright_green]{idx}.[/bright_green] {model.value}")
                
        while True:
            choice = Prompt.ask(
                f"\n{self.header} Escolha o modelo {model_type}",
                default=str(models.index(default_model) + 1),
                show_default=True
            ).strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(models):
                selected_model = models[int(choice) - 1]
                self.console.print(f"{self.header} [green]✓[/green] Modelo selecionado: {selected_model.value}")
                return selected_model
            else:
                self.console.print(f"{self.header} [bold red]Erro:[/bold red] Escolha inválida. Digite um número de 1 a {len(models)}.\n")
                
    def _get_model_details(self, model_type: str) -> Dict[str, Dict[str, str]]:
        """Retorna detalhes dos modelos"""
        if model_type == "Whisper":
            return {
                "tiny": {"quality": "Baixa", "speed": "Muito Rápida", "memory": "~1GB"},
                "base": {"quality": "Média", "speed": "Rápida", "memory": "~1GB"},
                "small": {"quality": "Boa", "speed": "Média", "memory": "~2GB"},
                "medium": {"quality": "Muito Boa", "speed": "Lenta", "memory": "~5GB"},
                "large": {"quality": "Excelente", "speed": "Muito Lenta", "memory": "~10GB"},
                "large-v2": {"quality": "Excelente+", "speed": "Muito Lenta", "memory": "~10GB"},
                "large-v3": {"quality": "Superior", "speed": "Muito Lenta", "memory": "~10GB"}
            }
        elif model_type == "Demucs":
            return {
                "htdemucs": {"quality": "Excelente", "speed": "Lenta", "memory": "~8GB"},
                "htdemucs_ft": {"quality": "Superior", "speed": "Muito Lenta", "memory": "~10GB"},
                "htdemucs_6s": {"quality": "Boa", "speed": "Média", "memory": "~6GB"},
                "hdemucs_mmi": {"quality": "Muito Boa", "speed": "Lenta", "memory": "~8GB"},
                "mdx": {"quality": "Boa", "speed": "Rápida", "memory": "~4GB"},
                "mdx_extra": {"quality": "Muito Boa", "speed": "Média", "memory": "~6GB"}
            }
        return {}
        
    def configure_advanced_options_enhanced(self, settings: Settings) -> None:
        """Configuração de opções avançadas aprimorada"""
        if not Confirm.ask(f"\n{self.header} Configurar opções avançadas?", default=False):
            return
            
        self.console.print(f"\n{self.header} [bold underline]Configurações Avançadas[/bold underline]\n")
        
        # Configurações de processamento
        self._configure_processing_options(settings)
        
        # Configurações de saída
        self._configure_output_options(settings)
        
        # Configurações de dispositivo
        self._configure_device_options(settings)
        
        # Configurações de idioma
        self._configure_language_options(settings)
        
        # Configurações de ferramentas externas
        self._configure_external_tools(settings)
        
    def _configure_processing_options(self, settings: Settings) -> None:
        """Configurar opções de processamento"""
        self.console.print("[bold cyan]Opções de Processamento:[/bold cyan]")
        
        # Whisper batch size
        batch_size = Prompt.ask(
            "Tamanho do batch do Whisper",
            default="16"
        )
        if batch_size.isdigit():
            settings.whisper_batch_size = int(batch_size)
            
        # Whisper compute type
        compute_types = ["float16", "float32", "int8"]
        self.console.print(f"Tipos de computação disponíveis: {', '.join(compute_types)}")
        compute_type = Prompt.ask(
            "Tipo de computação do Whisper",
            default="float16" if not getattr(settings, 'force_cpu', False) else "int8",
            choices=compute_types
        )
        settings.whisper_compute_type = compute_type
        
        # Separação vocal
        settings.use_separated_vocal = Confirm.ask(
            "Usar separação vocal?", 
            default=True
        )
        
        # Manter cache
        settings.keep_cache = Confirm.ask(
            "Manter cache após execução?", 
            default=False
        )
        
    def _configure_output_options(self, settings: Settings) -> None:
        """Configurar opções de saída"""
        self.console.print("\n[bold cyan]Opções de Saída:[/bold cyan]")
        
        settings.create_midi = Confirm.ask("Criar arquivo MIDI?", default=True)
        settings.create_plot = Confirm.ask("Criar gráfico de pitch?", default=False)
        settings.create_karaoke = Confirm.ask("Criar arquivo de karaokê?", default=True)
        settings.create_audio_chunks = Confirm.ask("Criar chunks de áudio?", default=False)
        settings.hyphenation = Confirm.ask("Usar hifenização?", default=True)
        
    def _configure_device_options(self, settings: Settings) -> None:
        """Configurar opções de dispositivo"""
        self.console.print("\n[bold cyan]Configurações de Dispositivo:[/bold cyan]")
        
        # Verificar suporte GPU
        gpu_available = check_gpu_support()[0] != "cpu"
        if gpu_available:
            self.console.print("[green]✓[/green] GPU detectada e disponível")
        else:
            self.console.print("[yellow]⚠[/yellow] GPU não detectada, usando CPU")
            
        settings.force_cpu = Confirm.ask("Forçar uso de CPU?", default=not gpu_available)
        
        if not settings.force_cpu and gpu_available:
            settings.force_whisper_cpu = Confirm.ask("Forçar Whisper na CPU?", default=False)
            settings.force_crepe_cpu = Confirm.ask("Forçar Crepe na CPU?", default=False)
        else:
            settings.force_whisper_cpu = True
            settings.force_crepe_cpu = True
            
        # Configurar dispositivos
        if settings.force_cpu:
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        else:
            settings.tensorflow_device, settings.pytorch_device = check_gpu_support()
            
    def _configure_language_options(self, settings: Settings) -> None:
        """Configurar opções de idioma"""
        self.console.print("\n[bold cyan]Configurações de Idioma:[/bold cyan]")
        
        # Lista de idiomas comuns
        common_languages = {
            "auto": "Detecção automática",
            "pt": "Português",
            "en": "Inglês", 
            "es": "Espanhol",
            "fr": "Francês",
            "de": "Alemão",
            "it": "Italiano",
            "ja": "Japonês",
            "ko": "Coreano",
            "zh": "Chinês"
        }
        
        self.console.print("Idiomas disponíveis:")
        for code, name in common_languages.items():
            self.console.print(f"  [cyan]{code}[/cyan]: {name}")
            
        language = Prompt.ask(
            "Código do idioma",
            default="auto"
        ).strip().lower()
        
        if language and language != "auto":
            settings.language = language
            
        # Números como numerais
        settings.keep_numbers = Confirm.ask(
            "Transcrever números como numerais?", 
            default=False
        )
        
    def _configure_external_tools(self, settings: Settings) -> None:
        """Configurar ferramentas externas"""
        self.console.print("\n[bold cyan]Ferramentas Externas:[/bold cyan]")
        
        # MuseScore
        musescore_path = Prompt.ask(
            "Caminho do MuseScore (para partituras)",
            default=""
        ).strip()
        if musescore_path and os.path.exists(musescore_path):
            settings.musescore_path = musescore_path
            
        # Cookies para YouTube
        cookie_file = Prompt.ask(
            "Arquivo de cookies para YouTube",
            default=""
        ).strip()
        if cookie_file and os.path.exists(cookie_file):
            settings.cookiefile = cookie_file
            
        # FFmpeg
        ffmpeg_path = Prompt.ask(
            "Pasta do FFmpeg",
            default=""
        ).strip()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            settings.ffmpeg_path = ffmpeg_path
            
    def save_settings_cache(self, settings: Settings) -> None:
        """Salva configurações em cache"""
        try:
            cache_data = {
                "whisper_model": settings.whisper_model.value if hasattr(settings, 'whisper_model') else None,
                "demucs_model": settings.demucs_model.value if hasattr(settings, 'demucs_model') else None,
                "language": getattr(settings, 'language', 'auto'),
                "whisper_batch_size": getattr(settings, 'whisper_batch_size', 16),
                "whisper_compute_type": getattr(settings, 'whisper_compute_type', 'float16'),
                "force_cpu": getattr(settings, 'force_cpu', False),
                "keep_cache": getattr(settings, 'keep_cache', False),
                "create_midi": getattr(settings, 'create_midi', True),
                "create_plot": getattr(settings, 'create_plot', False),
                "hyphenation": getattr(settings, 'hyphenation', True),
                "timestamp": time.time()
            }
            
            with open(self.settings_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.console.print(f"[yellow]Aviso:[/yellow] Não foi possível salvar cache: {e}")
            
    def load_settings_cache(self) -> Optional[Dict[str, Any]]:
        """Carrega configurações do cache"""
        try:
            if os.path.exists(self.settings_cache_file):
                with open(self.settings_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
        
    def display_summary(self, settings: Settings) -> None:
        """Exibe resumo das configurações"""
        self.console.print(f"\n{self.header} [bold underline]Resumo das Configurações[/bold underline]\n")
        
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Configuração", style="cyan")
        summary_table.add_column("Valor", style="green")
        
        # Configurações principais
        summary_table.add_row("Arquivo de entrada", str(getattr(settings, 'input_file_path', 'N/A')))
        summary_table.add_row("Pasta de saída", str(getattr(settings, 'output_folder_path', 'N/A')))
        summary_table.add_row("Modelo Whisper", str(getattr(settings, 'whisper_model', 'N/A')))
        summary_table.add_row("Modelo Demucs", str(getattr(settings, 'demucs_model', 'N/A')))
        summary_table.add_row("Idioma", str(getattr(settings, 'language', 'auto')))
        summary_table.add_row("Usar GPU", "Não" if getattr(settings, 'force_cpu', False) else "Sim")
        summary_table.add_row("Criar MIDI", "Sim" if getattr(settings, 'create_midi', True) else "Não")
        summary_table.add_row("Separação vocal", "Sim" if getattr(settings, 'use_separated_vocal', True) else "Não")
        
        self.console.print(summary_table)
        
        # Confirmação final
        if not Confirm.ask(f"\n{self.header} Continuar com essas configurações?", default=True):
            self.console.print(f"{self.header} [yellow]Operação cancelada pelo usuário.[/yellow]")
            sys.exit(0)
            
    def run_interactive_mode(self, settings: Settings) -> Settings:
        """Executa o modo interativo completo"""
        try:
            self.display_welcome()
            
            # Carregar cache se disponível
            cache = self.load_settings_cache()
            if cache and Confirm.ask(f"{self.header} Usar configurações salvas?", default=False):
                self._apply_cache_settings(settings, cache)
                # Ainda precisamos do arquivo de entrada
                self.get_input_file_enhanced(settings)
                self.get_output_folder_enhanced(settings)
            else:
                # Configuração manual
                self.get_input_file_enhanced(settings)
                self.get_output_folder_enhanced(settings)
                
                settings.whisper_model = self.select_model_enhanced(
                    WhisperModel, "Whisper", WhisperModel.LARGE_V2
                )
                
                settings.demucs_model = self.select_model_enhanced(
                    DemucsModel, "Demucs", DemucsModel.HTDEMUCS
                )
                
                self.configure_advanced_options_enhanced(settings)
                
            # Salvar configurações
            self.save_settings_cache(settings)
            
            # Mostrar resumo
            self.display_summary(settings)
            
            # Mensagem final
            self.console.print(f"\n{self.header} [bold cyan]🚀 Iniciando processamento...[/bold cyan]\n")
            
            return settings
            
        except KeyboardInterrupt:
            self.console.print(f"\n{self.header} [yellow]Operação cancelada pelo usuário.[/yellow]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"\n{self.header} [bold red]Erro no modo interativo:[/bold red] {e}")
            sys.exit(1)
            
    def _apply_cache_settings(self, settings: Settings, cache: Dict[str, Any]) -> None:
        """Aplica configurações do cache"""
        try:
            if cache.get('whisper_model'):
                settings.whisper_model = WhisperModel(cache['whisper_model'])
            if cache.get('demucs_model'):
                settings.demucs_model = DemucsModel(cache['demucs_model'])
                
            settings.language = cache.get('language', 'auto')
            settings.whisper_batch_size = cache.get('whisper_batch_size', 16)
            settings.whisper_compute_type = cache.get('whisper_compute_type', 'float16')
            settings.force_cpu = cache.get('force_cpu', False)
            settings.keep_cache = cache.get('keep_cache', False)
            settings.create_midi = cache.get('create_midi', True)
            settings.create_plot = cache.get('create_plot', False)
            settings.hyphenation = cache.get('hyphenation', True)
            
            self.console.print(f"{self.header} [green]✓[/green] Configurações carregadas do cache")
            
        except Exception as e:
            self.console.print(f"{self.header} [yellow]Aviso:[/yellow] Erro ao carregar cache: {e}")

def init_settings_interactive(settings: Settings) -> Settings:
    """Função de entrada para o modo interativo (compatibilidade)"""
    interactive_mode = InteractiveMode()
    return interactive_mode.run_interactive_mode(settings)