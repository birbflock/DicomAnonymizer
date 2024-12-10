# Streamlit to Executable
#### [Reference: Folder Structure](https://github.com/birbflock/DicomAnonymizer.git)

## Create a Virtual Environment
- Create the environment based on `environment.yml`
- Do NOT change / upgrade the version of those dependencies
```bash
conda env create -f environment.yml
```

# Activate the Virtual Environment

```bash
conda activate <env-name>
```

# Add the Main File

In this case, `./application/DicomAnonymizer.py`

# Create an Entry Point for the Executable 
- Create `run_app.py`.
- Copy EXACTLY the code below.
```python
import os
import streamlit.web.bootstrap

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    flag_options = {
        "server.port": 8501,
        "global.developmentMode": False,
    }

    streamlit.web.bootstrap.load_config_options(flag_options=flag_options)
    flag_options["_is_running_with_streamlit"] = True
    streamlit.web.bootstrap.run(
        "./application/DicomAnonymizer.py",
        "streamlit run",
        [],
        flag_options,
    )
```

# Navigate to the Streamlit Path

In the version we are using, it is located at: `.env\Lib\site-packages\streamlit\web\cli.py`

# Add the Magic Function (TBC)
```python
# ... def main(log_level="info"):
# [...]
# You can use any name you prefer as long as it starts with an underscore
def _main_run_clExplicit(file, is_hello, args=[], flag_options={}):
    bootstrap.run(file, is_hello, args, flag_options)

# ...if __name__ == "__main__":
# ...    main()
```

# Create a Hook to Get Streamlit Metadata

- Create `.\hooks\hook-streamlit.py`.
- Copy EXACTLY the code below.
```python
from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('streamlit', include_py_files=False, include_datas=['**/*.*'])
```

# Compile the App
Run the following command to create the first `run_app.spec` file. 

```bash
pyinstaller --onefile --additional-hooks-dir=./hooks run_app.py --clean
# --onefile: Create a single output file
# --clean: Delete cache and remove temporary files before building
# --additional-hooks-dir: An additional path to search for hooks. This option can be used multiple times.
```

# Create Streamlit Configuration Files
- Create `.streamlit\config.toml`.
- Copy EXACTLY the code below.
```bash

[global]
developmentMode = false

[server]
port = 8502

[client]
showErrorDetails = True

```

# Copy the Configuration Files to the Output Folder (TBC)
```bash
xcopy /s /e .streamlit output/.streamlit
# Select D = directory
```

# Copy app.py to the Output Folder (TBC)
```bash
copy app.py output/app.py
```

# Add the Data to the New Hook in `run_app.spec`
- Amend the file with the codes below.
- Change `<path_to_env>` and `<env_name>` to your path.
```python
...
a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        (
        "<path_to_env>/envs/<env_name>/Lib/site-packages/altair/vegalite/v5/schema/vega-lite-schema.json",
        "./altair/vegalite/v5/schema/"
    ),
    (
        "<path_to_env>/envs/<env_name>/Lib/site-packages/streamlit/static",
        "./streamlit/static"
    ),
    (   
        "<path_to_app>/application",
        "./application"
    )
    ],
    hiddenimports=["streamlit", "streamlit-options-menu", "pydicom"],
    ...
)
...

```

# Build the Executable

```bash
pyinstaller run_app.spec --clean
```

## 🎈 It's done! run your `dist/DicomAnonymizer.exe` file and see the magic 🪄

<pre>Huge Credits From: 
- The organised workflow by <a href="https://github.com/jvcss/PyInstallerStreamlit/tree/master">jvcss</a>
- The <a href="https://discuss.streamlit.io/t/using-pyinstaller-or-similar-to-create-an-executable/902">discussion</a> in Streamlit forum</pre>