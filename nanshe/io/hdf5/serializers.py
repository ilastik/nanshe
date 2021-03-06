__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$May 14, 2014 22:19:59 EDT$"


import os

import numpy
import h5py


# Need in order to have logging information no matter what.
from nanshe.util import prof


# Get the logger
logger = prof.logging.getLogger(__name__)


@prof.log_call(logger)
def create_numpy_structured_array_in_HDF5(file_handle, internalPath, data, overwrite = False):
    """
        Serializes a NumPy structure array to an HDF5 file by using the HDF5 compound data type.
        Also, will handle normal NumPy arrays and scalars, as well.
        
        Note:
            HDF5 does not support generic Python objects. So, serialization of objects to something
            else (perhaps strs of fixed size) must be performed first.
        
        Note:
            TODO: Write doctests.
        
        Args:
            file_handle(HDF5 file):     either an HDF5 file or an HDF5 filename.
            internalPath(str):          an internal path for the HDF5 file.
            data(numpy.ndarray):        the NumPy structure array to save (or normal NumPy array).
            overwrite(bool):            whether to overwrite what is already there (defaults to False).
    """

    close_file_handle = False

    if isinstance(file_handle, str) or isinstance(file_handle, unicode):
        file_handle = h5py.File(file_handle, "a")
        close_file_handle = True

    data_array = data
    if not isinstance(data_array, numpy.ndarray):
        try:
            data_array = numpy.array(data_array)
        except:
            if not data_array.dtype.names:
                raise TypeError("The argument provided for data is type: \"" + repr(type(data)) + "\" is not convertible to type \"" + repr(numpy.ndarray) + "\".")


    try:
        file_handle.create_dataset(internalPath,
                                   shape = data_array.shape,
                                   dtype = data_array.dtype,
                                   data = data_array,
                                   chunks = bool(data_array.ndim))
    except RuntimeError:
        if overwrite:
            del file_handle[internalPath]
            file_handle.create_dataset(internalPath,
                                       shape = data_array.shape,
                                       dtype = data_array.dtype,
                                       data = data_array,
                                       chunks = True)
        else:
            raise

    if close_file_handle:
        file_handle.close()


@prof.log_call(logger)
def read_numpy_structured_array_from_HDF5(file_handle, internalPath):
    """
        Serializes a NumPy structure array from an HDF5 file by using the HDF5 compound data type.
        Also, it will handle normal NumPy arrays and scalars, as well.

        Note:
            HDF5 does not support generic Python objects. So, serialization of objects to something
            else (perhaps strs of fixed size) must be performed first.

        Args:
            file_handle(HDF5 file):     either an HDF5 file or an HDF5 filename.
            internalPath(str):          an internal path for the HDF5 file.

        Note:
            TODO: Write doctests.

        Returns:
            data(numpy.ndarray):    the NumPy structure array.
    """

    close_file_handle = False

    if isinstance(file_handle, str) or isinstance(file_handle, unicode):
        file_handle = h5py.File(file_handle, "r")
        close_file_handle = True

    data = None

    data_object = file_handle[internalPath]
    data_file = data_object.file
    data_ref = data_object.value
    # data_ref = data_object[()]

    if isinstance(data_ref, h5py.Reference):
        if ("filename" in data_object.attrs) and \
           (os.path.normpath(data_object.attrs["filename"]) != os.path.normpath(data_file.filename)):
            with h5py.File(data_object.attrs["filename"], "r") as external_file_handle:
                if isinstance(data_ref, h5py.RegionReference):
                    data = external_file_handle[data_ref][data_ref]
                else:
                    data = external_file_handle[data_ref].value
        else:
            if isinstance(data_ref, h5py.RegionReference):
                data = data_file[data_ref][data_ref]
            else:
                data = data_file[data_ref].value
    elif isinstance(data_ref, (numpy.number, numpy.ndarray,)):
        if ("filename" in data_object.attrs):
            # It's a pseudo-ref.
            assert ("dataset" in data_object.attrs)

            new_dataset_name = data_object.attrs["dataset"]
            with h5py.File(data_object.attrs["filename"], "r") as external_file_handle:
                # assert isinstance(new_dataset_name, h5py.Dataset)

                if ("field" in data_object.attrs) and ("slice" in data_object.attrs):
                    new_field = data_object.attrs["field"]
                    new_slicing = eval(data_object.attrs["slice"])

                    data = external_file_handle[new_dataset_name][new_field][new_slicing]
                elif ("field" in data_object.attrs):
                    new_field = data_object.attrs["field"]

                    data = external_file_handle[new_dataset_name][new_field]
                elif ("slice" in data_object.attrs):
                    new_slicing = eval(data_object.attrs["slice"])

                    data = external_file_handle[new_dataset_name][new_slicing]
                else:
                    data = external_file_handle[new_dataset_name][()]
        else:
            data = data_object.value

    if close_file_handle:
        file_handle.close()

    return(data)


