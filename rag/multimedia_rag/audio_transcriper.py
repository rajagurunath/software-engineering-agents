import os
import requests
from datetime import datetime
import pixeltable as pxt
from pixeltable.functions import whisper

class AudioRAG:
    def __init__(self, workspace='slack_audio_workspace'):
        pxt.drop_dir(workspace, force=True)
        pxt.create_dir(workspace)
        self.workspace = workspace
        self.table_name = f'{workspace}.audio_table'
        self._init_table()

    def _init_table(self):
        self.audio_table = pxt.create_table(
            self.table_name,
            {'audio': pxt.Audio},
            if_exists='ignore'
        )

    def insert_audios(self, audio_paths):
        self.audio_table.insert({'audio': path} for path in audio_paths)

    def transcribe_audios(self, model='base.en'):
        self.audio_table.add_computed_column(
            transcription=whisper.transcribe(
                audio=self.audio_table.audio,
                model=model
            )
        )

    def get_transcripts(self):
        return self.audio_table.select(
            self.audio_table.audio,
            self.audio_table.transcription.text
        ).collect()

    def transcribe_slack_audio(self, local_audio_path, model='base.en'):
        self.audio_table.insert({'audio': local_audio_path})
        self.audio_table.add_computed_column(
            transcription=whisper.transcribe(
                audio=self.audio_table.audio,
                model=model
            )
        )
        result = self.audio_table.select(
            self.audio_table.transcription.text
        ).collect()
        transcript = result[-1] if result else None
        return transcript

def process_slack_audio_event(event_json):
    """
    Process a Slack event JSON containing an audio message.
    Downloads the audio file, saves it, and transcribes using AudioRAG.
    Uses Slack's transcript if available and complete, otherwise falls back to Whisper transcription.
    """
    event = event_json.get('event', {})
    files = event.get('files', [])
    result = None
    if event.get('subtype') == 'file_share' and files:
        for f in files:
            audio_url = f.get('url_private_download')
            user_id = f.get('user', 'unknown')
            transcript = None
            transcript_complete = False
            transcription = f.get('transcription')
            if transcription and transcription.get('status') == 'complete':
                preview = transcription.get('preview', {})
                transcript = preview.get('content')
                transcript_complete = True
            # Prepare local path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audio_{user_id}_{timestamp}.mp4"
            save_dir = os.path.join(os.path.dirname(__file__), '../../data/slack_audio')
            os.makedirs(save_dir, exist_ok=True)
            local_path = os.path.join(save_dir, filename)
            # Download audio file
            try:
                response = requests.get(audio_url)
                response.raise_for_status()
                with open(local_path, 'wb') as audio_file:
                    audio_file.write(response.content)
            except Exception as e:
                print(f"Failed to download audio: {e}")
                continue
            # Use Slack transcript if available and complete
            if transcript and transcript_complete:
                print(f"Using Slack transcript: {transcript}")
                result = transcript
            else:
                rag = AudioRAG()
                result = rag.transcribe_slack_audio(local_path)
                print(f"Whisper transcript: {result}")
    return result

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