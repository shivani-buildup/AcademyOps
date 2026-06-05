import os
import zipfile

def zipdir(path, ziph):
    exclude_dirs = {'venv', 'venv2', 'venv_streamlit', '.git', '.gemini', '.pytest_cache', '__pycache__'}
    for root, dirs, files in os.walk(path):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, path)
            ziph.write(file_path, arcname)

if __name__ == '__main__':
    zip_path = r'c:\Users\Admin\Desktop\AcademyOps_Project.zip'
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    zipdir(r'c:\Users\Admin\Desktop\AcademyOps', zipf)
    zipf.close()
    
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Zip created successfully at {zip_path}")
    print(f"Size: {size_mb:.2f} MB")
