#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

#!/usr/bin/env python3
from quart import Quart, Blueprint, request, render_template, send_file
from hypercorn.config import Config
from hypercorn.asyncio import serve
import os
import json
import argparse
import asyncio
import urllib.parse

PORT = 5000

def prefix(list):
    if len(list)==0:
        return ""
    index = 0
    while True:
        try:
            i0 = list[0][index]
            for i in list:
                if i[index]!=i0:
                    return i[0:index]
        except IndexError:
            return list[0][0:index]
        index += 1

def listdir(path):
    files = os.listdir(path)
    for i, file in enumerate(files):
        if os.path.isdir(os.path.join(path, file)):
            files[i] += "/"
    return files

class Keditor:

    _count = 0 

    def __init__(self, path, favicon=None, settings_file=None, protect=None):
        # Set umask to 0 to give others permission to whatever we create...
        os.umask(0) 
        self.path = path
        if settings_file is None:
            self.settings_file = os.path.join(os.getenv("HOME"), ".keditor-settings")
        else:
            self.settings_file = settings_file
        if protect is None:
            def null(func):
                return func
            self.protect = null
        else:
            self.protect = protect

        self.server = Blueprint(f'keditor{Keditor._count}', __name__, template_folder='.', static_folder='.', static_url_path='')
        Keditor._count += 1
        if favicon is None:
            self.favicon = os.path.join(self.server.root_path, 'static', 'favicon.ico')
        else:
            self.favicon = favicon

        @self.server.route("/")
        @self.protect
        async def index():
            return await render_template("keditor.html")

        @self.server.route("/load<path:subpath>")
        @self.protect
        async def index2(subpath):
            args = urllib.parse.parse_qs(subpath)
            if 'path' in args:
                self.path = args['path'][0]
                try:
                    listdir(self.path)
                except FileNotFoundError:
                    self.path = os.getcwd()
            return await render_template("keditor.html")

        @self.server.route('/favicon.ico')
        async def favicon():
            return await send_file(self.favicon, mimetype='image/x-icon')


        @self.server.route("/read", methods=["POST"])
        @self.protect
        async def read():
            path = await request.get_json()
            try:
                path_ = os.path.normpath(os.path.join(self.path, path))
                with open(path_, "r") as f:
                    data = f.read()
                    return json.dumps({"path": path_, "data": data})
            except:
                return json.dumps({"path": path_, "data": ""})

        @self.server.route("/write", methods=["POST"])
        @self.protect
        async def write():
            message = await request.get_json()
            path = message['path']
            path_ = os.path.join(self.path, path)
            data = message['data']
            try:
                if not os.path.exists(os.path.dirname(path_)):
                    os.makedirs(os.path.dirname(path_))
                with open(path_, "w") as f:
                    f.write(data)
            except Exception as e:
                return '"Unable to save file: ' + str(e) + '"'
            return '""'

        @self.server.route("/query", methods=["POST"])
        @self.protect
        async def query():
            path = await request.get_json()
            new_files = []
            new_files_ = []
            try:
                if os.path.isdir(path) and not path.endswith("/"):
                    path += "/"
                elif path=='..' or path=='.' or path.endswith('/..') or path.endswith('/.'):
                    path += '/'
                path_ = os.path.join(self.path, path)

                piece = path_.split('/')[-1]
                subpath = path.rstrip(piece)
                subpath_ = path_.rstrip(piece)
                files = listdir(subpath_)
                if len(files)==1:
                    path = os.path.join(subpath, files[0])
                    new_files = files
                    raise Exception
                for file in files:
                    if file.startswith(piece):
                        new_files.append(file)
                    if piece.endswith(' ') and file.startswith(piece.replace(" ", "")):
                        new_files_.append(file)
                if len(new_files)==0:
                    if len(new_files_)==0:
                        raise Exception
                    else:
                        new_files = new_files_
                piece = prefix(new_files)
                path = os.path.join(subpath, piece)
            except:     
                pass

            new_files.sort()
            return json.dumps({"path": path, "files": new_files})

        @self.server.route("/loadsettings", methods=["POST"])
        @self.protect
        async def loadsettings():
            try:
                with open(self.settings_file, "r") as f:
                    settings = f.read() 
                    return settings
            except:
                return '""'

        @self.server.route("/savesettings", methods=["POST"])
        @self.protect
        async def savesettings():
            settings = await request.get_json()
            try:
                with open(self.settings_file, "w") as f:
                    f.write(json.dumps(settings)) 
            except Exception as e:
                return '"Unable to save settings: ' + str(e) + '"'
            return '""'

    def run(self, port=PORT):
        app = Quart("keditor")
        app.register_blueprint(self.server)   
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(serve(app, config))
        #app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port, loop=self.loop)#, certfile='cert.pem', keyfile='cert.pem')
                     

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Text/code editor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", default=PORT, help="Port to run server on")
    parser.add_argument("-d", type=dir_path, default=os.getcwd(), help="Root directory for files")
    #parser.add_argument('-f', nargs='+', help='List of one or more file(s) to open')
    args = parser.parse_args()
    editor = Keditor(args.d)
    editor.run(args.p)
