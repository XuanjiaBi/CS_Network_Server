# You need to implement the "get" and "head" functions.
import os
class FileReader:
    def __init__(self):
        pass

    def get(self, filepath, cookies):
        try:
            if not (os.path.exists(filepath)):
                return None
            elif os.path.isdir(filepath):
                return "<html><body><h1>{}</h1></body></html>".format(filepath).encode()
            elif os.path.exists(filepath):
                file = open(filepath, 'rb')
                return file.read()
        except IOError:
            return None

        """
        Returns a binary string of the file contents, or None.
        """
        # try:
        #     with open(filepath, 'rb') as file:
        #         return file.read()
        #         # while msg:
        #         #     return msg
        # except IOError:
        #     return None

    #https://www.stackvidhya.com/python-read-binary-file/
        #try open(filepath,'rb'):
            #return ...;
            #return ;
        #except:
            #print("An exception occurred")
            #return 0;

    def head(self, filepath, cookies):
        """
        Returns the size to be returned, or None.
        """
        #seek();
        if not (os.path.exists(filepath)):
            return None
        elif os.path.isdir(filepath):
            return len("<html><body><h1>{}</h1></body></html>".format(filepath).encode())
        elif os.path.exists(filepath):
            file = open(filepath, 'rb')
            return len(file.read())
        # try:
        #     with open(filepath, 'rb') as file:
        #         #size = file.seek(0, os.SEEK_END)
        #         return len(file.read())
        # except FileNotFoundError:
        #     return None

