from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "bot_cpp",                 # module name
        ["bot.cpp"],            # source file
        extra_compile_args=["/O2"], # MSVC optimization
    ),
]

setup(
    name="bot_cpp",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
