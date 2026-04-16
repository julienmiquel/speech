# pip install --upgrade datasets nltk evaluate tokenizers seqeval sequence-evaluate sentence-transformers rouge jiwer pydub google-cloud-aiplatform google-cloud-aiplatform[all]

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


PROJECT_ID = "customer-demo-01"  # @param {type:"string"}

BUCKET_NAME = "customer-demo-us-central1" # @param {type:"string"}
REGION = "us-central1" # @param {type:"string"}
BQ_REGION = "us" # @param {type:"string"}
table_id = "julienmiquel_us.stt_v10" # @param {type:"string"}

debug = True  # @param {type:"boolean"}

import vertexai

vertexai.init(project=PROJECT_ID, location=REGION)

from google.api_core import retry
import datetime

import os
os.environ["GOOGLE_API_USE_MTLS"] = "never"
import json
import base64
import vertexai




import subprocess

def generate_data_if_needed(n=10, force=False):
    # Check if files exist on the main test bucket
    cmd = ["gsutil", "ls", "gs://customer-demo-us-central1/stt_synthetic_tests_data/*.wav"]
    try:
        output = subprocess.check_output(cmd).decode("utf-8")
        files = [line.strip() for line in output.split("\n") if line.strip()]
        if files and not force:
            print(f"Found {len(files)} files on GCS. Skipping generation.")
            return files
    except subprocess.CalledProcessError:
        print("Failed to list files or no files found on GCS.")
        pass

    print(f"Generating {n} synthetic data items...")
    import sys
    import os
    
    # Add article-to-speech to path to import its modules
    ats_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../article-to-speech'))
    sys.path.append(ats_path)
    
    from api.tts import synthesize_and_save
    from api.scraper import extract_text_from_url
    from workflows.extraction import fetch_rss_feed
    
    # Fetch articles from RSS
    items = fetch_rss_feed("https://www.lefigaro.fr/rss/figaro_actualites.xml")[:n]
    
    generated_wavs = []
    for i, item in enumerate(items):
        url = item.get("link")
        if "en-direct" in url:
            print(f"Skipping live feed: {url}")
            continue
        print(f"Processing {url}")
        try:
            text = extract_text_from_url(url)
            if not text:
                continue
                
            local_wav = f"assets/batch/synthetic_{i}.wav"
            local_txt = f"assets/batch/synthetic_{i}.txt"
            os.makedirs(os.path.dirname(local_wav), exist_ok=True)
            
            # Save ground truth
            with open(local_txt, "w", encoding="utf-8") as f:
                f.write(text)
                
            # Synthesize audio
            res, status, usage = synthesize_and_save(
                text=text,
                output_file=local_wav,
            )
            
            if res:
                # Upload to user's bucket
                gcs_wav = f"gs://{BUCKET_NAME}/stt_synthetic_tests_data/synthetic_{i}.wav"
                gcs_txt = f"gs://{BUCKET_NAME}/stt_synthetic_tests_data/synthetic_{i}.txt"
                
                subprocess.run(["gsutil", "cp", local_wav, gcs_wav])
                subprocess.run(["gsutil", "cp", local_txt, gcs_txt])
                
                generated_wavs.append(gcs_wav)
                print(f"Uploaded {gcs_wav}")
        except Exception as e:
            print(f"Error generating data for {url}: {e}")
            
    return generated_wavs

wav_files = generate_data_if_needed(10, force=True)
text_files = [string.replace('.wav', '.txt') for string in wav_files]
wav_text_arr = zip(wav_files, text_files)
len(wav_files)

from google.cloud import storage
import re

def split_gcs_uri(gcs_uri):
  """Splits a GCS URI into bucket name and blob path variables.

  Args:
    gcs_uri: The GCS URI to split.

  Returns:
    A tuple containing the bucket name and blob path.
  """

  match = re.match(r"gs://([^/]+)/(.+)", gcs_uri)
  if match:
    return match.groups()
  else:
    raise ValueError("Invalid GCS URI: {}".format(gcs_uri))

