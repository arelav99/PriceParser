from pymonad.either import Either, Right, Left

def safe_exec(f, *args, **kwargs) -> Either:
    try:
        return Right(f(*args, **kwargs))
    except Exception as e:
        return Left(str(e))


class AsyncIOMonad:
    def __init__(self, effect_fn):
        self.effect_fn = effect_fn

    async def run(self, *args, **kwargs):
        return await self.effect_fn(*args, **kwargs)
    
    def then(self, other_func):
        async def composed(*args, **kwargs):
            result = await self.effect_fn(*args, **kwargs)
            if result is not None:
                next_io = other_func(result)
                if isinstance(next_io, self.__class__):
                    return await next_io.run()
                return next_io
            return None

        return self.__class__(composed)
