__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Apr 14, 2014 17:42:07 EDT$"


import logging
import traceback
import os
import sys
import time

import psutil

import wrappers



# Nothing fancy. Just the basic logging unless otherwise specified, in which case this does nothing.
logging.basicConfig(level = logging.DEBUG, stream=sys.stderr)


def log_call(logger, to_log_call = True, to_print_args = False, to_print_time = True, to_print_exception = False):
    """
        Takes a given logger and uses it to log entering and leaving the decorated callable.
        Intended to be used as a decorator that takes a few arguments.

        Args:
            logger      (Logger):          Used for logging entry, exit and possibly arguments.
        
        Keyword Args:
            to_log_call (bool):            Whether to log call or not. This overrides all other arguments. It will be
                                           stored as a global variable on the function, which can be changed at runtime.

            to_print_args  (bool):         Whether to output the arguments and keyword arguments passed to the function.
                                           This should not automatically be true as some arguments may not be printable
                                           or may be expensive to print. Thus, it should be up to the developer to use
                                           their own discretion. Further, we don't want to break their existing code. It
                                           will be stored as a global variable on the function, which can be changed at
                                           runtime.

            to_print_time(bool):           Prints the time it took to run the wrapped callable.

            to_print_exception  (bool):    Whether to print the traceback when an exception is raise. It will be stored
                                           as a global variable on the function, which can be changed at runtime.
        
        Returns:
            log_call_decorator (for wrapping)
    """

    def log_call_decorator(callable):
        """
            The actual decorator, which is what is returned to decorate the callable in question.

            Args:
                callable:    Anything that can be called function, method, functor, lambda, etc.
        
            Returns:
                log_call_callable_wrapped, which is wrapped around the function in question.
        """

        @wrappers.wraps(callable)
        @wrappers.static_variables(to_log_call = to_log_call,
                                             to_print_args = to_print_args,
                                             to_print_time = to_print_time,
                                             to_print_exception = to_print_exception)
        def log_call_callable_wrapped(*args, **kwargs):
            """
                This is what will replace the original callable. It will behave the same except it will now log its
                entrance and exit. If set, it will log its parameters too.

                Args:
                    callable:    Anything that can be called function, method, functor, lambda, etc.

                Returns:
                    log_call_callable_wrapped, which is wrapped around the function in question.
            """

            result = None
            # This allows keyword arguments to be turned on or off at runtime.
            if log_call_callable_wrapped.to_log_call:
                # Log that we have entered the callable in question.
                logger.debug("Entering callable: \"" + callable.__name__ + "\".")

                # Output arguments and keyword arguments if acceptable.
                # This allows keyword arguments to be turned on or off at runtime.
                #
                # Note: We have used log_call_callable_wrapped.to_print_args.
                #       However, we cannot define this until after as wrapping will lose this variable.
                if (log_call_callable_wrapped.to_print_args):
                    logger.debug("Arguments: \"" + str(args) + "\"" + os.linesep + "Keyword Arguments: \"" + str(kwargs) + "\".")

                # We don't return immediately. Why? We want to know if this succeeded or failed.
                # So, we want the log message below to print after the function runs.
                diff_time = 0.0
                start_time = time.time()
                try:
                    result = callable(*args, **kwargs)
                except:
                    if log_call_callable_wrapped.to_print_exception:
                        logger.error(traceback.format_exc())
                    raise
                end_time = time.time()
                diff_time += (end_time - start_time)

                # Log that we have exited the callable in question.
                logger.debug("Exiting callable: \"" + callable.__name__ + "\".")

                if log_call_callable_wrapped.to_print_time:
                    logger.debug("Run time for callable: \"" + callable.__name__ + "\" is \"" + str(diff_time) + " s\".")
            else:
                # We don't return immediately. Why? We want to know if this succeeded or failed.
                # So, we want the log message below to print after the function runs.
                result = callable(*args, **kwargs)


            # Return the result even None.
            return(result)

        # The callable wrapped.
        return(log_call_callable_wrapped)

    # The arguments passed to the decorator for easy access.
    return(log_call_decorator)


def log_class(logger, to_log_call = True, to_print_args = False, to_print_time = True, to_print_exception = False):
    """
        Takes a given logger and uses it to log entering and leaving all methods of the decorated class.
        Intended to be used as a decorator that takes a few arguments.

        Args:
            logger      (Logger):          Used for logging entry, exit and possibly arguments.

        Keyword Args:
            to_log_call (bool):            Whether to log call or not. This overrides all other arguments. It will be
                                           stored as a global variable on the methods, which can be changed at runtime.

            to_print_args  (bool):         Whether to output the arguments and keyword arguments passed to the function.
                                           This should not automatically be true as some arguments may not be printable
                                           or may be expensive to print. Thus, it should be up to the developer to use
                                           their own discretion. Further, we don't want to break their existing code. It
                                           will be stored as a global variable on the methods, which can be changed at
                                           runtime.

            to_print_time(bool):           Prints the time it took to run the wrapped callable.

            to_print_exception  (bool):    Whether to print the traceback when an exception is raise. It will be stored
                                           as a global variable on the methods, which can be changed at runtime.

        Returns:
            log_call_decorator (for wrapping)
    """

    return(wrappers.class_decorate_all_methods(log_call(logger,
                                                                  to_log_call = to_log_call,
                                                                  to_print_args = to_print_args,
                                                                  to_print_time = to_print_time,
                                                                  to_print_exception = to_print_exception)))


def qt_log_class(logger, to_log_call = True, to_print_args = False, to_print_time = True, to_print_exception = False):
    """
        Takes a given logger and uses it to log entering and leaving all methods of the decorated class.
        Intended to be used as a decorator that takes a few arguments.

        Args:
            logger      (Logger):          Used for logging entry, exit and possibly arguments.

        Keyword Args:
            to_log_call (bool):            Whether to log call or not. This overrides all other arguments. It will be
                                           stored as a global variable on the methods, which can be changed at runtime.

            to_print_args  (bool):         Whether to output the arguments and keyword arguments passed to the function.
                                           This should not automatically be true as some arguments may not be printable
                                           or may be expensive to print. Thus, it should be up to the developer to use
                                           their own discretion. Further, we don't want to break their existing code. It
                                           will be stored as a global variable on the methods, which can be changed at
                                           runtime.

            to_print_time(bool):           Prints the time it took to run the wrapped callable.

            to_print_exception  (bool):    Whether to print the traceback when an exception is raise. It will be stored
                                           as a global variable on the methods, which can be changed at runtime.

        Returns:
            log_call_decorator (for wrapping)
    """

    return(wrappers.qt_class_decorate_all_methods(log_call(logger,
                                                                     to_log_call = to_log_call,
                                                                     to_print_args = to_print_args,
                                                                     to_print_time = to_print_time,
                                                                     to_print_exception = to_print_exception)))


@wrappers.static_variables(to_run = True)
def memory_profiler(logger, interval = 1, level=logging.INFO):
    """
        Runs forever get information about memory usage and dumping it to the logger provided at the given interval.

        Args:
            logger (Logger):               Used for logging memory profiling information.

        Keyword Args:
            interval (int or float):       Number of seconds to wait before issuing more profile information.
    """

    current_process = psutil.Process(os.getpid())

    while memory_profiler.to_run:
        logger.log(level, "Memory info = " + repr(current_process.memory_info_ex()))
        time.sleep(interval)
