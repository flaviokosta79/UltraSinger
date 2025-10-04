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
                "large-v3": {"quality": "Superior", "speed": "Muito Lenta", "memory": "~10GB"},
                "large-v3-turbo": {"quality": "Superior", "speed": "Ultra Rápida", "memory": "~6GB"}
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

    def configure_processing_jobs(self, settings: Settings) -> None:
        """Configurar quais jobs de processamento serão executados"""
        self.console.print(f"\n{self.header} [bold underline]Seleção de Jobs de Processamento[/bold underline]\n")

        # Criar tabela explicativa
        info_table = Table(show_header=True, header_style="bold magenta", title="Jobs Disponíveis")
        info_table.add_column("Job", style="cyan", width=25)
        info_table.add_column("Descrição", style="white", width=50)
        info_table.add_column("Padrão", style="green", width=8)

        info_table.add_row(
            "🎤 Separação Vocal",
            "Separa vocais do instrumental usando Demucs",
            "Sim"
        )
        info_table.add_row(
            "📝 Transcrição (Whisper)",
            "Transcreve letras da música automaticamente",
            "Sim"
        )
        info_table.add_row(
            "🎵 Detecção de Pitch (Crepe)",
            "Detecta as notas musicais cantadas",
            "Sim"
        )
        info_table.add_row(
            "🎹 Geração de MIDI",
            "Cria arquivo MIDI com as notas detectadas",
            "Não"
        )
        info_table.add_row(
            "📊 Geração de Gráficos",
            "Cria visualizações do pitch e timing",
            "Não"
        )
        info_table.add_row(
            "🎼 Partitura (MuseScore)",
            "Gera partitura em PDF (requer MuseScore)",
            "Não"
        )
        info_table.add_row(
            "✂️ Hifenização",
            "Divide palavras em sílabas para sincronização",
            "Sim"
        )

        self.console.print(info_table)
        self.console.print()

        # Perguntar se quer personalizar ou usar padrão
        use_custom = Confirm.ask(
            f"{self.header} Personalizar jobs de processamento?",
            default=False
        )

        if not use_custom:
            # Usar configurações padrão
            self.console.print(f"{self.header} [green]✓[/green] Usando configuração padrão de jobs")
            settings.use_separated_vocal = True
            settings.use_pitch_detection = True  # Crepe ativo
            settings.ignore_audio = False  # Usar Whisper
            settings.create_midi = False
            settings.create_plot = False
            settings.hyphenation = True
            # MuseScore não tem flag específica, será criado se musescore_path existir
            return

        # Configuração personalizada
        self.console.print(f"\n{self.header} [bold cyan]Configuração Personalizada de Jobs[/bold cyan]\n")

        # 1. Separação Vocal
        settings.use_separated_vocal = Confirm.ask(
            "🎤 Executar separação vocal com Demucs?",
            default=True
        )

        # 2. Transcrição
        use_transcription = Confirm.ask(
            "📝 Executar transcrição com Whisper?",
            default=True
        )

        if not use_transcription:
            self.console.print("[yellow]⚠ Aviso:[/yellow] Sem transcrição, você deve fornecer um arquivo UltraStar.txt existente")
            settings.ignore_audio = True
        else:
            settings.ignore_audio = False

        # 3. Detecção de Pitch
        settings.use_pitch_detection = Confirm.ask(
            "🎵 Executar detecção de pitch com Crepe?",
            default=True
        )

        if not settings.use_pitch_detection:
            self.console.print("[yellow]⚠ Aviso:[/yellow] Pitch detection é essencial para qualidade. Continuando sem ela...")
            self.console.print("[yellow]⚠ Aviso:[/yellow] Sem pitch detection, a geração de arquivos pode ser limitada")        # 4. Geração de MIDI
        settings.create_midi = Confirm.ask(
            "🎹 Gerar arquivo MIDI?",
            default=False
        )

        # 5. Geração de Gráficos
        settings.create_plot = Confirm.ask(
            "📊 Gerar gráficos de visualização?",
            default=False
        )

        # 6. Hifenização
        settings.hyphenation = Confirm.ask(
            "✂️ Aplicar hifenização nas letras?",
            default=True
        )

        # 7. Partitura
        create_sheet = Confirm.ask(
            "🎼 Gerar partitura em PDF? (requer MuseScore instalado)",
            default=False
        )
        settings.create_sheet = create_sheet

        if create_sheet and not settings.musescore_path:
            musescore_path = Prompt.ask(
                "Caminho do executável do MuseScore",
                default=""
            ).strip()
            if musescore_path and os.path.exists(musescore_path):
                settings.musescore_path = musescore_path
            else:
                self.console.print("[yellow]⚠ Aviso:[/yellow] Caminho do MuseScore inválido. Partitura não será gerada.")

        # 8. Audio chunks (opcional)
        settings.create_audio_chunks = Confirm.ask(
            "🔊 Criar chunks de áudio separados?",
            default=False
        )

        # 9. Karaoke
        settings.create_karaoke = Confirm.ask(
            "🎤 Criar arquivo de karaokê?",
            default=True
        )

        # Resumo dos jobs selecionados
        self.console.print(f"\n{self.header} [bold green]Jobs Selecionados:[/bold green]")
        jobs_summary = []
        if settings.use_separated_vocal:
            jobs_summary.append("✓ Separação Vocal")
        if not settings.ignore_audio:
            jobs_summary.append("✓ Transcrição (Whisper)")
        if settings.use_pitch_detection:
            jobs_summary.append("✓ Detecção de Pitch (Crepe)")
        if settings.create_midi:
            jobs_summary.append("✓ Geração MIDI")
        if settings.create_plot:
            jobs_summary.append("✓ Geração de Gráficos")
        if settings.hyphenation:
            jobs_summary.append("✓ Hifenização")
        if settings.musescore_path:
            jobs_summary.append("✓ Partitura PDF")
        if settings.create_audio_chunks:
            jobs_summary.append("✓ Audio Chunks")
        if settings.create_karaoke:
            jobs_summary.append("✓ Karaokê")

        for job in jobs_summary:
            self.console.print(f"  {job}")

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

        # Separação vocal
        settings.use_separated_vocal = Confirm.ask(
            "Usar separação vocal (Demucs)?",
            default=True
        )

        # Transcrição com Whisper
        use_whisper = Confirm.ask(
            "Usar transcrição com Whisper?",
            default=True
        )

        if use_whisper:
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
        else:
            # Se não usar Whisper, deve ignorar áudio ou ter um arquivo txt
            self.console.print("[yellow]⚠[/yellow] Sem transcrição Whisper, você deve fornecer um arquivo UltraStar.txt existente")
            settings.ignore_audio = True

        # Detecção de pitch com Crepe
        use_crepe = Confirm.ask(
            "Usar detecção de pitch com Crepe?",
            default=True
        )

        if use_crepe:
            # Crepe step size
            step_size = Prompt.ask(
                "Step size do Crepe (ms) - menor = mais preciso mas mais lento",
                default="10"
            )
            if step_size.isdigit():
                settings.crepe_step_size = int(step_size)

            # Crepe model capacity
            crepe_models = ["tiny", "small", "medium", "large", "full"]
            self.console.print(f"Modelos Crepe disponíveis: {', '.join(crepe_models)}")
            crepe_model = Prompt.ask(
                "Modelo Crepe",
                default="full",
                choices=crepe_models
            )
            settings.crepe_model_capacity = crepe_model
        else:
            self.console.print("[yellow]⚠[/yellow] Sem detecção de pitch, a qualidade do resultado pode ser comprometida")
            # Ainda executar mas com configurações mínimas

        # Manter cache
        settings.keep_cache = Confirm.ask(
            "Manter cache após execução?",
            default=False
        )

    def _configure_output_options(self, settings: Settings) -> None:
        """Configurar opções de saída (formato UltraStar)"""
        self.console.print("\n[bold cyan]Opções de Formato de Saída:[/bold cyan]")

        # Formato de versão UltraStar
        from modules.Ultrastar.ultrastar_txt import FormatVersion

        format_versions = ["0.3.0", "1.0.0", "1.1.0", "1.2.0"]
        self.console.print(f"Versões de formato UltraStar disponíveis: {', '.join(format_versions)}")
        format_choice = Prompt.ask(
            "Versão do formato UltraStar.txt",
            default="1.2.0",
            choices=format_versions
        )

        if format_choice == "0.3.0":
            settings.format_version = FormatVersion.V0_3_0
        elif format_choice == "1.0.0":
            settings.format_version = FormatVersion.V1_0_0
        elif format_choice == "1.1.0":
            settings.format_version = FormatVersion.V1_1_0
        else:
            settings.format_version = FormatVersion.V1_2_0

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
                # Modelos
                "whisper_model": settings.whisper_model.value if hasattr(settings, 'whisper_model') else None,
                "demucs_model": settings.demucs_model.value if hasattr(settings, 'demucs_model') else None,

                # Idioma
                "language": getattr(settings, 'language', 'auto'),

                # Configurações Whisper
                "whisper_batch_size": getattr(settings, 'whisper_batch_size', 16),
                "whisper_compute_type": getattr(settings, 'whisper_compute_type', 'float16'),

                # Configurações Crepe
                "crepe_model_capacity": getattr(settings, 'crepe_model_capacity', 'full'),
                "crepe_step_size": getattr(settings, 'crepe_step_size', 10),

                # Device
                "force_cpu": getattr(settings, 'force_cpu', False),
                "force_whisper_cpu": getattr(settings, 'force_whisper_cpu', False),
                "force_crepe_cpu": getattr(settings, 'force_crepe_cpu', False),

                # Jobs de processamento
                "use_separated_vocal": getattr(settings, 'use_separated_vocal', True),
                "use_pitch_detection": getattr(settings, 'use_pitch_detection', True),
                "ignore_audio": getattr(settings, 'ignore_audio', False),
                "create_midi": getattr(settings, 'create_midi', False),
                "create_plot": getattr(settings, 'create_plot', False),
                "create_sheet": getattr(settings, 'create_sheet', False),
                "hyphenation": getattr(settings, 'hyphenation', True),
                "create_karaoke": getattr(settings, 'create_karaoke', True),
                "create_audio_chunks": getattr(settings, 'create_audio_chunks', False),

                # Outros
                "keep_cache": getattr(settings, 'keep_cache', False),
                "keep_numbers": getattr(settings, 'keep_numbers', False),

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

        # Tabela de configurações gerais
        summary_table = Table(show_header=True, header_style="bold magenta", title="Configurações Gerais")
        summary_table.add_column("Configuração", style="cyan")
        summary_table.add_column("Valor", style="green")

        summary_table.add_row("📂 Arquivo de entrada", str(getattr(settings, 'input_file_path', 'N/A')))
        summary_table.add_row("📁 Pasta de saída", str(getattr(settings, 'output_folder_path', 'N/A')))
        summary_table.add_row("🌐 Idioma", str(getattr(settings, 'language', 'auto')))
        summary_table.add_row("⚡ Usar GPU", "Não" if getattr(settings, 'force_cpu', False) else "Sim")
        summary_table.add_row("💾 Manter cache", "Sim" if getattr(settings, 'keep_cache', False) else "Não")

        self.console.print(summary_table)
        self.console.print()

        # Tabela de jobs de processamento
        jobs_table = Table(show_header=True, header_style="bold cyan", title="Jobs de Processamento")
        jobs_table.add_column("Job", style="cyan", width=30)
        jobs_table.add_column("Status", style="white", width=10)
        jobs_table.add_column("Modelo/Config", style="yellow")

        # Separação Vocal
        if getattr(settings, 'use_separated_vocal', True):
            jobs_table.add_row(
                "🎤 Separação Vocal",
                "[green]✓ Ativo[/green]",
                str(getattr(settings, 'demucs_model', 'htdemucs'))
            )
        else:
            jobs_table.add_row("🎤 Separação Vocal", "[red]✗ Desativado[/red]", "-")

        # Transcrição
        if not getattr(settings, 'ignore_audio', False):
            jobs_table.add_row(
                "📝 Transcrição (Whisper)",
                "[green]✓ Ativo[/green]",
                str(getattr(settings, 'whisper_model', 'large-v2'))
            )
        else:
            jobs_table.add_row("📝 Transcrição (Whisper)", "[red]✗ Desativado[/red]", "-")

        # Detecção de Pitch
        if getattr(settings, 'use_pitch_detection', True):
            jobs_table.add_row(
                "🎵 Detecção de Pitch (Crepe)",
                "[green]✓ Ativo[/green]",
                f"{getattr(settings, 'crepe_model_capacity', 'full')} (step: {getattr(settings, 'crepe_step_size', 10)}ms)"
            )
        else:
            jobs_table.add_row("🎵 Detecção de Pitch (Crepe)", "[red]✗ Desativado[/red]", "-")

        # MIDI
        if getattr(settings, 'create_midi', False):
            jobs_table.add_row("🎹 Geração de MIDI", "[green]✓ Ativo[/green]", "-")
        else:
            jobs_table.add_row("🎹 Geração de MIDI", "[dim]○ Desativado[/dim]", "-")

        # Gráficos
        if getattr(settings, 'create_plot', False):
            jobs_table.add_row("📊 Geração de Gráficos", "[green]✓ Ativo[/green]", "-")
        else:
            jobs_table.add_row("📊 Geração de Gráficos", "[dim]○ Desativado[/dim]", "-")

        # Hifenização
        if getattr(settings, 'hyphenation', True):
            jobs_table.add_row("✂️ Hifenização", "[green]✓ Ativo[/green]", "-")
        else:
            jobs_table.add_row("✂️ Hifenização", "[dim]○ Desativado[/dim]", "-")

        # Karaoke
        if getattr(settings, 'create_karaoke', True):
            jobs_table.add_row("🎤 Arquivo Karaokê", "[green]✓ Ativo[/green]", "-")
        else:
            jobs_table.add_row("🎤 Arquivo Karaokê", "[dim]○ Desativado[/dim]", "-")

        # Partitura
        if getattr(settings, 'create_sheet', False):
            jobs_table.add_row("🎼 Partitura PDF", "[green]✓ Ativo[/green]", "MuseScore")
        else:
            jobs_table.add_row("🎼 Partitura PDF", "[dim]○ Desativado[/dim]", "-")

        self.console.print(jobs_table)

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

                # NOVA SEÇÃO: Seleção de Jobs de Processamento
                self.configure_processing_jobs(settings)

                # Seleção de modelos (apenas se os jobs correspondentes estiverem ativos)
                if not settings.ignore_audio:
                    settings.whisper_model = self.select_model_enhanced(
                        WhisperModel, "Whisper", WhisperModel.LARGE_V2
                    )

                if settings.use_separated_vocal:
                    settings.demucs_model = self.select_model_enhanced(
                        DemucsModel, "Demucs", DemucsModel.HTDEMUCS
                    )

                # Opções avançadas (configurações detalhadas)
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
            # Modelos
            if cache.get('whisper_model'):
                settings.whisper_model = WhisperModel(cache['whisper_model'])
            if cache.get('demucs_model'):
                settings.demucs_model = DemucsModel(cache['demucs_model'])

            # Idioma
            settings.language = cache.get('language', 'auto')

            # Configurações Whisper
            settings.whisper_batch_size = cache.get('whisper_batch_size', 16)
            settings.whisper_compute_type = cache.get('whisper_compute_type', 'float16')

            # Configurações Crepe
            settings.crepe_model_capacity = cache.get('crepe_model_capacity', 'full')
            settings.crepe_step_size = cache.get('crepe_step_size', 10)

            # Device
            settings.force_cpu = cache.get('force_cpu', False)
            settings.force_whisper_cpu = cache.get('force_whisper_cpu', False)
            settings.force_crepe_cpu = cache.get('force_crepe_cpu', False)

            # Jobs de processamento
            settings.use_separated_vocal = cache.get('use_separated_vocal', True)
            settings.use_pitch_detection = cache.get('use_pitch_detection', True)
            settings.ignore_audio = cache.get('ignore_audio', False)
            settings.create_midi = cache.get('create_midi', False)
            settings.create_plot = cache.get('create_plot', False)
            settings.create_sheet = cache.get('create_sheet', False)
            settings.hyphenation = cache.get('hyphenation', True)
            settings.create_karaoke = cache.get('create_karaoke', True)
            settings.create_audio_chunks = cache.get('create_audio_chunks', False)

            # Outros
            settings.keep_cache = cache.get('keep_cache', False)
            settings.keep_numbers = cache.get('keep_numbers', False)

            self.console.print(f"{self.header} [green]✓[/green] Configurações carregadas do cache")

        except Exception as e:
            self.console.print(f"{self.header} [yellow]Aviso:[/yellow] Erro ao carregar cache: {e}")

def init_settings_interactive(settings: Settings) -> Settings:
    """Função de entrada para o modo interativo (compatibilidade)"""
    interactive_mode = InteractiveMode()
    return interactive_mode.run_interactive_mode(settings)
