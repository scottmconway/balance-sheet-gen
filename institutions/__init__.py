import os

pkg_dir = os.path.dirname(os.path.abspath(__file__))

__all__ = [
    fname[:-3] for fname in os.listdir(pkg_dir) if fname.endswith("_institution.py")
]
__all__.append("institution")
