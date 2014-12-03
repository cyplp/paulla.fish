import os
import datetime


from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config
from pyramid.response import Response

from pyramid.renderers import get_renderer

import magic

import couchdbkit
from couchdbkit.designer import push

from models import ToStore

settings = get_current_registry().settings
print settings

# server object
server = couchdbkit.Server(settings['couchdb.url'])

# create database
db = server.get_or_create_db(settings['couchdb.db'])
ToStore.set_db(db)

here = os.path.dirname(__file__)
for view in ['list']:
    path = os.path.join(here, 'couchdb', '_design', view)
    push(path, db)

@view_config(route_name='listing', renderer='templates/listing.pt')
def list_view(request):
    stored = ToStore.view('list/all',
                          descending=True,)
    return {"layout": site_layout(),
            'file_list': stored}


@view_config(route_name='new', renderer='json', request_method='POST')
def new_view(request):
    if request.POST.get('fdescr', 'fname'): # TODO
        descripton = request.POST['description']
        filename = request.POST['filename'].filename

        inputFile = request.POST['filename'].file

        toStore = ToStore(descripton=descripton,
                          filename=filename,
                          dtInserted=datetime.datetime.now())
        toStore.save()
        mime = ''
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as guess:
            mime = guess.id_buffer(inputFile.read(1024))

        inputFile.seek(0)

        toStore.put_attachment(inputFile, 'attachment', content_type=mime)

        return HTTPFound(location=request.route_path('listing'))
    else:
        request.session.flash(
            'Please enter a short description for the file!'
            )
    return {}


@view_config(route_name='download')
def dl_page(request):
    try:
        stored = ToStore.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound :
        return "Nope" # todo 404

    body = stored.fetch_attachment('attachment', stream=True)
    response = Response(content_type=stored._attachments['attachment']['content_type'],
                        body_file=body,
                        content_length=stored._attachments['attachment']['length'],
                        content_md5=stored._attachments['attachment']['digest'],
                        content_disposition='ttachment; filename="%s"' % stored.filename)

    return response


@view_config(route_name='detail', renderer='templates/detail.pt')
def detail_page(request):
    try:
        stored = ToStore.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound :
        return "Nope" # todo 404



    return {'layout': site_layout(),
            'stored': stored}


@view_config(context='pyramid.exceptions.NotFound', renderer='templates/notfound.pt')
def notfound_view(request):
    request.response.status = '404 Not Found'
    return {'layout': site_layout()}

def site_layout():
    renderer = get_renderer("templates/layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout
