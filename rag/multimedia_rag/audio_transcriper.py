import os
import requests
from datetime import datetime
import pixeltable as pxt
from pixeltable.functions import whisper
import logging

logger = logging.getLogger(__name__)

class AudioRAG:
    def __init__(self, workspace='slack_audio_workspace'):
        try:
            pxt.drop_dir(workspace, force=True)
            pxt.create_dir(workspace)
        except Exception as e:
            logger.warning(f"Workspace setup issue: {e}")
            # Try to use existing workspace
            try:
                pxt.get_dir(workspace)
            except:
                pxt.create_dir(workspace)
                
        self.workspace = workspace
        self.table_name = f'{workspace}.audio_table'
        self._init_table()

    def _init_table(self):
        try:
            self.audio_table = pxt.create_table(
                self.table_name,
                {'audio': pxt.Audio},
                if_exists='ignore'
            )
        except Exception as e:
            logger.error(f"Failed to create audio table: {e}")
            # Try to get existing table
            try:
                self.audio_table = pxt.get_table(self.table_name)
            except:
                raise Exception(f"Could not create or access audio table: {e}")

    def insert_audios(self, audio_paths):
        try:
            self.audio_table.insert({'audio': path} for path in audio_paths)
        except Exception as e:
            logger.error(f"Failed to insert audio paths: {e}")

    def transcribe_audios(self, model='base.en'):
        try:
            # Check if transcription column already exists
            if 'transcription' not in [col.name for col in self.audio_table.columns]:
                self.audio_table.add_computed_column(
                    transcription=whisper.transcribe(
                        audio=self.audio_table.audio,
                        model=model
                    )
                )
        except Exception as e:
            logger.error(f"Failed to add transcription column: {e}")

    def get_transcripts(self):
        return self.audio_table.select(
            self.audio_table.audio,
            self.audio_table.transcription.text
        ).collect()

    def transcribe_slack_audio(self, local_audio_path, model='base.en'):
        try:
            # Insert the audio file
            self.audio_table.insert([{'audio': local_audio_path}])
            
            # Add transcription column if it doesn't exist
            if 'transcription' not in [col.name for col in self.audio_table.columns]:
                self.audio_table.add_computed_column(
                    transcription=whisper.transcribe(
                        audio=self.audio_table.audio,
                        model=model
                    )
                )
            
            # Get the latest transcription
            result = self.audio_table.select(
                self.audio_table.transcription.text
            ).order_by(self.audio_table.id, asc=False).limit(1).collect()
            
            transcript = result[0]['text'] if result and len(result) > 0 else None
            return transcript
            
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return None

def process_slack_audio_event(event_json):
    """
    Process a Slack event JSON containing an audio message.
    Downloads the audio file, saves it, and transcribes using AudioRAG.
    Uses Slack's transcript if available and complete, otherwise falls back to Whisper transcription.
    """
    try:
        event = event_json.get('event', {})
        files = event.get('files', [])
        
        if event.get('subtype') != 'file_share' or not files:
            return None
            
        for f in files:
            mimetype = f.get('mimetype', '')
            if not (mimetype.startswith('audio/') or mimetype in ['audio/mp4', 'audio/mpeg', 'audio/x-m4a']):
                continue
                
            audio_url = f.get('url_private_download')
            user_id = f.get('user', 'unknown')
            
            # Check for Slack's built-in transcript first
            transcript = None
            transcript_complete = False
            transcription = f.get('transcription')
            
            if transcription and transcription.get('status') == 'complete':
                preview = transcription.get('preview', {})
                transcript = preview.get('content')
                transcript_complete = True
                logger.info(f"Using Slack transcript: {transcript}")
                return transcript
            
            # Fallback to Whisper transcription
            if not audio_url:
                continue
                
            # Prepare local path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audio_{user_id}_{timestamp}.mp4"
            save_dir = os.path.join(os.path.dirname(__file__), '../../data/slack_audio')
            os.makedirs(save_dir, exist_ok=True)
            local_path = os.path.join(save_dir, filename)
            
            # Download audio file
            try:
                from config.settings import settings
                headers = {'Authorization': f'Bearer {settings.slack_architect_bot_token}'}
                response = requests.get(audio_url, headers=headers)
                response.raise_for_status()
                
                with open(local_path, 'wb') as audio_file:
                    audio_file.write(response.content)
                    
                logger.info(f"Downloaded audio file to: {local_path}")
                
            except Exception as e:
                logger.error(f"Failed to download audio: {e}")
                continue
            
            # Transcribe using AudioRAG
            try:
                rag = AudioRAG()
                transcript = rag.transcribe_slack_audio(local_path)
                logger.info(f"Whisper transcript: {transcript}")
                
                # Clean up the file
                if os.path.exists(local_path):
                    os.remove(local_path)
                    
                return transcript
                
            except Exception as e:
                logger.error(f"Failed to transcribe audio: {e}")
                # Clean up the file even on error
                if os.path.exists(local_path):
                    os.remove(local_path)
                continue
                
    except Exception as e:
        logger.error(f"Error processing audio event: {e}")
        
    return None

if __name__ == "__main__":
    audios = [
        '/Users/gurunathlunkupalivenugopal/ionet/repos/agent_team/data/slack_audio/audio_U06SPFE6V1D_1753082257.870909_20250721_141740.mp4',
        # '/Users/gurunathlunkupalivenugopal/Downloads/audio_message.mp4',
        # '/Users/gurunathlunkupalivenugopal/Downloads/audio_message (2).mp4'
    ]
    # rag = AudioRAG()
    # rag.insert_audios(audios)
    # rag.transcribe_audios()
    # print(rag.get_transcripts())
    a= {}
    process_slack_audio_event(a)