"""
Presentation Processing Service
================================

Extracts text from presentations (PPTX/PDF), generates TTS audio
for each slide, and prepares structured data for frontend display.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import asyncio

logger = logging.getLogger(__name__)

# Import presentation processing libraries
try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False
    logger.warning("python-pptx not available")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available")

try:
    from stt_pipelines.uzbek_tts_pipeline import create_uzbek_tts
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("TTS pipeline not available")


class PresentationService:
    """Service for processing presentations and generating audio"""
    
    def __init__(self, audio_output_dir: str = "./uploads/audio/presentations"):
        self.audio_output_dir = audio_output_dir
        os.makedirs(audio_output_dir, exist_ok=True)
        
        # Initialize TTS
        self.tts = None
        if TTS_AVAILABLE:
            try:
                self.tts = create_uzbek_tts(voice="female_clear")
                logger.info("✅ TTS initialized for presentations")
            except Exception as e:
                logger.error(f"❌ Failed to initialize TTS: {e}")
    
    async def process_presentation(self, presentation_path: str, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Process a presentation file and generate audio for each slide
        
        Args:
            presentation_path: Path to presentation file (PPTX or PDF)
            lesson_id: Lesson database ID
            
        Returns:
            Dictionary with slides and audio paths, or None on error
        """
        try:
            file_ext = Path(presentation_path).suffix.lower()
            
            if file_ext == '.pptx' and PPTX_AVAILABLE:
                return await self._process_pptx(presentation_path, lesson_id)
            elif file_ext == '.pdf' and PDF_AVAILABLE:
                return await self._process_pdf(presentation_path, lesson_id)
            else:
                logger.error(f"❌ Unsupported file format: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to process presentation: {e}")
            return None
    
    async def _process_pptx(self, pptx_path: str, lesson_id: int) -> Dict[str, Any]:
        """Extract text and generate audio from PPTX"""
        prs = Presentation(pptx_path)
        slides_data = []
        
        for idx, slide in enumerate(prs.slides):
            slide_number = idx + 1
            
            # Extract text from slide
            text_content = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text_content.append(shape.text.strip())
            
            slide_text = "\n".join(text_content)
            
            if not slide_text:
                slide_text = f"Slayd {slide_number}"
            
            # Generate audio for slide
            audio_path = await self._generate_slide_audio(
                slide_text, 
                lesson_id, 
                slide_number
            )
            
            slides_data.append({
                'slide_number': slide_number,
                'text': slide_text,
                'audio_path': audio_path,
                'duration_estimate': self._estimate_audio_duration(slide_text)
            })
            
            logger.info(f"✅ Processed slide {slide_number}/{len(prs.slides)}")
        
        # Save presentation metadata
        presentation_data = {
            'lesson_id': lesson_id,
            'total_slides': len(slides_data),
            'slides': slides_data,
            'processed_at': str(asyncio.get_event_loop().time())
        }
        
        # Save metadata to JSON
        metadata_path = os.path.join(
            self.audio_output_dir,
            f"lesson_{lesson_id}_presentation_metadata.json"
        )
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(presentation_data, f, ensure_ascii=False, indent=2)
        
        presentation_data['metadata_path'] = metadata_path
        
        logger.info(f"✅ Processed {len(slides_data)} slides for lesson {lesson_id}")
        return presentation_data
    
    async def _process_pdf(self, pdf_path: str, lesson_id: int) -> Dict[str, Any]:
        """Extract text and generate audio from PDF"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            slides_data = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text().strip()
                
                if not page_text:
                    page_text = f"Sahifa {page_num + 1}"
                
                # Generate audio for page
                audio_path = await self._generate_slide_audio(
                    page_text,
                    lesson_id,
                    page_num + 1
                )
                
                slides_data.append({
                    'slide_number': page_num + 1,
                    'text': page_text,
                    'audio_path': audio_path,
                    'duration_estimate': self._estimate_audio_duration(page_text)
                })
                
                logger.info(f"✅ Processed page {page_num + 1}/{len(pdf_reader.pages)}")
        
        # Save presentation metadata
        presentation_data = {
            'lesson_id': lesson_id,
            'total_slides': len(slides_data),
            'slides': slides_data,
            'processed_at': str(asyncio.get_event_loop().time())
        }
        
        # Save metadata to JSON
        metadata_path = os.path.join(
            self.audio_output_dir,
            f"lesson_{lesson_id}_presentation_metadata.json"
        )
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(presentation_data, f, ensure_ascii=False, indent=2)
        
        presentation_data['metadata_path'] = metadata_path
        
        logger.info(f"✅ Processed {len(slides_data)} pages for lesson {lesson_id}")
        return presentation_data
    
    async def _generate_slide_audio(self, text: str, lesson_id: int, slide_number: int) -> Optional[str]:
        """Generate TTS audio for a slide"""
        if not self.tts:
            logger.warning("⚠️ TTS not available, skipping audio generation")
            return None
        
        try:
            # Create audio file path
            audio_filename = f"lesson_{lesson_id}_slide_{slide_number}.mp3"
            audio_path = os.path.join(self.audio_output_dir, audio_filename)
            
            # Generate speech (run in executor to avoid blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.tts.speak_text(text, save_to_file=audio_path)
            )
            
            if os.path.exists(audio_path):
                logger.info(f"✅ Generated audio for slide {slide_number}")
                return audio_path
            else:
                logger.error(f"❌ Audio file not created for slide {slide_number}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to generate audio for slide {slide_number}: {e}")
            return None
    
    def _estimate_audio_duration(self, text: str) -> float:
        """Estimate audio duration in seconds based on text length"""
        # Average reading speed: ~150 words per minute
        words = len(text.split())
        duration = (words / 150) * 60
        return round(duration, 1)
    
    def load_presentation_metadata(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Load previously processed presentation metadata"""
        metadata_path = os.path.join(
            self.audio_output_dir,
            f"lesson_{lesson_id}_presentation_metadata.json"
        )
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load metadata: {e}")
        
        return None
    
    def get_slide_data(self, lesson_id: int, slide_number: int) -> Optional[Dict[str, Any]]:
        """Get data for a specific slide"""
        metadata = self.load_presentation_metadata(lesson_id)
        if metadata and 'slides' in metadata:
            for slide in metadata['slides']:
                if slide['slide_number'] == slide_number:
                    return slide
        return None
    
    async def regenerate_slide_audio(self, lesson_id: int, slide_number: int, text: str) -> Optional[str]:
        """Regenerate audio for a specific slide with updated text"""
        return await self._generate_slide_audio(text, lesson_id, slide_number)


# Global service instance
_presentation_service: Optional[PresentationService] = None


def get_presentation_service() -> PresentationService:
    """Get or create the presentation service singleton"""
    global _presentation_service
    if _presentation_service is None:
        _presentation_service = PresentationService()
    return _presentation_service
