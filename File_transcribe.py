import boto3    # Libraria care lucreaza cu AWS-uri
import csv
import time

AUTH_FILE = "creditentials.csv"

access_key = ""
secret_access_key = ""


def StartJob(trans_client, job_uri, job_name, file_type):
    """
    Incepe un job de transcribe pentru un fisier din S3

    :param trans_client: clientul AWS-ului de transcribe
    :param job_uri: URI-ul fisierului mp3 din S3 la care sa dea transcribe
    :param job_name: Numele jobului, ar trebui sa fie unic
    :param file_type: tipul fisierului, in cazul asta mp3
    :return: resultatul transcriptiei
    """

    trans_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=file_type,
        LanguageCode='en-US')

    # Verifica statusul jobului odata la 15 secunde de 60 de ori
    iterations = 60
    while iterations > 0:
        result = trans_client.get_transcription_job(TranscriptionJobName=job_name)

        # Daca am terminat jobul sau ceva a mers prost iese din while
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break

        time.sleep(15)

        iterations -= 1

    return result


if __name__ == "__main__":

    # Citeste datele de autentificare dintr-un fisier
    with open(AUTH_FILE, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        header = next(reader)
        data = next(reader)

        access_key = data[0]
        secret_access_key = data[1]

    # Creeaza un client de transcribe cu datele de autentificare
    transcribe = boto3.client('transcribe',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_access_key,
                              region_name="eu-central-1")

    result = StartJob(transcribe,
                      "s3://test-bucket-foni/Audio_Medical/Amazon Transcribe Medical Demo.mp3",
                      "VeryUniqueJobName",
                      "mp3")

    if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        print(result)




