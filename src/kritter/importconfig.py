#
# This file is part of Vizy 
#
# All Vizy source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Vizy source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

import os
import importlib.util

def __import(modulename, filename, imports):
    spec = importlib.util.spec_from_file_location(modulename, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Check if we've successfully imported what we expect to import.
    # If we fail, maybe it's been edited out, or some other error (syntax, etc.)
    for i in imports:
        eval(f"module.{i}")
    return module

def import_config(filename, etcdir, imports=[]):
    basename = os.path.basename(filename)
    etc_filename = os.path.join(etcdir, basename)
    try:
        return __import(basename, etc_filename, imports)
    except:
        # If we fail, let's make a new/fresh copy and try again. (It should succeed.)
        os.system(f"cp {filename} {etc_filename}")
        return __import(basename, etc_filename, imports)