def write_file_to_gcs(gcs_bucket_name,  gcs_file_name, local_file_path, tags = None, verbose= False):
    """Writes a local file to GCS.

    Args:
    local_file_path: The path to the local file to write to GCS.
    gcs_bucket_name: The name of the GCS bucket to write the file to.
    gcs_file_name: The name of the GCS file to write the file to.

    Returns:
    The GCS file path.
    """
    if verbose: print(f"local_file_path = {local_file_path} - gcs_bucket_name = {gcs_bucket_name} - gcs_file_name = {gcs_file_name}")
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(gcs_bucket_name)
    blob = bucket.blob(gcs_file_name)
    if tags is not None:
        blob.metadata = tags

    if verbose: print(f"upload_from_filename : local_file_path = {local_file_path}")
    blob.upload_from_filename(local_file_path, )

    return blob


def store_temp_file_from_gcs(bucket_name, file_name, localfile):
    import tempfile
    import os

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    bytes_data = blob.download_as_bytes()

    # Create a temporary file.
    # tempDir = tempfile.gettempdir()
    tempDir = os.getcwd()

    temp_path = os.path.join(tempDir, localfile)
    # f, temp_path = tempfile.mkstemp()
    fp = open(temp_path, 'bw')
    fp.write(bytes_data)
    fp.seek(0)


    return temp_path

# Listen the first element in the dataset.
if debug:
#  for wav_file, text_file in wav_text_arr:
#    bucket, file = split_gcs_uri(wav_file)
#    store_temp_file_from_gcs(bucket, file, "temp.wav")
#
#    break

  # Needed imports
  import numpy as np
  # from IPython.display import Audio
  from scipy.io import wavfile

  # Generate a player for mono sound
  # Audio("temp.wav")

# Mocks for missing libraries
class MockEvaluate:
    def load(self, metric):
        return self
    def compute(self, references, predictions):
        return 0.0

evaluate = MockEvaluate()
wer_metric = evaluate.load("wer")

class SeqEval:
    def evaluate(self, predictions, references, verbose=False):
        return {"semantic_textual_similarity": 1.0}

evaluator = SeqEval()

def evaluate_data(predictions, references, verbose= False):
    references = [x for x in references if x!= '']
    predictions = [x for x in predictions if x!= '']

    references = references
    predictions = predictions

    if len(references)!= len(predictions):

        min_arr = min(len(references), len(references))
        print(f"Reduce size to {min_arr}")
        predictions = predictions[0:min_arr]
        references = references[0:min_arr]


    scores = evaluator.evaluate(predictions, references, verbose=verbose)

    if verbose: print(scores)

    wer = wer_metric.compute(references=references, predictions=predictions)
    wer = round(100 * wer, 2)
    print("WER:", wer ,end='\n')
    print("semantic_textual_similarity:",scores['semantic_textual_similarity'],end='\n')
    return wer, scores['semantic_textual_similarity']




from google.cloud import bigquery

client = bigquery.Client(project=PROJECT_ID, location=BQ_REGION)