class HDF5MaskedDataset(object):
    """
        Provides an abstraction of the masked array the HDF5 Group where the contents of a
        masked array are serialized.

        Note:
                This behaves roughly like an `h5py.Dataset` and roughly like a
                `numpy.ma.masked_array`. Internally, it uses an `h5py.Group` to
                contain the components of the masked array and allow
                interaction with them.
    """

    def __init__(self,
                 group, shape=None, dtype=None, data=None, chunks=True,
                 **kwargs
            ):
        assert isinstance(group, h5py.Group)

        assert "compression" not in kwargs
        assert "compression_opts" not in kwargs

        self._group = group

        if len(self._group):
            assert len(self._group) == 3

            assert data is None
            assert shape is None
            assert dtype is None

            assert "data" in self._group
            assert "mask" in self._group
            assert "fill_value" in self._group

            assert self._group["data"].shape == self._group["mask"].shape
            assert self._group["data"].dtype == self._group["fill_value"].dtype
            assert self._group["mask"].dtype == numpy.dtype(numpy.bool8)
        else:
            assert (data is not None) or \
                   ((shape is not None) and (dtype is not None))

            shape = tuple(shape)
            dtype = numpy.dtype(dtype)

            if data is not None:
                if (shape is not None) and (dtype is not None):
                    assert data.shape == shape
                    assert data.dtype == dtype
                else:
                    shape = tuple(data.shape)
                    dtype = numpy.dtype(data.dtype)

            self._group.create_dataset(
                "data",
                shape=shape,
                dtype=dtype,
                chunks=chunks,
                **kwargs
            )
            self._group.create_dataset(
                "mask",
                shape=shape,
                dtype=numpy.bool8,
                chunks=chunks,
                compression="gzip",
                compression_opts=2,
                **kwargs
            )
            self._group.create_dataset(
                "fill_value",
                shape=tuple(),
                dtype=dtype
            )

            if data is not None:
                self._group["data"][...] = data
                self._group["mask"][...] = numpy.ma.getmaskarray(data)
                if isinstance(data, numpy.ma.masked_array):
                    self._group["fill_value"][...] = dtype.type(data.fill_value)

    @property
    def group(self):
        return(self._group)

    @property
    def name(self):
        return(self._group.name)

    @property
    def data(self):
        return(self._group["data"])

    @data.setter
    def data(self, value):
        self._group["data"][...] = value

    @property
    def mask(self):
        return(self._group["mask"])

    @mask.setter
    def mask(self, value):
        self._group["mask"][...] = value

    @property
    def fill_value(self):
        return(self._group["fill_value"])

    @fill_value.setter
    def fill_value(self, value):
        self._group["fill_value"][...] = value

    def __len__(self):
        return(len(self._group["data"]))

    @property
    def dims(self):
        return(self._group["data"].dims)

    @property
    def ndim(self):
        return(len(self._group["data"].shape))

    @property
    def shape(self):
        return(self._group["data"].shape)

    @shape.setter
    def shape(self, shape):
        self.resize(shape)

    @property
    def size(self):
        return(self._group["data"].size)

    @property
    def dtype(self):
        return(self._group["data"].dtype)

    def resize(self, size, axis=None):
        self._group["data"].resize(size, axis)
        self._group["mask"].resize(size, axis)

    def __getitem__(self, args):
        result = self._group["data"][args]
        result = result.view(numpy.ma.masked_array)

        result.mask = self._group["mask"][args]
        result.fill_value = self._group["fill_value"][...]

        return(result)

    def __setitem__(self, args, value):
        self._group["data"][args] = value
        self._group["mask"][args] = numpy.ma.getmaskarray(value)

        if isinstance(value, numpy.ma.masked_array):
            self._group["fill_value"][...] = value.fill_value

    def __array__(self, dtype=None):
        result = self._group["data"].__array__(dtype=dtype)
        result = result.view(numpy.ma.masked_array)

        result.mask = self._group["mask"][...]
        result.fill_value = self._group["fill_value"][...]

        return(result)
