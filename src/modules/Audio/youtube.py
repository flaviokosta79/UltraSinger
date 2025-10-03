"""YouTube Downloader - Enhanced with comprehensive support"""

import os
import re
import json
import time
import urllib.parse
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
import yt_dlp

from modules.os_helper import sanitize_filename, get_unused_song_output_dir
from modules import os_helper
from modules.ProcessData import MediaInfo
from modules.Audio.bpm import get_bpm_from_file
from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, yellow_highlighted, blue_highlighted
from modules.Image.image_helper import save_image
from modules.musicbrainz_client import search_musicbrainz


class YouTubeDownloader:
    """Enhanced YouTube downloader with comprehensive support"""
    
    def __init__(self, cache_folder: Optional[str] = None):
        """Initialize YouTube downloader with cache support"""
        self.cache_folder = cache_folder or os.path.join(os.getcwd(), "cache", "youtube")
        self.validation_errors = []
        self._ensure_cache_folder()
    
    def _ensure_cache_folder(self):
        """Ensure cache folder exists"""
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder, exist_ok=True)
    
    def validate_youtube_url(self, url: str) -> bool:
        """Validate YouTube URL format"""
        self.validation_errors.clear()
        
        if not url:
            self.validation_errors.append("URL não pode estar vazia")
            return False
        
        # YouTube URL patterns
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        
        self.validation_errors.append("URL do YouTube inválida")
        return False
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors.copy()
    
    def extract_video_info(self, url: str, cookiefile: Optional[str] = None) -> Dict[str, Any]:
        """Extract comprehensive video information"""
        if not self.validate_youtube_url(url):
            raise ValueError(f"URL inválida: {', '.join(self.validation_errors)}")
        
        ydl_opts = {
            "cookiefile": cookiefile,
            "quiet": True,
            "no_warnings": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract comprehensive information
                video_info = {
                    "id": info.get("id", ""),
                    "title": info.get("title", ""),
                    "uploader": info.get("uploader", ""),
                    "channel": info.get("channel", ""),
                    "duration": info.get("duration", 0),
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "upload_date": info.get("upload_date", ""),
                    "description": info.get("description", ""),
                    "tags": info.get("tags", []),
                    "categories": info.get("categories", []),
                    "thumbnail": info.get("thumbnail", ""),
                    "formats": info.get("formats", []),
                    "artist": info.get("artist", ""),
                    "track": info.get("track", ""),
                    "album": info.get("album", ""),
                    "release_year": info.get("release_year", ""),
                }
                
                return video_info
                
        except Exception as e:
            print(f"{red_highlighted(f'Erro ao extrair informações do vídeo: {str(e)}')}")
            raise
    
    def parse_artist_title(self, video_info: Dict[str, Any]) -> Tuple[str, str]:
        """Parse artist and title from video information"""
        # Try explicit artist/track fields first
        if video_info.get("artist") and video_info.get("track"):
            return video_info["artist"].strip(), video_info["track"].strip()
        
        title = video_info.get("title", "")
        channel = video_info.get("channel", "")
        
        # Common separators for artist - title format
        separators = [" - ", " – ", " — ", " | ", " / "]
        
        for separator in separators:
            if separator in title:
                parts = title.split(separator, 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
        
        # Fallback to channel and title
        return channel.strip(), title.strip()
    
    def save_download_metadata(self, video_info: Dict[str, Any], download_path: str):
        """Save download metadata to cache"""
        try:
            metadata_file = os.path.join(self.cache_folder, "download_history.json")
            
            # Load existing metadata
            metadata_list = []
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_list = json.load(f)
                except:
                    metadata_list = []
            
            # Add new metadata
            new_metadata = {
                "timestamp": datetime.now().isoformat(),
                "video_id": video_info.get("id", ""),
                "title": video_info.get("title", ""),
                "channel": video_info.get("channel", ""),
                "duration": video_info.get("duration", 0),
                "download_path": download_path,
                "url": f"https://youtube.com/watch?v={video_info.get('id', '')}"
            }
            
            metadata_list.append(new_metadata)
            
            # Keep only last 50 downloads
            if len(metadata_list) > 50:
                metadata_list = metadata_list[-50:]
            
            # Save metadata
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"{yellow_highlighted(f'Aviso: Não foi possível salvar metadados: {str(e)}')}")


def get_youtube_title(url: str, cookiefile: str = None) -> tuple[str, str]:
    """Get the title of the YouTube video - Legacy function for compatibility"""
    downloader = YouTubeDownloader()
    try:
        video_info = downloader.extract_video_info(url, cookiefile)
        return downloader.parse_artist_title(video_info)
    except Exception as e:
        print(f"{red_highlighted(f'Erro ao obter título do YouTube: {str(e)}')}")
        # Fallback to original implementation
        ydl_opts = {
            "cookiefile": cookiefile,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(
                url, download=False  # We just want to extract the info
            )

        if "artist" in result:
            return result["artist"].strip(), result["track"].strip()
        if "-" in result["title"]:
            return result["title"].split("-")[0].strip(), result["title"].split("-")[1].strip()
        return result["channel"].strip(), result["title"].strip()


def __download_youtube_audio(url: str, clear_filename: str, output_path: str, cookiefile: str = None, quality: str = "best"):
    """Download audio from YouTube with enhanced options"""

    print(f"{ULTRASINGER_HEAD} {blue_highlighted('Baixando áudio...')}")
    
    # Quality options
    format_selector = {
        "best": "bestaudio/best",
        "high": "bestaudio[abr>=128]/best[abr>=128]",
        "medium": "bestaudio[abr>=96]/best[abr>=96]",
        "low": "bestaudio[abr>=64]/best[abr>=64]"
    }.get(quality, "bestaudio/best")
    
    ydl_opts = {
        "format": format_selector,
        "outtmpl": os.path.join(output_path, clear_filename),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio", 
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ],
        "cookiefile": cookiefile,
        "extractaudio": True,
        "audioformat": "mp3",
        "embed_subs": False,
        "writesubtitles": False,
        "writeautomaticsub": False,
    }

    __start_download(ydl_opts, url)


def __download_youtube_thumbnail(url: str, clear_filename: str, output_path: str, cookiefile: str = None) -> str:
    """Download thumbnail from YouTube"""

    print(f"{ULTRASINGER_HEAD} Downloading thumbnail")
    ydl_opts = {
        "skip_download": True,
        "writethumbnail": True,
        "cookiefile": cookiefile,
    }

    thumbnail_url = download_and_convert_thumbnail(ydl_opts, url, clear_filename, output_path)
    return thumbnail_url


def download_and_convert_thumbnail(ydl_opts, url: str, clear_filename: str, output_path: str) -> str:
    """Download and convert thumbnail from YouTube"""

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        thumbnail_url = info_dict.get("thumbnail")
        if thumbnail_url:
            response = ydl.urlopen(thumbnail_url)
            image_data = response.read()
            save_image(image_data, clear_filename, output_path)
            return thumbnail_url
        else:
            return ""


def __download_youtube_video(url: str, clear_filename: str, output_path: str, cookiefile: str = None, quality: str = "best") -> None:
    """Download video from YouTube with enhanced options"""

    print(f"{ULTRASINGER_HEAD} {blue_highlighted('Baixando vídeo...')}")
    
    # Quality options for video
    format_selector = {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/mp4",
        "high": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
        "medium": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
        "low": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]"
    }.get(quality, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/mp4")
    
    ydl_opts = {
        "format": format_selector,
        "outtmpl": os.path.join(output_path, clear_filename + ".%(ext)s"),
        "cookiefile": cookiefile,
        "merge_output_format": "mp4",
        "writesubtitles": False,
        "writeautomaticsub": False,
    }
    __start_download(ydl_opts, url)


def __start_download(ydl_opts, url: str) -> None:
    """Start the download with enhanced error handling"""
    
    # Add progress hook
    def progress_hook(d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                progress_text = f"Progresso: {percent:.1f}%"
                print(f"\r{blue_highlighted(progress_text)}", end='', flush=True)
            elif '_percent_str' in d:
                percent_str = d["_percent_str"]
                progress_text = f"Progresso: {percent_str}"
                print(f"\r{blue_highlighted(progress_text)}", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\n{green_highlighted('Download concluído!')}")
    
    ydl_opts['progress_hooks'] = [progress_hook]
    ydl_opts['no_warnings'] = True
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            raise Exception(f"Vídeo indisponível: {error_msg}")
        elif "Private video" in error_msg:
            raise Exception(f"Vídeo privado: {error_msg}")
        elif "This video is not available" in error_msg:
            raise Exception(f"Vídeo não disponível: {error_msg}")
        else:
            raise Exception(f"Falha no download: {error_msg}")


def download_from_youtube(input_url: str, output_folder_path: str, cookiefile: str = None, 
                         audio_quality: str = "best", video_quality: str = "best", 
                         download_video: bool = True, download_thumbnail: bool = True) -> tuple[str, str, str, MediaInfo]:
    """Enhanced YouTube download with comprehensive options"""
    
    print(f"{ULTRASINGER_HEAD} {green_highlighted('Iniciando download do YouTube...')}")
    
    # Initialize enhanced downloader
    downloader = YouTubeDownloader()
    
    try:
        # Extract video information
        video_info = downloader.extract_video_info(input_url, cookiefile)
        (artist, title) = downloader.parse_artist_title(video_info)
        
        print(f"{blue_highlighted(f'Artista: {artist}')}")
        print(f"{blue_highlighted(f'Título: {title}')}")
        duration_text = f"Duração: {video_info.get('duration', 0)} segundos"
        print(f"{blue_highlighted(duration_text)}")

        # Get additional data for song
        song_info = search_musicbrainz(title, artist)

        basename_without_ext = sanitize_filename(f"{song_info.artist} - {song_info.title}")
        basename = basename_without_ext + ".mp3"
        song_output = os.path.join(output_folder_path, basename_without_ext)
        song_output = get_unused_song_output_dir(song_output)
        os_helper.create_folder(song_output)
        
        # Download audio (always required)
        __download_youtube_audio(input_url, basename_without_ext, song_output, cookiefile, audio_quality)
        
        # Download video (optional)
        if download_video:
            try:
                __download_youtube_video(input_url, basename_without_ext, song_output, cookiefile, video_quality)
            except Exception as e:
                print(f"{yellow_highlighted(f'Aviso: Não foi possível baixar o vídeo: {str(e)}')}")

        # Handle cover/thumbnail
        cover_url = ""
        if song_info.cover_url is not None and song_info.cover_image_data is not None:
            cover_url = song_info.cover_url
            save_image(song_info.cover_image_data, basename_without_ext, song_output)
        elif download_thumbnail:
            try:
                cover_url = __download_youtube_thumbnail(input_url, basename_without_ext, song_output, cookiefile)
            except Exception as e:
                print(f"{yellow_highlighted(f'Aviso: Não foi possível baixar a thumbnail: {str(e)}')}")
        
        # Get BPM from audio file
        audio_file_path = os.path.join(song_output, basename)
        try:
            real_bpm = get_bpm_from_file(audio_file_path)
        except Exception as e:
            print(f"{yellow_highlighted(f'Aviso: Não foi possível calcular BPM: {str(e)}')}")
            real_bpm = 120  # Default BPM
        
        # Save download metadata
        downloader.save_download_metadata(video_info, song_output)
        
        print(f"{green_highlighted('Download do YouTube concluído com sucesso!')}")
        
        return (
            basename_without_ext,
            song_output,
            audio_file_path,
            MediaInfo(
                artist=song_info.artist, 
                title=song_info.title, 
                year=song_info.year, 
                genre=song_info.genres, 
                bpm=real_bpm,
                cover_url=cover_url, 
                video_url=input_url
            ),
        )
        
    except Exception as e:
        print(f"{red_highlighted(f'Erro no download do YouTube: {str(e)}')}")
        raise


def enhanced_download_from_youtube(input_url: str, output_folder_path: str, 
                                 options: Optional[Dict[str, Any]] = None) -> tuple[str, str, str, MediaInfo]:
    """Enhanced YouTube download with full configuration options"""
    
    if options is None:
        options = {}
    
    return download_from_youtube(
        input_url=input_url,
        output_folder_path=output_folder_path,
        cookiefile=options.get('cookiefile'),
        audio_quality=options.get('audio_quality', 'best'),
        video_quality=options.get('video_quality', 'best'),
        download_video=options.get('download_video', True),
        download_thumbnail=options.get('download_thumbnail', True)
    )
