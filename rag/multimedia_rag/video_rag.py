import os
import sys
# Ensure local project root is prioritized for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import pixeltable as pxt
from pixeltable.functions.video import extract_audio
from pixeltable.functions import whisper
from config.settings import settings
from core.integrations.llm_client import LLMClient
from dotenv import load_dotenv
import asyncio
load_dotenv()
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
            existing_columns = list(self.video_table.columns())  # Fix: columns() returns names
            
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
            # Validate video file exists and has content
            if not os.path.exists(video_path):
                raise ValueError(f"Video file not found: {video_path}")
            
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                raise ValueError(f"Video file is empty: {video_path}")
            
            logger.info(f"Processing video file: {video_path} (size: {file_size} bytes)")

            # Insert video into table
            current_time = datetime.now()
            try:
                self.video_table.insert([{
                    'video': video_path,
                    'user_id': user_id,
                    'timestamp': current_time
                }])
                logger.info("Video inserted into Pixeltable successfully")
            except Exception as e:
                logger.error(f"Failed to insert video into Pixeltable: {e}")
                # Try to process without Pixeltable for transcription
                return await self._process_video_fallback(video_path, user_id)
            
            # Wait a moment for processing
            await asyncio.sleep(2)
            
            # Get transcription with retry logic
            audio_transcript = ""
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = self.video_table.select(
                        self.video_table.transcription.text
                    ).order_by(self.video_table.timestamp, asc=False).limit(1).collect()
                    
                    if result and len(result) > 0 and result[0]['text']:
                        audio_transcript = result[0]['text']
                        logger.info("Audio transcription extracted successfully")
                        break
                    else:
                        logger.warning(f"Transcription attempt {attempt + 1} returned empty result")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(3)  # Wait longer between retries
                except Exception as e:
                    logger.error(f"Transcription attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(3)
            
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
    
    async def _process_video_fallback(self, video_path: str, user_id: str) -> Dict[str, Any]:
        """
        Fallback video processing when Pixeltable fails
        """
        try:
            logger.info("Using fallback video processing")
            
            # Try to analyze video with vision model only
            video_understanding = await self._analyze_video_with_vision(video_path, "")
            
            return {
                'success': True,
                'audio_transcript': "Audio transcription not available",
                'video_understanding': video_understanding,
                'combined_analysis': f"{video_understanding}\n\nNote: Audio transcription was not available for this video."
            }
            
        except Exception as e:
            logger.error(f"Fallback video processing failed: {e}")
            return {
                'success': False,
                'error': f"Both primary and fallback video processing failed: {str(e)}",
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
            # Extract a few frames from the video for analysis
            frames_analysis = await self._extract_and_analyze_frames(video_path)
            
            vision_prompt = f"""
            You are an expert video analyst. Based on the video frames and audio transcript below, provide insights about:
            1. What the video is likely about
            2. Key topics discussed
            3. Any technical concepts mentioned
            4. Actionable items or questions raised
            5. Visual elements observed in the video
            
            Video Frames Analysis:
            {frames_analysis}
            
            Audio Transcript:
            {audio_transcript}
            
            Provide a comprehensive analysis of the video content combining both visual and audio information:
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
    
    async def _extract_and_analyze_frames(self, video_path: str) -> str:
        """
        Extract key frames from video and analyze them
        """
        try:
            import cv2
            import base64
            from io import BytesIO
            from PIL import Image
            
            # Open video file
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return "Could not open video file for frame extraction"
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            # Extract frames at different intervals (beginning, middle, end)
            frame_positions = [0, total_frames // 2, total_frames - 1] if total_frames > 2 else [0]
            
            frames_info = []
            for i, pos in enumerate(frame_positions):
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
                ret, frame = cap.read()
                
                if ret:
                    # Convert frame to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Analyze frame content (simplified - you could use vision model here)
                    height, width = frame_rgb.shape[:2]
                    timestamp = pos / fps if fps > 0 else 0
                    
                    frames_info.append(f"Frame {i+1} (at {timestamp:.1f}s): {width}x{height} resolution")
            
            cap.release()
            
            return f"Video duration: {duration:.1f}s, Total frames: {total_frames}, FPS: {fps:.1f}\nFrames analyzed: {'; '.join(frames_info)}"
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return f"Frame extraction failed: {str(e)}"

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
    

async def process_slack_video_event1(event_json) -> Optional[Dict[str, Any]]:
    """
    Process a Slack event JSON containing a video message.
    Downloads the video file, saves it, and processes using VideoRAG.
    
    Args:
        event_json: Slack event JSON
        
    Returns:
        Dictionary with processing results or None if not a video event
    """
    video_info = process_slack_video_event(event_json)  # Call synchronously
    if video_info:
        result = await process_video_with_rag(video_info)
        print(result)
    else:
        print("No video event found.")

if __name__ == "__main__":
    # Example usage
    example_event= {}
    asyncio.run(process_slack_video_event1(example_event))