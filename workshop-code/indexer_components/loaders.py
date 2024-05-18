import os
import hashlib
import requests

CACHE_PATH = "./loader_cache"

class DocLoader:

    @staticmethod
    def load_html(uri: str) -> str:
        """
        Loads the HTML document from the specified URI into the `doc` attribute.
        If the document exists in cache, load it from there.

        Returns:
            str: The content of the HTML document.
        """
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)

        hasher = hashlib.sha256()
        hasher.update(uri.encode('utf-8'))
        hash_filename = hasher.hexdigest()
        short_hash = hash_filename[:4]
        filename = f"{short_hash}-{uri.split('/')[-1]}.html"
        cached_file_path = os.path.join(CACHE_PATH, filename)

        if os.path.exists(cached_file_path):
            with open(cached_file_path, 'r', encoding='utf-8') as file:
                doc = file.read()
        else:
            response = requests.get(uri)
            response.raise_for_status()
            doc = response.text

            with open(cached_file_path, 'w', encoding='utf-8') as file:
                file.write(doc)

        return doc