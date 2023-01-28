import functools
import typing


def post_notify(notifier: typing.Callable):
    def decorate(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            notifier()
            return result
        return wrapper
    return decorate
