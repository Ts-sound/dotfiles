import argparse, os, glob, logging, json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s %(funcName)s:%(lineno)d]: %(message)s")

filepath = str(Path(__file__).resolve().parent)
logging.info(f"workpath: {filepath}")
