import threading
import asyncio
from flask import *
from generate import *
from aioflask import Flask

app = Flask(__name__)
gen_queue = Queue()

async def gen_text(data):
    result = []
    def callback(res):
        result.append(res)

    gen_queue.put((data, callback))
    
    while len(result) == 0:
        await asyncio.sleep(0.2)

    return result.pop()

@app.route("/gen")
async def gen_text_route():
    text = await gen_text({
        "text": request.args.get("text"),
        "min_length": int(request.args.get("min_length", default=20)),
        "max_length": int(request.args.get("max_length", default=80)),
        "auto_translate": bool(request.args.get("auto_translate", default=False)),
    })

    resp = Response(text, status=200)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp
    
if __name__ == "__main__":
    thread = threading.Thread(target=text_generation_thread, args=(gen_queue, ), daemon=True)
    thread.start()
    app.run(host="0.0.0.0")