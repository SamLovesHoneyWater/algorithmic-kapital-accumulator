import hashlib
import json
import os
import pandas as pd

def hash_dict(d):
    """
    Generate a hash for a dictionary.

    Args:
        d (dict): The dictionary to hash.

    Returns:
        str: The resulting hash.
    """
    # Convert the dictionary to a JSON string
    dict_str = json.dumps(d, sort_keys=True, default=str)
    
    # Create a hash object
    hash_obj = hashlib.sha256()
    
    # Update the hash object with the dictionary string
    hash_obj.update(dict_str.encode('utf-8'))
    
    # Return the hexadecimal digest of the hash
    return hash_obj.hexdigest()

def save_dataframe_to_cache(df, hash_str):
    """
    Save a dataframe to a cache directory with the given hash as the filename.

    Args:
        df (pd.DataFrame): The dataframe to save.
        hash (str): The hash to use as the filename.

    Raises:
        FileExistsError: If a file with the same hash already exists.
    """
    # Define the cache directory and file path
    cache_dir = "./cache"
    file_path = os.path.join(cache_dir, hash_str)

    # Create the cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    # Check if the file already exists
    if os.path.exists(file_path):
        raise FileExistsError(f"The file '{file_path}' already exists.")

    # Save the dataframe to the file
    df.to_csv(file_path, index=False)

def load_dataframe_from_cache(hash_str):
    """
    Load a dataframe from the cache directory with the given hash as the filename.

    Args:
        hash_str (str): The hash to use as the filename.

    Returns:
        pd.DataFrame: The loaded dataframe.
    """
    # Define the cache directory and file path
    cache_dir = "./cache"
    file_path = os.path.join(cache_dir, hash_str)

    # Check if the file exists
    if not os.path.exists(file_path):
        return

    # Load the dataframe from the file
    return pd.read_csv(file_path)
