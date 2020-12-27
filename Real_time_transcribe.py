from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
import pyaudio
import aiofile
import asyncio

HZ_RATE = 16000


class EventHandler(TranscriptResultStreamHandler):
    """
    O clasa care o extinde pe cea de la Amazon. Handler pentru stream-ul de transcribe
    """
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(alt.transcript)  # Aici afiseaza rezultatul transcribe-ului


async def basic_transcribe():
    """
    Creeaza un job de transcribe pe care il tine cat timp citeste audio din fisier.

    :return: None
    """
    client = TranscribeStreamingClient(region="eu-central-1")

    # Stream-ul catre Amazon Transcribe
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=HZ_RATE,
        media_encoding="pcm"
    )

    async def read_chunks():
        async with aiofile.AIOFile('test.wav', 'rb') as afp:
            reader = aiofile.Reader(afp, chunk_size=1024 * 16)

            # Pentru fiecare 'chunk' de audio din fisier, il trimite catre procesul de transcribe
            async for chunk in reader:
                await stream.input_stream.send_audio_event(audio_chunk=chunk)

        # Cand a terminat de citit din fisierul audio, opreste stream-ul de transcribe
        await stream.input_stream.end_stream()

    # Handler-ul care se ocupa de transcribe
    handler = EventHandler(stream.output_stream)

    # Asteapta sa termine de transcris fisierul
    await asyncio.gather(read_chunks(), handler.handle_events())


# Porneste transcribe-ul si asteapta pana se termina
loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()
