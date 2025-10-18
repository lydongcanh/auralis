import os

def get_required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    
    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
    
    return value