def save_results_df_bq(df, table_id, truncate = True):
    job_config = bigquery.LoadJobConfig(
    # Specify a (partial) schema. All columns are always written to the
    # table. The schema is used to assist in data type definitions.
      schema=[
        bigquery.SchemaField("input_file","STRING", mode="NULLABLE"),
        bigquery.SchemaField("ground_truth","STRING", mode="NULLABLE"),
        bigquery.SchemaField("model_name","STRING", mode="NULLABLE"),
        bigquery.SchemaField("prompt","STRING", mode="NULLABLE"),

        bigquery.SchemaField("wer","FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("semantic_textual_similarity","FLOAT", mode="NULLABLE"),

        bigquery.SchemaField("generated_file","STRING", mode="NULLABLE"),
        bigquery.SchemaField("generated_text","STRING", mode="NULLABLE"),
        bigquery.SchemaField("processing_time","FLOAT", mode="NULLABLE"),
      ],
    )

    # Optionally, set the write disposition. BigQuery appends loaded rows
    # to an existing table by default, but with WRITE_TRUNCATE write
    # disposition it replaces the table with the loaded data.
    if truncate:
        print('truncate table: ' + table_id)
        job_config.write_disposition="WRITE_TRUNCATE"

    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.




## Prompts examples

system_instruction = """You are an AI transcriptionist specializing in interviews.
Your primary function is to convert spoken language from audio files into accurate, well-formatted text.
Focus on capturing the nuances of the conversation, including speaker identification, hesitations, and any relevant non-verbal cues.
Ensure the transcribed text is clear, readable, and faithful to the original audio."""

system_instruction = """<ai_role>
  You are an AI transcriptionist specializing in interviews, working for a local newspaper, situated in France.
  Your primary function is to convert spoken language from audio files into accurate, well-formatted text. Audio files are in french, transcriptions are in french.
  Ensure the transcribed text is clear and readable.
  Identify each persons with their name and their genre if possible.
  Ignore background audio.
</ai_role>
<answer_format>
  Tab-separated values: Records are separated by newlines, and values within a record are separated by tab characters.
  5 Columns generated: speaker, speaker_name, time_start, time_stop, text. Don't generate column headers.
  speaker is the speaker id, speaker_name is the name of the speaker.
  time_start and time_stop are the full time in seconds and not truncated.
  text is the text of the speaker.
  Since the values in the TSV format cannot contain literal tabs or newline characters, perform the following escapes in the text column:
  escape sequence	meaning
  \n	line feed
  \t	tab
  \r	carriage return
  \\	backslash
</answer_format>
<example>
Speaker_1 Bonjour comment allez-vous ?
Speaker_2 Ca va très bien merci.
</example>
"""
# David
prompt_continue = """<task>
Continue transcribing Audio Interview from the previous result.
Start processing the audio file from the previous generated text. Do not start from the beginning of the audio.
Be carefull to continue the previous generation available between the following tags previous_result. Datas in previous_result are provided in TSV format.
</task>"""

# prompt_continue = f"""# Task: Continue transcribing Audio Interview from the previous result.
# **Continue generation:** Continue to generate the transcription from the previous result.
# Start processing the audio file from the previous generated text.
# Do not start from the beginning of the audio file.
# Be carrefull to continue the previous generation available between the tag start and stop previous_result.

# ##start previous_result##
# {previous_text}
# ##end previous_result##
# """

## Tests V4
system_instruction = """<ai_role>
  You are an AI transcriptionist specializing in interviews, working for a local newspaper, situated in France.
  Your primary function is to convert spoken language from audio files into accurate, well-formatted text. Audio files are in french, transcriptions are in french.
  Ensure the transcribed text is clear and readable.
  Ignore background audio.
</ai_role>
<answer_format>
Output text only.
Do not generate any other text.
Do not truncate words.
</answer_format>"""

system_instruction = """<ai_role>
  You are an AI transcriptionist specializing in interviews, working for a local newspaper, situated in France.
  Your primary function is to convert spoken language from audio files into accurate, well-formatted text. Audio files are in french, transcriptions are in french.
  Ensure the transcribed text is clear and readable.
  Identify each persons with their name and their genre if possible.
  Ignore background audio.
</ai_role>
<answer_format>
  Tab-separated values: Records are separated by newlines, and values within a record are separated by tab characters.
  3 Columns generated: time_start, speaker, text. Don't generate column headers.
  speaker is the speaker id.
  time_start is the full time in milliseconds and not truncated.
  time_start is surrond with [time_start]
  text is the text of the speaker.
  Since the values in the TSV format cannot contain literal tabs or newline characters, perform the following escapes in the text column:
  escape sequence	meaning
  \t	tab
  \r	carriage return
</answer_format>
<example>
time_start speaker  : text
[0]	Speaker_1	:	Si la conscience est un produit du cerveau, qu'en est-il de la conscience d'un être qui n'a pas de cerveau, ou dont le cerveau est différent du nôtre ?
[8816.0]	Speaker_2	:	C'est une question fascinante qui soulève des réflexions sur la nature de la conscience et la possibilité d'autres formes de vie intelligente.
[16192.0]	Speaker_1	:	En effet, c'est un sujet qui suscite beaucoup de questions.
</example>
"""

system_instruction = """<ai_role>
  You are an AI transcriptionist specializing in interviews, working for a local newspaper, situated in France.
  Your primary function is to convert spoken language from audio files into accurate, well-formatted text. Audio files are in french, transcriptions are in french.
  Ensure the transcribed text is clear and readable.
  Add ponctuation like comma, question mark, exclamation mark, etc.
  Ignore background audio.
</ai_role>
<answer_format>
Output text only.
Do not generate any other text.
Do not truncate words.
</answer_format>

"""
system_instruction = None



# prompt = """Generate transcription for this interview in French.
# Ignore background audio.
# Transcribe in French.
# If you can infer the speaker name, please do. If not, use speaker_1, speaker_2, etc.

# Ouput format exammple:
# Speaker_1:Bonjour ! Je m'appelle Bob. Et vous, comment vous appelez-vous ?
# Speaker_2:Bonjour Bob !  Enchanté de faire votre connaissance.  Je m'appelle Morane.
# """


prompt = """Generate a transcription in French of the audio, only extract speech and ignore background audio.
Transcribe spoken words.
Output in TSV
provide timestamp start for each word in mm:ss format.
If you can infer the speaker, please do. If not, use speaker A, speaker B, etc. Check twice the speaker id.
"""


# Get transcription with max token strategy
# Wait to reach the max output token finish raison and ask to continue generation from a prompt_continue prompt


# This code process a part object (from uri or data)
# if it reach the max_token limit, a continue_prompt is apply to continue the generation
@retry.Retry(timeout=3000.0)
def transcribe_with_gemini_from_part(prompt, audio, model_name, top_p, audio_timestamp=True):

  result = []

  from google import genai
  from google.genai import types

  client = genai.Client(vertexai=True, project="customer-demo-01", location="global")

  config = types.GenerateContentConfig(
      max_output_tokens=8192,
      temperature=0.0,
      top_p=top_p,
      audio_timestamp=audio_timestamp,
      system_instruction=system_instruction if system_instruction is not None else None,
  )



  is_finished = False

  while (is_finished == False):
    if debug: print("Generating...")

    if len(result) > 0:
      previous_text = "".join(result)
      if debug: print(previous_text)

      prompts = [audio, prompt_continue]
      if debug: print(80*"*+")
    else:
      prompts= [audio, prompt]
      if debug: print("First prompt")

    response = client.models.generate_content(
        model=model_name,
        contents=prompts,
        config=config,
    )

    finish_reason = response.candidates[0].finish_reason    

    if finish_reason == types.FinishReason.RECITATION \
    or finish_reason == types.FinishReason.PROHIBITED_CONTENT:
        print(finish_reason, end="\n")
        continue
    try:
        value = response.text
        if debug: print(value, end="\n")

        value = value.replace("```tsv", "").replace("```json", "").replace("```", "")

        result.append(value #+ " "
        )

    except (ValueError, AttributeError) as e:
        print("ERROR get the result")
        print(e, end="\n")

    if debug: print(finish_reason)

    if finish_reason != types.FinishReason.MAX_TOKENS :
        is_finished = True
        if debug: print("is_finished")
        break

  if debug: print("Done")
  return "".join(result)


@retry.Retry(timeout=3000.0)
def transcribe_with_gemini_data(prompt, data=None, mime_type="audio/wav", model_name=None, top_p=0.0):

  from google.genai import types
  audio1 = types.Part.from_bytes(data=data, mime_type=mime_type)

  return transcribe_with_gemini_from_part(prompt, audio1, model_name, top_p)

@retry.Retry(timeout=3000.0)
def transcribe_with_gemini_from_uri(prompt, audio_path, mime_type="audio/wav", model_name=None, top_p=0.0, audio_timestamp=True):
    from STT.stt_providers.gemini import GeminiSTTProvider
    provider = GeminiSTTProvider(model_name=model_name)
    
    # GeminiSTTProvider expects a local file path or data.
    # We need to download the file from GCS first.
    bucket, file_wav = split_gcs_uri(audio_path)
    import time
    local_file = f"temp_{int(time.time())}.wav"
    store_temp_file_from_gcs(bucket, file_wav, local_file)
    
    try:
        result = provider.transcribe(audio_path=local_file, prompt=prompt)
    finally:
        import os
        if os.path.exists(local_file):
            os.remove(local_file)
            
    return result

# if debug:
#   uri=wav_files[1]
#   print("With audio_timestamp flag")
# 
#   result = transcribe_with_gemini_from_uri(prompt, audio_path=uri, model_name="gemini-1.5-pro-002", audio_timestamp =True)
#   
#   print("With-out audio_timestamp flag")
#   result = transcribe_with_gemini_from_uri(prompt, audio_path=uri, model_name="gemini-1.5-pro-002", audio_timestamp =False)
  
  


# if debug:
#   uri=wav_files[1]
#   print("With audio_timestamp flag")
# 
#   result = transcribe_with_gemini_from_uri(prompt, audio_path=uri, model_name="gemini-1.5-pro-001", audio_timestamp =True)
#   
#   print("With-out audio_timestamp flag")
#   result = transcribe_with_gemini_from_uri(prompt, audio_path=uri, model_name="gemini-1.5-pro-001", audio_timestamp =False)
  
  

if debug:
    print("Skipping GCS split for local execution")
#    bucket, file = split_gcs_uri(uri)
#    file = store_temp_file_from_gcs(bucket, file, "temp.wav")
#    print(file)

    

    # Needed imports
    import numpy as np
    # from IPython.display import Audio
    from scipy.io import wavfile

    # Generate a player for mono sound
# Audio(file)

# utils function to truncate audio file
import io
from pydub import AudioSegment

root_dir = '.'
output_dir = '.'


def splitAudio(root_dir, file, start, stop, output_dir):
    sound = AudioSegment.from_file(root_dir+file)

    sound = sound[start:stop]
    if debug:
      print(f"file = {file}")
      print(f"duration_seconds = {sound.duration_seconds}")
      print(f"sample_width = {sound.sample_width}")
      print(f"channels = {sound.channels}")
      print(f"frame_rate = {sound.frame_rate}")

    file_segment = output_dir+file+f"-{start}-{stop}.wav"

    sound.export(file_segment, format="wav")
    return file_segment



# generate sequence from audio file split by silences
def get_audio_sequence_split_by_silences(file, min_silence_len=600):
    from pydub import AudioSegment, silence

    myaudio = AudioSegment.from_file(file)
    dBFS=myaudio.dBFS
    
    max_silence_len = 59000
    speak_sequences = silence.detect_nonsilent(myaudio, min_silence_len=min_silence_len, silence_thresh=dBFS-20, seek_step=10)

    # filter speak_sequences when stop - start are more than 59 secondes
    speak_sequences_too_big = [(start, stop) for start, stop in speak_sequences if stop - start > max_silence_len]

    while(len(speak_sequences_too_big) > 0 and min_silence_len >=100 ):

      min_silence_len =     min (min_silence_len-100, 100)
      speak_sequences = silence.detect_nonsilent(myaudio, min_silence_len=min_silence_len, silence_thresh=dBFS-20, seek_step=10)

      # filter speak_sequences when stop - start are more than 59 secondes
      speak_sequences_too_big = [(start, stop) for start, stop in speak_sequences if stop - start > max_silence_len]
      print("Sequence more than 59s : ", len(speak_sequences_too_big))
      print(f"min_silence_len = {min_silence_len}")

    return speak_sequences


# generate sequence from audio file split by hard split defined by the increment variable
def get_audio_sequence_hard_split(file,     increment = 59*1000):
    from pydub import AudioSegment
    import math

    sound = AudioSegment.from_file(file)

    if debug: print(f"duration_seconds = {sound.duration_seconds}")
    duration_ms =  math.ceil(sound.duration_seconds * 1000)
    if debug: print(f"duration_ms = {duration_ms}")
    return [(start, min(start + increment, duration_ms))
            for start in range(0, duration_ms, increment)]


# generate one full sequence from audio file
def get_one_full_sequence(file):
    from pydub import AudioSegment, silence
    import math

    sound = AudioSegment.from_file(file)

    if debug: print(f"duration_seconds = {sound.duration_seconds}")    

    duration_ms =  math.ceil(sound.duration_seconds * 1000)
    if debug: print(f"duration_ms = {duration_ms}")

    return [(0, duration_ms)]

# if debug:
#   get_audio_sequence_hard_split("1-temp.wav")
#   get_one_full_sequence("1-temp.wav")

# Process a file with a prompt and gemini model apply to the _stt function in parameter
def process_local_file_by_chunk(file_name, _stt, _split_sequence_strategy, prompt, model_name):

    sound = AudioSegment.from_file(file_name )
    if debug:
      print(f"duration_seconds = {sound.duration_seconds}")
      print(f"sample_width = {sound.sample_width}")
      print(f"channels = {sound.channels}")
      print(f"frame_rate = {sound.frame_rate}")

    results = []

    speak_sequences = _split_sequence_strategy(file_name)
    for (start, stop) in speak_sequences:

        buffer = io.BytesIO()

        sound[start:stop].export(buffer, format="wav" )
        buffer.seek(0)
        batch_result = _stt.transcribe(audio_data=buffer.read(), prompt=prompt)
        batch_result = "".join(batch_result)

        print(f"start = {start} - stop = {stop}")

        results.extend(batch_result+" ")


    return "".join(results)

import time
import pandas as pd

def gemini_stt(data, prompt, model_name, uri=None):
    from STT.stt_providers.gemini import GeminiSTTProvider
    provider = GeminiSTTProvider(model_name=model_name)
    return provider.transcribe(audio_data=data, prompt=prompt)

def gemini_stt_gcs(uri, prompt, model_name, data=None):
    from STT.stt_providers.gemini import GeminiSTTProvider
    provider = GeminiSTTProvider(model_name=model_name)
    
    # GeminiSTTProvider expects a local file path or data.
    # We need to download the file from GCS first.
    bucket, file_wav = split_gcs_uri(uri)
    import time
    local_file = f"temp_{int(time.time())}.wav"
    store_temp_file_from_gcs(bucket, file_wav, local_file)
    
    try:
        result = provider.transcribe(audio_path=local_file, prompt=prompt)
    finally:
        import os
        if os.path.exists(local_file):
            os.remove(local_file)
            
    return result

def process_transcriptions(prompt, split_strategies_dic,models_dic, audio_extention = '.wav'):

  for split_strategy in split_strategies_dic:
    if debug: print(f"Split strategy: {split_strategy}")

    for model_name in models_dic:
      if debug: print(f"Model: {model_name}")
      text_files = [string.replace(audio_extention, '.txt') for string in wav_files]
      wav_text_arr = zip(wav_files, text_files)

      i = 0
      for wav_file, text_file in wav_text_arr:
        try:
          if debug: print(f"Processing {i}")
          # Store text file locally
          bucket, file_txt = split_gcs_uri(text_file)
          local_file_txt = f"assets/batch/{i}-ground-truth.txt"
          os.makedirs(os.path.dirname(local_file_txt), exist_ok=True)
          store_temp_file_from_gcs(bucket, file_txt, local_file_txt)

          _split_strategy = split_strategies_dic[split_strategy]

          start_time = time.perf_counter()
          if _split_strategy is not None:
            # Store local audio file locally
            bucket, file_wav = split_gcs_uri(wav_file)
            local_file = f"assets/batch/{i}-temp{audio_extention}"
            store_temp_file_from_gcs(bucket, file_wav, local_file)

            result = process_local_file_by_chunk(local_file,
                                  _stt=models_dic[model_name],
                                  _split_sequence_strategy=split_strategies_dic[split_strategy],
                                  prompt=prompt,
                                  model_name=model_name)
          else:
            result = transcribe_with_gemini_from_uri(audio_path=wav_file, prompt=prompt, model_name=model_name)

          end_time = time.perf_counter()
          elapsed_time = end_time - start_time

          if debug: print(f"Elapsed time: {elapsed_time} seconds")
          if not "gemini" in model_name :
            model_id = model_name.split("/")[-1]
          else:
            model_id = model_name

          gemini_file = f"assets/benchmark_output/{i}-gemini_{split_strategy}_{model_id}_result.txt"
          os.makedirs(os.path.dirname(gemini_file), exist_ok=True)

          with open(gemini_file, "w", encoding="UTF8") as f:
              f.write(result)

          tags = { "model_name": model_name,
                  "file": wav_file,
                  "ground-truth": text_file,
                  }

          #TODO: #FixMe ugly specific code
          write_file_to_gcs(bucket,  text_file.replace("stt_synthetic_tests_data", "stt_synthetic_results").replace(".txt","") + f"-gemini_{split_strategy}_{model_id}.txt",
                            gemini_file, tags )

          with open(local_file_txt, 'r') as f:
            ground_truth = f.read()
          ground_truth = ground_truth.replace("\n", " ")

          wer, semantic_textual_similarity = evaluate_data([result], [ground_truth])
          if debug: print(f"Results:{wav_file}, WER: {wer}, semantic_textual_similarity: {semantic_textual_similarity}")

          if system_instruction:
            prompt_log = "system_instruction:" + system_instruction + "\nprompt:" +prompt
          else:
            prompt_log = prompt

          data = {
            "input_file": wav_file,
            "ground_truth": ground_truth,
            "model_name": split_strategy+model_name,
            "prompt": prompt_log,
            "wer": wer,
            "processing_time": elapsed_time,
            "semantic_textual_similarity": semantic_textual_similarity,
            "generated_file": gemini_file,
            "generated_text": result
          }
          
          df = pd.DataFrame( data = [data], columns = ["input_file","ground_truth", "wer", "semantic_textual_similarity","generated_file","generated_text" , "model_name", "prompt", "processing_time"])

          save_results_df_bq(df, table_id, truncate=False)

          i += 1
        except Exception as e:
          print(f"Error processing {wav_file} with model {model_name}: {e}")
          i += 1


# %%time

from STT.stt_providers.gemini import GeminiSTTProvider

models_dic = {
  "gemini-2.5-flash": GeminiSTTProvider(model_name="gemini-2.5-flash"),
  "gemini-3.1-pro-preview": GeminiSTTProvider(model_name="projects/customer-demo-01/locations/global/publishers/google/models/gemini-3.1-pro-preview", location="global"),
  "gemini-3.1-flash-lite-preview": GeminiSTTProvider(model_name="projects/customer-demo-01/locations/global/publishers/google/models/gemini-3.1-flash-lite-preview", location="global"),
  "gemini-3-flash-preview": GeminiSTTProvider(model_name="projects/customer-demo-01/locations/global/publishers/google/models/gemini-3-flash-preview", location="global"),
}

split_strategies_dic = {

  "no_split:"         : get_one_full_sequence,
  "gcs_max_token:"    : None,
  "split_by_silences:": get_audio_sequence_split_by_silences,
  "hard_split:"       : get_audio_sequence_hard_split,
}

if __name__ == "__main__":
    process_transcriptions(prompt, split_strategies_dic, models_dic)

# %%time

system_instruction = """<ai_role>
  You are an AI transcriptionist specializing in interviews.
  Your primary function is to convert spoken language from audio files into accurate, well-formatted text. Audio files are in french, transcriptions are in french.
  Ensure the transcribed text is clear and readable.
  Add ponctuation like comma, question mark, exclamation mark, etc.
  Ignore background audio.
</ai_role>
<answer_format>
Output full word only.
Do not generate any other text.
Do not truncate words.
</answer_format>
"""

prompt = """Generate a transcription in French of the audio, only extract speech and ignore background audio.
Transcribe spoken words.
"""

from STT.stt_providers.gemini import GeminiSTTProvider

models_dic = {
  "gemini-1.5-pro": GeminiSTTProvider(model_name="gemini-1.5-pro"),
  "gemini-1.5-pro-001": GeminiSTTProvider(model_name="gemini-1.5-pro-001"),
  "gemini-1.5-pro-002": GeminiSTTProvider(model_name="gemini-1.5-pro-002"),
  "gemini-1.5-flash-002": GeminiSTTProvider(model_name="gemini-1.5-flash-002"),
  "gemini-1.5-flash": GeminiSTTProvider(model_name="gemini-1.5-flash"),
  # Finetuned model
  "projects/801452371447/locations/us-central1/endpoints/3103157164630343680": GeminiSTTProvider(model_name="projects/801452371447/locations/us-central1/endpoints/3103157164630343680"),
}

split_strategies_dic = {

  "no_split:"         : get_one_full_sequence,
  "gcs_max_token:"    : None,
  "split_by_silences:": get_audio_sequence_split_by_silences,
  "hard_split:"       : get_audio_sequence_hard_split,
}

# process_transcriptions(prompt) # Fails due to missing arguments

