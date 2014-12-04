__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Jun 20, 2014 12:07:48 EDT$"


#import nanshe.advanced_debugging


#logger = nanshe.advanced_debugging.logging.getLogger(__name__)




class SPAMSException(Exception):
    pass


#@nanshe.advanced_debugging.log_call(logger)
def run_multiprocessing_queue_spams_trainDL(queue, *args, **kwargs):
    """
        Designed to run spams.trainDL in a separate process.

        It is necessary to run SPAMS in a separate process as segmentation faults
        have been discovered in later parts of the Python code dependent on whether
        SPAMS has run or not. It is suspected that spams may interfere with the
        interpreter. Thus, it should be sandboxed (run in a different Python interpreter)
        so that it doesn't damage what happens in this one.

        This particular version uses a multiprocessing.Queue to return the resulting dictionary.


        Args:
            queue(multiprocessing.Queue):           what will take the returned dictionary from spams.trainDL.
            *args(list):                            a list of position arguments to pass to spams.trainDL.
            *kwargs(dict):                          a dictionary of keyword arguments to pass to spams.trainDL.

        Note:
            Todo
            Look into having the raw data for input for spams.trainDL copied in.
    """

    # It is not needed outside of calling spams.trainDL.
    # Also, it takes a long time to load this module.
    import spams

    import StringIO
    import traceback

    print "asldflksadfjslkd"

    X = queue.get()

    print X
    print X.dtype
    print X.shape
    try:
        result = spams.trainDL(X, *args, **kwargs)
        queue.put(result)
    except:
        fd = StringIO.StringIO()
        traceback.print_exc(file=fd)
        tb = fd.getvalue()
        print(tb)
        raise

#@nanshe.advanced_debugging.log_call(logger)
def call_multiprocessing_queue_spams_trainDL(X, *args, **kwargs):
    """
        Designed to start spams.trainDL in a separate process and handle the result in an unnoticeably different way.

        It is necessary to run SPAMS in a separate process as segmentation faults
        have been discovered in later parts of the Python code dependent on whether
        SPAMS has run or not. It is suspected that spams may interfere with the
        interpreter. Thus, it should be sandboxed (run in a different Python interpreter)
        so that it doesn't damage what happens in this one.

        This particular version uses a multiprocessing.Queue to return the resulting dictionary.


        Args:
            X(numpy.matrix)                         a Fortran order NumPy Matrix with the same name as used by spams.trainDL (so if someone tries to use it as a keyword argument...).
            *args(list):                            a list of position arguments to pass to spams.trainDL.
            *kwargs(dict):                          a dictionary of keyword arguments to pass to spams.trainDL.

        Note:
            Todo
            Look into having the raw data for input for spams.trainDL copied in.

        Returns:
            result(numpy.matrix): the dictionary found
    """

    # Only necessary for dealing with SPAMS
    import multiprocessing

    import numpy

    queue = multiprocessing.Queue()
    queue.put(X)
    print "asldflksadfjslkd"

    p = multiprocessing.Process(target = run_multiprocessing_queue_spams_trainDL, args = (queue,) + args, kwargs = kwargs)
    print "asldflksadfjslkd"

    p.start()
    print "asldflksadfjslkd"

    result = queue.get()
    if not isinstance(result, numpy.ndarray):
        raise Exception(result)

    result = result.copy()
    p.join()

    if p.exitcode != 0:
        raise SPAMSException("SPAMS has terminated with exitcode \"" + repr(p.exitcode) + "\".")

    return(result)


