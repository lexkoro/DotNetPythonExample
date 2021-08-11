import threading, queue
import concurrent.futures

from datetime import datetime
from utils.generic_utils import parse_csv, parse_json, prepare_for_queue, save_audio

import time
from vits.synthesizer import Synthesizer
from utils.config import PATHS, APP_SETTINGS


input_queue = queue.Queue()
synthesizer = Synthesizer(PATHS.TTS_CONFIG_PATH, PATHS.TTS_MODEL_PATH)

def call_synthesizer(data: list):
    filename = "_".join(
    ["Test_Sprecher", str(data[0]),datetime.now().strftime("%S%f")]
    )
    # filename = data["FileName"]
    audio_data = synthesizer.inference(
        str(data[1]),
        int(data[0]),
        {"speech_speed": 1.0, "speech_var_a": 0.345, "speech_var_b": 0.6},
    )

    save_audio(file_name=filename, audio_data=audio_data)

    return str(audio_data)
    

# def paralelize(
#     objects: Sequence[Any],
#     worker: Callable[[Sequence[Any]], Any],
#     max_threads: int = 10,
# ) -> Sequence[concurrent.futures.Future]:
#     """Paralelize tasks using connector on list of URLS.

#     URLs are split into up-to num_threads chunks and each chunk is processed
#     in its own thread. Connectors in worker method MUST be duplicated to ensure
#     thread safety.

#     :returns: collection of instance of Future objects, each one corresponding
#         to one thread. It is caller responsibility to check if threads have
#         finished successfully.
#     """
#     number_of_chunks = min(len(objects), max_threads)
#     objects_chunks = chunks(objects, number_of_chunks)

#     futures = []
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
#         for objects_chunk in objects_chunks:
#             futures.append(executor.submit(call_synthesizer, objects_chunk))
#     return futures 

def queue_worker():
    """
    This worker processes incoming jobs in a separate thread.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

        future_to_job = {}

        while True:
            # sleep to reduce cpu usage
            time.sleep(1.)

            # check for status of the futures which are currently working
            done, not_done = concurrent.futures.wait(
                future_to_job,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )

            # if there is incoming work, start a new future
            while not input_queue.empty():

                # fetch a job from the queue
                job = input_queue.get()

                # Start the load operation and mark the future with its job
                future_to_job[executor.submit(call_synthesizer, job)] = job

            # process any completed futures
            for future in done:
                job = future_to_job[future]
                try:
                    data = future.result()
                finally:
                    got_work = False
                    del future_to_job[future]

wk_thread = threading.Thread(target=queue_worker, daemon=True).start()

def process_task(sp_id, text):
    data_obj = [sp_id, text]
    input_queue.put(data_obj)
    