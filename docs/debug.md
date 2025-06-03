For debugging the test `test_env_sample_fallback` in `tests/test_settings.py`, I inserted following print lines right before `assertion` statement:

```python
print("Resolved dotenvs:", settings.resolve_loaded_dotenv_paths())
print("Directory contents:", list(tmp_path.iterdir()))
print("get_root_dir():", settings.get_root_dir())
print("is_test_mode():", settings    print("Resolved dotenvs:", settings.resolve_loaded_dotenv_paths())
print("Directory contents:", list(tmp_path.iterdir()))
print("get_root_dir():", settings.get_root_dir())
print("is_test_mode():", settings.is_test_mode()).is_test_mode())
```
