import warnings

warnings.warn(
    "starlette-flask is archived and no longer maintained. "
    "The existing code works but will receive no further updates. "
    "Consider vendoring the middleware directly into your project. "
    "See https://github.com/hasansezertasan/starlette-flask for details.",
    FutureWarning,
    stacklevel=2,
)
