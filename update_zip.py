import zipfile
import os
from pathlib import Path

zip_name = 'ecommerce-sentiment-rnn_kaggle.zip'
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    for file in Path('src').glob('*.py'):
        arcname = f'src/{file.name}'
        zf.write(file, arcname)
        print(f'Updated: {arcname}')
    
    for file in ['requirements.txt', 'README.md', 'ANNOTATION_GUIDELINE.md']:
        if os.path.exists(file):
            zf.write(file, file)

print(f'\n✓ Zip updated: {zip_name} ({os.path.getsize(zip_name)/1024:.1f} KB)')
