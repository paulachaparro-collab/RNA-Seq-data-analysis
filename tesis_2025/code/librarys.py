# 📊 Paquetes para manipulación de datos
import pandas as pd    # Manipulación de tablas y matrices
import numpy as np     # Cálculos matemáticos como log, media, etc.

# 📁 Manejo de archivos, rutas, texto
import os              # Rutas, archivos, directorios
import sys             # Acceso a argumentos de línea de comandos
import re              # Expresiones regulares
from io import StringIO  # Tratar texto como archivo en memoria

# 🔬 Lectura de archivos FASTA/FASTQ
from Bio import SeqIO  # Parte de Biopython

# 🧠 Subprocesos del sistema (pysradb, prefetch, etc.)
import subprocess

# 📈 Visualización de datos
import matplotlib.pyplot as plt

#en el notebook:
__all__ = ["pd", "np", "os", "sys", "re", "StringIO", "subprocess", "SeqIO", "plt"]
from libs_tesis import *
