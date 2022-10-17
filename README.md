# Install
## Dependencies

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Tests
For running tests, you need to install the `requirements-development.txt` while in the virtual environment:

```
pip install -r requirements-development.txt
```

For running test, you need to have a `.env` file in the `tests` folder. The content should be like this:

```shell
EOL_API_TOKEN=abcdefghijklmnopqrstuvwxyz1234567890
```

where you substitute the part after the equal sign by your EOL API Key.

Subsequently, you can run:

```
pytest .
```