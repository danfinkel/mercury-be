def run_python(pythonScript: str) -> str:
    import os
    import sys   
    import subprocess
    
    # write out script
    filename="runpython.py"
    work_dir = "./pythonscript"

    filepath = os.path.join(work_dir, filename)
    stdoutpath = os.path.join(work_dir, 'stdout.txt')
    file_dir = os.path.dirname(filepath)

    os.makedirs(file_dir, exist_ok=True)
    if pythonScript is not None:
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(pythonScript) # type: ignore
    
    cmd = [
        sys.executable, filepath,
        ]
    
    f = open(stdoutpath, "w")
    subprocess.call(cmd, stdout=f)
    f.close()

    try:
        with open(stdoutpath, "r") as f:
            return f.read() # type: ignore
    except Exception as e:
        return e # type: ignore