from importlib import reload
import sys
import os
import logging
import traceback

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from . sequence import Sequence

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.event_type != "modified":
            return
        if event.src_path.endswith(".py"):
            modulename = os.path.splitext(os.path.basename(event.src_path))[0]
            try:
                module = sys.modules[modulename]
            except KeyError:
                return
            try:
                reload(module)
            except:
                traceback.print_exc()
                return
            imported = getattr(module, modulename)
            import __main__
            to_replace = getattr(__main__, modulename)
            if isinstance(imported, Sequence) and isinstance(to_replace, Sequence):
                logging.getLogger().info(f"UPDATING {imported} => {to_replace}")
                to_replace.events = imported.events

def init_reloader():
    import __main__
    watchfolder = os.path.join(os.getcwd(), os.path.dirname(__main__.__file__))
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, watchfolder, recursive=False)
    observer.start()
