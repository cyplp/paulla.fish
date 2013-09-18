import os
import uuid
import logging
import sqlite3

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.response import Response,FileResponse

here = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig()
log = logging.getLogger(__file__)

# views
@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    rs = request.db.execute("select id, fdescr, fpath, fid, fname from tasks where closed = 0")
    tasks = [dict(id=row[0], fdescr=row[1], fpath=row[2], fid=row[3], fname=row[4]) for row in rs.fetchall()]
    return {'tasks': tasks}

@view_config(route_name='new', renderer='new.mako')
def new_view(request):
    if request.method == 'POST':
        if request.POST.get('fdescr','fname'):
            fdescr = request.POST['fdescr']
            fname = request.POST['fname'].filename
            input_file = request.POST['fname'].file
            fid = str(uuid.uuid4())
            fpath = os.path.join('./paulla/fish/upfiles')
            full_fpath = os.path.join(fpath,fid)
            tmp_fpath = full_fpath + '~'
            output_file = open(tmp_fpath, 'wb')
            input_file.seek(0)
            while True:
                data = input_file.read(2<<16)
                if not data:
                    break
                output_file.write(data)
            output_file.close()
            os.rename(tmp_fpath, full_fpath)
            request.db.execute(
                'insert into tasks (fdescr, fpath, fid, fname, closed) values (?, ?, ?, ?, ?)',
                [request.POST['fdescr'], fpath, fid, fname, 0])
            request.db.commit()
            request.session.flash('%s was successfully added!' %(fname))
            return HTTPFound(location=request.route_path('list'))
        else:
            request.session.flash('Please enter a short description for the file!')
    return {}

@view_config(route_name='close')
def close_view(request):
    task_id = int(request.matchdict['id'])
    request.db.execute("update tasks set closed = ? where id = ?",
                       (1, task_id))
    request.db.commit()
    request.session.flash('File was successfully marked for delete!')
    return HTTPFound(location=request.route_path('list'))

@view_config(route_name='dl')
def dl_page(request):
    task_id = int(request.matchdict['id'])
    rs = request.db.execute("select fdescr, fpath, fid, fname from tasks where id = %i" % (task_id))
    file_data = fdescr, fpath, fid, fname = rs.fetchone()
    response = FileResponse(
        os.path.join(fpath,fid),
        request=request,
        )
    return response

@view_config(route_name='detail', renderer='detail.mako')
def detail_page(request):
    task_id = int(request.matchdict['id'])
    rs = request.db.execute("select id, fdescr, fpath, fid, fname from tasks where id = %i" % (task_id))
    file_data = id, fdescr, fpath, fid, fname = rs.fetchone()
    return {'file_data' : file_data}

@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(request):
    request.response.status = '404 Not Found'
    return {}


# subscribers
@subscriber(NewRequest)
def new_request_subscriber(event):
    request = event.request
    settings = request.registry.settings
    request.db = sqlite3.connect(settings['db'])
    request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    request.db.close()


@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    log.warn('Initializing database...')
    with open(os.path.join(here, 'schema.sql')) as f:
        stmt = f.read()
        settings = event.app.registry.settings
        db = sqlite3.connect(settings['db'])
        db.executescript(stmt)
        db.commit()
