"""
MetadataValidator Module

Validação cruzada de metadados de músicas usando múltiplas fontes.
"""

from .metadata_validator import (
    MetadataValidator,
    MetadataSource,
    ValidatedMetadata,
    create_lrclib_source,
    create_musicbrainz_source
)

__all__ = [
    'MetadataValidator',
    'MetadataSource',
    'ValidatedMetadata',
    'create_lrclib_source',
    'create_musicbrainz_source'
]
