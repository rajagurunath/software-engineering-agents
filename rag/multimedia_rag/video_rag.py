import os
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import pixeltable as pxt
from pixeltable.functions.video import extract_audio
from pixeltable.functions import whisper
from config.settings import settings
from core.integrations.llm_client import LLMClient

logger = logging.getLogger(__name__)

class VideoRAG:
    """
    Video RAG system using Pixeltable for video processing and vision model for understanding.
    """
    
    def __init__(self, workspace='slack_video_workspace'):
        self.workspace = workspace
        self.table_name = f'{workspace}.video_table'
        self.llm_client = LLMClient()
        self._init_workspace()
        self._init_table()
    
    def _init_workspace(self):
        """Initialize Pixeltable workspace"""
        try:
            pxt.drop_dir(self.workspace, force=True)
            pxt.create_dir(self.workspace)
        except Exception as e:
            logger.warning(f"Workspace setup issue: {e}")
            try:
                pxt.get_dir(self.workspace)
            except:
                pxt.create_dir(self.workspace)
    
    def _init_table(self):
        """Initialize video table with computed columns"""
        try:
            self.video_table = pxt.create_table(
                self.table_name,
                {
                    'video': pxt.Video,
                    'user_id': pxt.String,
                    'timestamp': pxt.Timestamp
                },
                if_exists='ignore'
            )
            
            # Add computed columns if they don't exist
            existing_columns = [col.name for col in self.video_table.columns]
            
            if 'audio_track' not in existing_columns:
                self.video_table.add_computed_column(
                    audio_track=extract_audio(self.video_table.video)
                )
            
            if 'transcription' not in existing_columns:
                self.video_table.add_computed_column(
                    transcription=whisper.transcribe(
                        audio=self.video_table.audio_track,
                        model='base.en'
                    )
                )
                
        except Exception as e:
            logger.error(f"Failed to create video table: {e}")
            try:
                self.video_table = pxt.get_table(self.table_name)
            except:
                raise Exception(f"Could not create or access video table: {e}")
    
    async def process_video(self, video_path: str, user_id: str) -> Dict[str, Any]:
        """
        Process video file and extract insights using vision model.
        
        Args:
            video_path: Path to the video file
            user_id: Slack user ID
            
        Returns:
            Dictionary with video analysis results
        """
        try:
            # Insert video into table
            current_time = datetime.now()
            self.video_table.insert({
                'video': video_path,
                'user_id': user_id,
                'timestamp': current_time
            })
            
            # Get transcription
            result = self.video_table.select(
                self.video_table.transcription.text
            ).order_by(self.video_table.timestamp, asc=False).limit(1).collect()
            
            audio_transcript = result[0]['text'] if result and len(result) > 0 else ""
            
            # Use vision model to understand video content
            video_understanding = await self._analyze_video_with_vision(video_path, audio_transcript)
            
            return {
                'success': True,
                'audio_transcript': audio_transcript,
                'video_understanding': video_understanding,
                'combined_analysis': f"{video_understanding}\n\nAudio Transcript: {audio_transcript}"
            }
            
        except Exception as e:
            logger.error(f"Failed to process video: {e}")
            return {
                'success': False,
                'error': str(e),
                'audio_transcript': '',
                'video_understanding': '',
                'combined_analysis': ''
            }
    
    async def _analyze_video_with_vision(self, video_path: str, audio_transcript: str) -> str:
        """
        Analyze video content using the vision model.
        
        Args:
            video_path: Path to the video file
            audio_transcript: Transcribed audio content
            
        Returns:
            Video analysis from vision model
        """
        try:
            # For now, we'll use the LLM to analyze based on audio transcript
            # In a full implementation, you'd extract video frames and send to vision model
            
            vision_prompt = f"""
            You are an expert video analyst. Based on the audio transcript below, provide insights about:
            1. What the video is likely about
            2. Key topics discussed
            3. Any technical concepts mentioned
            4. Actionable items or questions raised
            
            Audio Transcript:
            {audio_transcript}
            
            Provide a concise analysis of the video content:
            """
            
            # Use the configured vision model
            analysis = await self.llm_client.generate_text(
                sys_prompt="You are an expert video content analyst specializing in technical discussions and io.net platform topics.",
                user_prompt=vision_prompt
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze video with vision model: {e}")
            return f"Video analysis failed: {str(e)}"

def process_slack_video_event(event_json) -> Optional[Dict[str, Any]]:
    """
    Process a Slack event JSON containing a video message.
    Downloads the video file, saves it, and processes using VideoRAG.
    
    Args:
        event_json: Slack event JSON
        
    Returns:
        Dictionary with processing results or None if not a video event
    """
    try:
        event = event_json.get('event', {})
        files = event.get('files', [])
        
        if event.get('subtype') != 'file_share' or not files:
            return None
            
        for f in files:
            mimetype = f.get('mimetype', '')
            if not mimetype.startswith('video/'):
                continue
                
            video_url = f.get('url_private_download')
            user_id = f.get('user', 'unknown')
            filename = f.get('name', 'video_message.mp4')
            
            if not video_url:
                continue
                
            # Prepare local path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"video_{user_id}_{timestamp}.mp4"
            save_dir = os.path.join(os.path.dirname(__file__), '../../data/slack_video')
            os.makedirs(save_dir, exist_ok=True)
            local_path = os.path.join(save_dir, safe_filename)
            
            # Download video file
            try:
                headers = {'Authorization': f'Bearer {settings.slack_bot_token}'}
                response = requests.get(video_url, headers=headers)
                response.raise_for_status()
                
                with open(local_path, 'wb') as video_file:
                    video_file.write(response.content)
                    
                logger.info(f"Downloaded video file to: {local_path}")
                
                return {
                    'local_path': local_path,
                    'user_id': user_id,
                    'filename': filename,
                    'success': True
                }
                
            except Exception as e:
                logger.error(f"Failed to download video: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
                
    except Exception as e:
        logger.error(f"Error processing video event: {e}")
        
    return None

async def process_video_with_rag(video_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process downloaded video using VideoRAG.
    
    Args:
        video_info: Dictionary with video information from process_slack_video_event
        
    Returns:
        Video analysis results
    """
    if not video_info.get('success'):
        return None
        
    try:
        video_rag = VideoRAG()
        result = await video_rag.process_video(
            video_info['local_path'],
            video_info['user_id']
        )
        
        # Clean up the file
        if os.path.exists(video_info['local_path']):
            os.remove(video_info['local_path'])
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to process video with RAG: {e}")
        # Clean up the file even on error
        if os.path.exists(video_info.get('local_path', '')):
            os.remove(video_info['local_path'])
        return None