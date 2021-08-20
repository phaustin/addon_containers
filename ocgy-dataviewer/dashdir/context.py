"""
this module defines absolute paths and reads a version number from the file
VERSION if it exists.  If it doesn't find VERSION, it creates the file
and writes "no_version" for the version number.

to use this in another module in the dashdir directory do:

import context

then use context.data_dir and context.root_dir to read data files etc. and
context.__version__ to access the version number.  It also adds root_dir
to sys.path so that dashdir can be used for library imports -- i.e. for  modules
outside of the dashdir directory

import dashdir

will allow access to dashdir.plotting, dashdir.station etc.

By doing this you can replace code with hard-coded paths like this

GIPY05 = pd.read_csv("./data/GIPY05_filtered.csv")

with the more robust:

GIPY05 = pd.read_csv(Path(data_dir / "GIPY05_filtered.csv"))

"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
data_dir = root_dir / 'data'

sys.path.insert(0,str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n"
      f"back of path: {sys.path[-1]}\n{sep}\n")

version_file= root_dir / 'VERSION'

if not version_file.is_file():
    __version__ = 'no_version'
    try:
        with open(version_file,'w') as f:
            f.write(__version__)
    except:
        __version_file__=None
else:
    with open(version_file) as f:
        __version__=f.read().strip()
