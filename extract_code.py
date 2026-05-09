import json

def extract_code(nb_path, out_path):
    with open(nb_path, encoding='utf-8') as f:
        nb = json.load(f)
    code = '\n'.join([''.join(cell.get('source', [])) for cell in nb['cells'] if cell['cell_type'] == 'code'])
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(code)

extract_code('notebooks/exploration.ipynb', 'exploration_code.py')
extract_code('models/models.ipynb', 'models_code.py')
