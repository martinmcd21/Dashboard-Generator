import subprocess
import shutil
import os

def generate_pbix(template_path, csv_path, output_path):
    workdir = "pbix_work"
    shutil.rmtree(workdir, ignore_errors=True)

    subprocess.run([
        "pbi-tools",
        "extract",
        template_path,
        "-o", workdir
    ], check=True)

    shutil.copy(csv_path, f"{workdir}/Data/Model/Data.csv")

    subprocess.run([
        "pbi-tools",
        "compile",
        workdir,
        "-o", output_path
    ], check=True)
