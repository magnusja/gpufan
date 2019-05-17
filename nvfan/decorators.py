import functools

import nvfan


def base_decorator(mode_function, **kwargs):

    def decorator(function):
        outer_kwargs = kwargs

        if 'device' not in outer_kwargs:
            outer_kwargs['device'] = None

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            mode_function(**outer_kwargs)
            maybe_result = function(*args, **kwargs)
            nvfan.driver(outer_kwargs['device'])
            return maybe_result

        return wrapper

    return decorator


aggressive = functools.partial(base_decorator, mode_function=nvfan.aggressive)
constant = functools.partial(base_decorator, mode_function=nvfan.constant)
driver = functools.partial(base_decorator, mode_function=nvfan.driver)
