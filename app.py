import os 

from sanic import Sanic, response
from motor.motor_asyncio import AsyncIOMotorClient
from jinja2 import Environment, PackageLoader

from objects import LogEntry


app = Sanic(__name__)

app.static('/static', './static')

jinja_env = Environment(loader=PackageLoader('app', 'templates'))


# def is_image_url(u):
#     image_types = ['.png', '.jpg', '.gif', '.jpeg', '.webp']
#     return any(urlparse(u.lower()).path.endswith(x) for x in image_types)
#

def render_template(name, *args, **kwargs):
    template = jinja_env.get_template(name + '.html')
    kwargs.update(globals())
    return response.html(template.render(*args, **kwargs))


app.render_template = render_template


@app.listener('before_server_start')
async def init(app, loop):
    app.db = AsyncIOMotorClient(os.getenv('MONGO_URI')).modmail_bot



@app.get('/')
async def index(request):
    return response.text('Ce site est utilisé pour afficher '
                         'les logs des tickets support.')


@app.get('/logs/raw/<key>')
async def get_raw_logs_file(request, key):
    document = await app.db.logs.find_one({'key': key})

    if document is None:
        return response.text('Ticket inexistant', status=404)

    log_entry = LogEntry(app, document)

    return log_entry.render_plain_text()


@app.get('/logs/<key>')
async def get_logs_file(request, key):
    """Renvoi du ticket rendue en texte brut"""

    document = await app.db.logs.find_one({'key': key})

    if document is None:
        return response.text('Ticket inexistant', status=404)

    log_entry = LogEntry(app, document)

    return log_entry.render_html()


@app.get('/favicon.ico')
async def get_favicon(request):
    return await response.file('/static/favicon.ico')

if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', 8000))
