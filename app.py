from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from queue import Queue
from threading import Thread
import json
import markdown
import bleach
from pipeline import run_research_pipeline

app = Flask(__name__)

def render_md(text):
    return bleach.clean(markdown.markdown(text, extensions=['tables', 'fenced_code']), tags=['p','h1','h2','h3','h4','h5','h6','ul','ol','li','strong','em','a','blockquote','code','pre','table','thead','tbody','tr','th','td','hr','br'], attributes={'a':['href','title']}, protocols=['http','https'], strip=True)

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/research')
def research():
    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '')
    if not isinstance(topic, str) or not topic.strip() or len(topic) > 1000:
        return jsonify(error='Enter a topic of 1–1000 characters.'), 400
    events = Queue()
    def worker():
        try:
            result = run_research_pipeline(topic.strip(), lambda stage: events.put({'stage': stage}))
            events.put({'stage':'done', 'report':render_md(result['report']), 'critic':render_md(result['critic']), 'raw':result['report']})
        except Exception:
            app.logger.exception('Research failed')
            events.put({'stage':'error','error':'Research failed. Check the Flask terminal for details.'})
    Thread(target=worker, daemon=True).start()
    def stream():
        while True:
            event = events.get()
            yield json.dumps(event) + '\n'
            if event['stage'] in ('done','error'):
                break
    return Response(stream_with_context(stream()), mimetype='application/x-ndjson', headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'})

if __name__ == '__main__':
    app.run(port=5000)
