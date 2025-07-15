import os, time
from libarchive import is_archive, Entry, SeekableArchive, _libarchive
from zipfile import ZIP_STORED, ZIP_DEFLATED


def is_zipfile(filename):
    return is_archive(filename, formats=('zip',))


class ZipEntry(Entry):
    def __init__(self, *args, **kwargs):
        super(ZipEntry, self).__init__(*args, **kwargs)

    def get_filename(self):
        return self.pathname

    def set_filename(self, value):
        self.pathname = value

    filename = property(get_filename, set_filename)

    def get_file_size(self):
        return self.size

    def set_file_size(self, value):
        assert isinstance(value, int), 'Please provide size as int or long.'
        self.size = value

    file_size = property(get_file_size, set_file_size)

    def get_date_time(self):
        return time.localtime(self.mtime)[0:6]

    def set_date_time(self, value):
        assert isinstance(value, tuple), 'mtime should be tuple (year, month, day, hour, minute, second).'
        assert len(value) == 6, 'mtime should be tuple (year, month, day, hour, minute, second).'
        self.mtime = time.mktime(value + (0, 0, 0))

    date_time = property(get_date_time, set_date_time)

    header_offset = Entry.header_position

    def _get_missing(self):
        raise NotImplemented()

    def _set_missing(self, value):
        raise NotImplemented()

    compress_type = property(_get_missing, _set_missing)
    comment = property(_get_missing, _set_missing)
    extra = property(_get_missing, _set_missing)
    create_system = property(_get_missing, _set_missing)
    create_version = property(_get_missing, _set_missing)
    extract_version = property(_get_missing, _set_missing)
    reserved = property(_get_missing, _set_missing)
    flag_bits = property(_get_missing, _set_missing)
    volume = property(_get_missing, _set_missing)
    internal_attr = property(_get_missing, _set_missing)
    external_attr = property(_get_missing, _set_missing)
    CRC = property(_get_missing, _set_missing)
    compress_size = property(_get_missing, _set_missing)

# encryption is one of (traditional = zipcrypt, aes128, aes256)
class ZipFile(SeekableArchive):
    def __init__(self, f, mode='r', compression=ZIP_DEFLATED, allowZip64=False, password=None,
        encryption=None):
        self.compression = compression
        self.encryption = encryption
        super(ZipFile, self).__init__(
            f, mode=mode, format='zip', entry_class=ZipEntry, encoding='CP437', password=password
        )
        

    getinfo = SeekableArchive.getentry

    def set_initial_options(self):
        if self.mode == 'w' and self.compression == ZIP_STORED:
            # Disable compression for writing.
            _libarchive.archive_write_set_format_option(self._a, "zip", "compression", "store")
        
        if self.mode == 'w' and self.password:
            if not self.encryption:
                self.encryption = "traditional"
            _libarchive.archive_write_set_format_option(self._a, "zip", "encryption", self.encryption)
          
       

    def namelist(self):
        return list(self.iterpaths())

    def infolist(self):
        return list(self)

    def open(self, name, mode, pwd=None):
        if mode == 'r':
            if pwd:
                self.add_passphrase(pwd)
            return self.readstream(name)
        else:
            return self.writestream(name)

    def extract(self, name: str, path=None, pwd=None, withoutpath: bool = True):
        """
        Method for extracting sigle file in the zip archive.
        Parameters
        ----------
            name: str
                name of file inside the archive
            path: str
                target directory, where the archive should be extracted
            pwd: str
                password to the archive being extracted
            withoutpath: bool
                boolean flag to determine whether the name of extracted file
                should remain same (False) or should  be sanitized (True)
        """
        if pwd:
            self.add_passphrase(pwd)
        if not path:
            path = os.getcwd()
        if withoutpath:
            arcname = self.sanitize_filename(filename=name)
            targetpath = os.path.join(path, arcname)
            targetpath = os.path.normpath(targetpath)
        else:
            targetpath = os.path.join(path, name)
        return self.readpath(name, targetpath)

    def extractall(self, path, names=None, pwd=None, withoutpath: bool = True):
        """
        Method for extracting all the files provided in names array. In case names are not provided, they are
        obtained by namelist method.
        Parameters
        ----------
            path: str
                target directory, where the archive should be extracted
            names: list
                array of names of files to be extracted
            pwd: str
                password to the archive being extracted
            withoutpath: bool
                boolean flag to determine whether the name of extracted file
                should remain same (False) or should  be sanitized (True)
        """
        if pwd:
            self.add_passphrase(pwd)
        if not names:
            names = self.namelist()
        if names:
            for name in names:
                self.extract(name, path, withoutpath=withoutpath)

    def read(self, name, pwd=None):
        if pwd:
            self.add_passphrase(pwd)
        return super(ZipFile, self).read(name)

    def writestr(self, member, data, compress_type=None):
        if compress_type != self.compression and not (compress_type is None):
            raise Exception('Cannot change compression type for individual entries.')
        return self.write(member, data)

    def setpassword(self, pwd):
        return self.set_passphrase(pwd)

    def testzip(self):
        raise NotImplemented()

    def _get_missing(self):
        raise NotImplemented()

    def _set_missing(self, value):
        raise NotImplemented()

    comment = property(_get_missing, _set_missing)
