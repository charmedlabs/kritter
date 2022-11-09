import os 
from time import sleep
from threading import Thread
from .util import time_stamped_file


MARKER = ".time_marker"

class FileMirror:

    def __init__(self, file_client, src_path="", dst_path="/"):
        super().__init__()
        self.src_path = src_path
        self.marker = os.path.join(self.src_path, MARKER)
        self.dst_path = dst_path
        self.file_client = file_client
        # create date marker file if it doesn't exist
        if not os.path.exists(self.marker):
            with open(self.marker, "w") as f:
                pass
            # set marker to 0 mtime (12/31/1969)
            self._update_marker(0)
        self.thread_ = Thread(target=self.thread)
        self.mtime = 0
        self.local_files = None
        self.check_delete = True
        self.run_thread = True
        self.thread_.start()

    def close(self):
        self.run_thread = False
        self.thread_.join()

    def _update_marker(self, mtime):
        if mtime>self.mtime: # Advance the time only
            self.mtime = mtime
            os.utime(self.marker, (mtime, mtime)) 
   
    def thread(self):
        while self.run_thread:
            # Find all images in path, sort by mtime
            files = os.listdir(self.src_path)
            files.remove(MARKER) # MARKER doesn't count as a legit file
            local_files = set(files)
            # Detect removal of local files and handle deletions remotely
            if self.local_files is not None:
                added_files = list(local_files.difference(self.local_files))
                deleted_files = self.local_files.difference(local_files)
            else:
                added_files = deleted_files = []
            self.local_files = local_files
            if self.check_delete or deleted_files:
                self._delete_remote()
                self.check_delete = False

            files.sort(key=lambda f : os.path.getmtime(os.path.join(self.src_path, f)))
            mtime = os.path.getmtime(self.marker)
            # Get rid of all files that are less than marker mtime.
            # (These have already been uploaded.)
            files = [f for f in files if os.path.getmtime(os.path.join(self.src_path, f))>=mtime]
            files += added_files
            error = False
            for file in files:
                if not self.run_thread:
                    return
                src_file = os.path.join(self.src_path, file)  
                dst_file = os.path.join(self.dst_path, file)                        
                print('Uploading', file)
                try:
                    self.file_client.copy_to(src_file, dst_file, True)
                    mtime = os.path.getmtime(src_file)
                    self._update_marker(mtime)
                    print('done')
                except Exception as e:
                    print('Exception uploading', src_file, e)
                    error = True
                    break
            if files and not error:
                # Add a microsecond to the marker.  It's possible for files to have the same mtime.
                # We don't want to advance the time unless we've successfully uploaded all of the
                # existing files (Imagine we have n files all with the same mtime.)  If we get here
                # we've uploaded all existing files successfully. 
                mtime += .000001 
                self._update_marker(mtime)
            else: # We're either waiting for new data or we've errored -- don't thrash.
                sleep(1)

    def _delete_remote(self):
        try:
            remote_files = set(self.file_client.list(self.dst_path))
        except Exception as e:
            print("Unable to get remote files", e)
            return
        diff = remote_files.difference(self.local_files)
        for file in diff:
            if not self.run_thread:
                return
            print("Deleting", file)
            try:
                self.file_client.delete(os.path.join(self.dst_path, file))
                print("done")
            except Exception as e:
                print("Unable to remove remote file", file, e)

    def _get_filename(self, ext):
        return os.path.join(self.src_path, kritter.time_stamped_file(ext))

