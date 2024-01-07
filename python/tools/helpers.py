from regex import R


def run_python(pythonScript: str):
    import os
    import sys   
    import subprocess
    
    # write out script
    filename="runpython2.py"
    work_dir = "./pythonscript"

    filepath = os.path.join(work_dir, filename)
    stdoutpath = os.path.join(work_dir, 'stdout.txt')
    stderrpath = os.path.join(work_dir, 'stderr.txt')
    file_dir = os.path.dirname(filepath)

    os.makedirs(file_dir, exist_ok=True)
    if pythonScript is not None:
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(pythonScript) # type: ignore
    
    cmd = [
        sys.executable, filepath,
        ]
    
    f = open(stdoutpath, "w")
    g = open(stderrpath, "w")
    subprocess.run(cmd, stdout=f, stderr=g, timeout=60)
    f.close()
    g.close()

    try:
        with open(stdoutpath, "r") as f:
            stdout = f.read() # type: ignore

        with open(stderrpath, "r") as f:
            stderr = f.read() # type: ignore
        
        if stderr == '':
            # return ('success', stdout) # type: ignore
            return stdout
        else:
            # return ('error', stderr) # type: ignore
            return stderr
        
    except Exception as e:
        # return 'error', e # type: ignore
        return e
    
def exposed_conversion_rate(start_date: str, window: int) -> float:
    """
    Returns the conversion rate for a given date range.
    """
    import os
    import psycopg2
    import csv
    from datetime import datetime, timedelta

    # Environment variables holding credentials and connection details
    host = os.environ['RENDER_PG_HOST']
    database = os.environ['RENDER_PG_NAME']
    username = os.environ['RENDER_PG_USER']
    password = os.environ['RENDER_PG_PASSWORD']

    return 1.0