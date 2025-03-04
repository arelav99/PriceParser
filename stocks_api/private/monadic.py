from pymonad.either import Either, Right, Left

def safe_exec(f, *args, **kwargs) -> Either:
    try:
        return Right(f(*args, **kwargs))
    except Exception as e:
        return Left(str(e))