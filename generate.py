from queue import Queue
from transformers import pipeline
from time import sleep
import transformers
import translators as ts
import random
import traceback

transformers.utils.logging.set_verbosity(transformers.logging.FATAL)

def text_generation_thread(gen_queue : Queue):
    print("Model loading...")
    generator = pipeline('text-generation', model='facebook/opt-350m')
    print("Model loaded!")
    def generate(text, min_l, max_l):
        return generator(text, do_sample=True, min_length=min_l, max_length=max_l)

    seed = random.randint(0, 100000)
    while True:
        try:
            if gen_queue.empty():
                sleep(0.25)
                pass
            
            data, callback = gen_queue.get()
            if data is None or callback is None:
                continue

            text = data["text"].strip()
            min_length, max_length = data["min_length"], data["max_length"]

            if data["auto_translate"] is True:
                en_text = translate_text(text, 'tr', 'en')
                generated_text = generate(en_text, min_length, max_length)[0]["generated_text"]
                generated_text = generated_text[len(en_text):]

                tr_generated_text = translate_text(generated_text, 'en', 'tr')

                generated_text = text + " " + tr_generated_text

                callback(generated_text)
            else:
                generated_text = generate(text, min_length, max_length)[0]["generated_text"]
                callback(generated_text)

            seed += 1
        except Exception as e:
            print(e)

def translate_text(text, from_lang, to_lang):
    result = None
    services = [
        ts.google,
        ts.bing,
        ts.alibaba,
        ts.tencent
    ]

    while result is None:
        for translate in services:
            try: 
                result = translate(text, from_language=from_lang, to_language=to_lang)
                break
            except:
                print("Service", translate.__name__, "failed. Using another one.")

    return result
        

        