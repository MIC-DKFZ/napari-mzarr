import dask.array as da
import zarr
import numcodecs
from imagecodecs.numcodecs import JpegXl


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith((".mzarr", ".mzz")):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    numcodecs.register_codec(JpegXl)
    grp = zarr.open(zarr.ZipStore(path, mode='r'), mode="r")

    multiscale = grp.attrs["multiscale"]
    data = [
        # da.from_zarr(grp, component=d["path"]) for d in multiscales["datasets"]
        da.from_zarr(grp[d["path"]]) for d in multiscale["datasets"]
    ]

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {}

    if grp.attrs["seg"]:
        layer_type = "labels"
    else:
        layer_type = "image"
    return [(data, add_kwargs, layer_type)]
