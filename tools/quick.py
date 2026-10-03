"""Construção rápida + provas para iteração de desenho."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))
from yauren.build import main as build_main  # noqa

SP = os.environ.get("SP", "/tmp")
weights = [a for a in sys.argv[1:] if a.isdigit()]
t = time.time()
build_main(weights)
print("build", round(time.time() - t, 1), "s")
