import os, json
from datetime import datetime
path_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'uploads'))

def finalize_metadata(folder, questions_count):
    path = os.path.join(path_base, folder)
    meta_path = os.path.join(path, 'meta.json')
    if not os.path.exists(meta_path):
        return
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    meta['finishedAt'] = datetime.now().isoformat()
    meta['questionsCount'] = questions_count
    with open(meta_path, 'w') as f:
        json.dump(meta, f)
