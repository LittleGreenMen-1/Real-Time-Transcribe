from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
import pyaudio
import aiofile
import asyncio

HZ_RATE = 16000             # Rata cu care sa preia audio-ul de la microfon, pe care o trimite mai departe
                            # si AWS-ului

CHUNK = 1024                # Marimea chunk-urilor pe care le preia de la microfon
FORMAT = pyaudio.paInt16    # Formatul cu care sa 'interpreteze' audio-ul
CHANNELS = 2                # Numarul de canale (legat de stream-ul de la microfon)
RECORD_SECONDS = 15         # Cat timp sa inregistreze audio de la microfon


class EventHandler(TranscriptResultStreamHandler):
    """
    Aceeasi clasa de handler ca la Real_time_transcribe.py
    """
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(alt.transcript)


async def basic_transcribe():
    """
    Singura diferenta dintre functia asta si cea de la Real_time_transcribe.py e
    functia read_chunks()
    :return:
    """
    client = TranscribeStreamingClient(region="eu-central-1")

    # Stream-ul catre job-ul de transcribe
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=HZ_RATE,
        media_encoding="pcm"
    )

    # Stream-ul de la microfon, pe care il trimite mai departe la stream-ul de transcribe
    p = pyaudio.PyAudio()
    mic_stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=HZ_RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    async def read_chunks():
        for i in range(0, int(HZ_RATE / CHUNK * RECORD_SECONDS)):
            # Citeste un chunk de la microfon si il trimite la transcribe
            data = mic_stream.read(CHUNK)

            await stream.input_stream.send_audio_event(audio_chunk=data)

        # Inchide microfonul dupa ce a preluat de la microfon numarul de secunde precizat
        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()

        await stream.input_stream.end_stream()

    handler = EventHandler(stream.output_stream)
    await asyncio.gather(read_chunks(), handler.handle_events())


loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()