#@nanshe.advanced_debugging.log_call(logger)
def run_multiprocessing_array_spams_trainDL(result_shared, X_shared, *args, **kwargs):
    """
        Designed to start spams.trainDL in a separate process and handle the result in an unnoticeably different way.

        It is necessary to run SPAMS in a separate process as segmentation faults
        have been discovered in later parts of the Python code dependent on whether
        SPAMS has run or not. It is suspected that spams may interfere with the
        interpreter. Thus, it should be sandboxed (run in a different Python interpreter)
        so that it doesn't damage what happens in this one.

        This particular version uses a multiprocessing.Array to share memory to return the resulting dictionary.


        Args:
            output_array(multiprocessing.Array):    shared memory array to store results in.
            X_shared(multiprocessing.Array):        a NumPy array converted using ctypeslib for easy memory sharing.
            *args(list):                            a list of position arguments to pass to spams.trainDL.
            *kwargs(dict):                          a dictionary of keyword arguments to pass to spams.trainDL.

        Note:
            This is somewhat faster than using multiprocessing.Queue.

            Todo
            Need to deal with return_model case.
            Look into having the raw data for input for spams.trainDL copied in.
    """

    # Just to make sure this exists in the new process. Shouldn't be necessary.
    import numpy
    # Just to make sure this exists in the new process. Shouldn't be necessary.
    # Also, it is not needed outside of calling this function.
    import spams


    import StringIO
    import traceback

    try:
        # Reconstruct X in the new process
        X_obj = X_shared.get_obj()
        X = numpy.ctypeslib.as_array(X_obj)
        X = numpy.asfortranarray(X)
        X = numpy.asmatrix(X)

        # Reconstruct the result in the new process
        result_obj = result_shared.get_obj()
        result = numpy.ctypeslib.as_array(result_obj)

        result[:] = spams.trainDL(X, *args, **kwargs)
    except:
        fd = StringIO.StringIO()
        traceback.print_exc(file=fd)
        tb = fd.getvalue()
        print(tb)
        raise


#@nanshe.advanced_debugging.log_call(logger)
def call_multiprocessing_array_spams_trainDL(X, *args, **kwargs):
    """
        Designed to start spams.trainDL in a separate process and handle the result in an unnoticeably different way.

        It is necessary to run SPAMS in a separate process as segmentation faults
        have been discovered in later parts of the Python code dependent on whether
        SPAMS has run or not. It is suspected that spams may interfere with the
        interpreter. Thus, it should be sandboxed (run in a different Python interpreter)
        so that it doesn't damage what happens in this one.

        This particular version uses a multiprocessing.Array to share memory to return the resulting dictionary.


        Args:
            X(numpy.matrix):                        a Fortran order NumPy Matrix with the same name as used by spams.trainDL (so if someone tries to use it as a keyword argument...).
            *args(list):                            a list of position arguments to pass to spams.trainDL.
            **kwargs(dict):                         a dictionary of keyword arguments to pass to spams.trainDL.

        Note:
            This is somewhat faster than using multiprocessing.Queue.

            Todo
            Need to deal with return_model case.
            Look into having the raw data for input for spams.trainDL copied in.
    """

    # Only necessary for dealing with SPAMS
    import multiprocessing

    # Just to make sure this exists in the new process. Shouldn't be necessary.
    import numpy

    X_ctypes = numpy.ctypeslib.as_ctypes(X)
    X_shared = multiprocessing.Array(X_ctypes._type_, X_ctypes)

    result = numpy.empty( (X.shape[0], kwargs["K"]), dtype = X.dtype)
    result_ctypes = numpy.ctypeslib.as_ctypes(result)
    result_shared = multiprocessing.Array(result_ctypes._type_, result_ctypes)

    print "X.dtype = " + repr(X.dtype)
    print "X.shape = " + repr(X.shape)

    print "result.dtype = " + repr(result.dtype)
    print "result.shape = " + repr(result.shape)

    p = multiprocessing.Process(target = run_multiprocessing_array_spams_trainDL, args = (result_shared, X_shared,) + args, kwargs = kwargs)
    p.start()
    p.join()

    if p.exitcode != 0:
        raise SPAMSException("SPAMS has terminated with exitcode \"" + repr(p.exitcode) + "\".")

    result_obj = result_shared.get_obj()
    result = numpy.ctypeslib.as_array(result_obj)

    return(result)


#@nanshe.advanced_debugging.log_call(logger)
def call_spams_trainDL(*args, **kwargs):
    """
        Encapsulates call to spams.trainDL. Ensures copy of results occur just in case.
        Designed to be like the multiprocessing calls.

        Args:
            *args(list):                            a list of position arguments to pass to spams.trainDL.
            **kwargs(dict):                         a dictionary of keyword arguments to pass to spams.trainDL.

        Note:
            For legacy.
    """

    # It is not needed outside of calling spams.trainDL.
    # Also, it takes a long time to load this module.
    import spams

    result = spams.trainDL(*args, **kwargs)
    result = result.copy()

    return(result)