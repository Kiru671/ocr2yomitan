import os
import subprocess
import sys
import shutil
from pathlib import Path

def get_manga_ocr_data_paths():
    """Get paths to manga_ocr data files"""
    try:
        import manga_ocr
        manga_ocr_path = Path(manga_ocr.__file__).parent
        data_path = manga_ocr_path / 'data'
        
        data_files = []
        for file in data_path.iterdir():
            if file.is_file():
                # Format: (source_path, destination_in_bundle)
                data_files.append((str(file), f'manga_ocr/data/{file.name}'))
        
        return data_files
    except ImportError:
        print("⚠ manga_ocr not installed, trying to find data files...")
        return []

def install_dependencies():
    """Install required packages"""
    packages = [
        'pyinstaller',
        'flask',
        'flask-cors',
        'manga-ocr',
        'pillow',
        'torch',
        'torchvision',
        'torchaudio'
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def build_executable():
    """Build the executable using PyInstaller"""
    # Get manga_ocr data files
    manga_ocr_data = get_manga_ocr_data_paths()
    
    # Clean up previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Build command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--add-data', 'templates;templates',
        '--add-data', 'config.json;.',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'flask_cors',
        '--name', 'JapaneseOCR',
    ]
    
    # Add manga_ocr data files to command
    for src, dest in manga_ocr_data:
        cmd.extend(['--add-data', f'{src};{dest}'])
    
    # Add the script name
    cmd.append('jp_ocr.py')
    
    print("Building with command:", ' '.join(cmd))
    
    # Build with PyInstaller
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("Build output:")
        print(result.stdout)
        if result.stderr:
            print("Build errors:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print("Output:", e.stdout)
        print("Error:", e.stderr)
        return False
    
    return True

def check_build():
    """Check if build was successful"""
    dist_dir = 'dist'
    if os.path.exists(dist_dir) and os.listdir(dist_dir):
        print(f"✓ Build successful! Executable is in the '{dist_dir}' folder.")
        return True
    else:
        print("✗ Build failed - dist folder is empty")
        return False

def main():
    print("Starting build process for Japanese OCR executable...")
    
    # Step 1: Install dependencies
    print("\n1. Installing dependencies...")
    install_dependencies()
    
    # Step 2: Build executable
    print("\n2. Building executable...")
    success = build_executable()
    
    # Step 3: Check result
    print("\n3. Checking build result...")
    if success and check_build():
        print("\n🎉 Build completed successfully!")
        print("\nTo run the application, navigate to the 'dist' folder and run 'JapaneseOCR.exe'")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

if __name__ == '__main__':
    main()