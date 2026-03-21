import zipfile
import os
from pathlib import Path

zip_name = 'ecommerce-sentiment-rnn_kaggle.zip'
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add src/ directory
    for file in Path('src').glob('*.py'):
        arcname = f'src/{file.name}'
        zf.write(file, arcname)
        print(f'✓ src/{file.name}')
    
    # Add data/data_final.csv (main input dataset)
    if os.path.exists('data/data_final.csv'):
        zf.write('data/data_final.csv', 'data/data_final.csv')
        print(f'✓ data/data_final.csv')
    
    # Add .gitkeep to data folder (so folder structure is preserved)
    zf.writestr('data/.gitkeep', '')
    print(f'✓ data/.gitkeep')
    
    # Add key documentation
    for file in ['requirements.txt', 'README.md', 'ANNOTATION_GUIDELINE.md']:
        if os.path.exists(file):
            zf.write(file, file)
            print(f'✓ {file}')

size_kb = os.path.getsize(zip_name) / 1024
print(f'\n✅ Zip file created: {zip_name} ({size_kb:.1f} KB)')
