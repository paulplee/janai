# janai
JanAI is a janitor for OpenAI objects. To help me maintain and clean up the mess of objects I created.

# How to run
1. `pip -m venv <myenv>`
2. `source <myenv>/bin/activate`
3. `pip install -r requirements`
4. Add the OpenAI API key and relevant project ID's to `.env`
5. `streamlit run Home.py`

# Streamlit VSCode debugging
Add the following configuration to the `launch.json`

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
    
        {
            "name": "Python Debugger: JanAI",
            "type": "debugpy",
            "request": "launch",
            "program": "${cwd}/.venv_janai/lib/python3.12/site-packages/streamlit",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": [
                "run",
                "Home.py"
            ],
        }
    ]
}
```