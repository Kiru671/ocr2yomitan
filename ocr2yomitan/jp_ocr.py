import argparse
import sys
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from manga_ocr import MangaOcr
from PIL import Image, ImageGrab
import threading, time, json, webbrowser
import hashlib
import io, os

app = Flask(__name__)
CORS(app) 
latest_text = ""
history = []
ocr_instance = None
last_clipboard_hash = None

CONFIG_PATH = "config.json"

def create_default_config():
    """Create default configuration"""
    return {
        "host": "127.0.0.1",
        "port": 5000,
        "open_browser": True,
        "check_interval": 0.5,
    }

def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            print(f"✓ Loaded config from {CONFIG_PATH}")
        except Exception as e:
            print(f"⚠ Error loading config: {e}")
            print("Using default configuration...")
            config = create_default_config()
    else:
        config = create_default_config()
        # Save default config
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            print(f"✓ Created default config at {CONFIG_PATH}")
        except Exception as e:
            print(f"⚠ Could not save config: {e}")
    
    return config

config = load_config()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/latest")
def latest_json():
    global latest_text
    return jsonify({"text": latest_text})

@app.route("/config")
def config_endpoint():
    """Return current configuration"""
    return jsonify(config)

@app.route("/history")
def get_history():
    return jsonify(history)

@app.route("/status")
def status():
    """Return status information"""
    clipboard_available = True
    try:
        # Test if clipboard is accessible
        ImageGrab.grabclipboard()
    except Exception:
        clipboard_available = False
    
    return jsonify({
        "clipboard_available": clipboard_available,
        "latest_text": latest_text,
        "ocr_ready": ocr_instance is not None,
        "last_processed": last_clipboard_hash is not None
    })

def get_clipboard_image():
    """Get image from clipboard if available"""
    try:
        clipboard_content = ImageGrab.grabclipboard()
        if isinstance(clipboard_content, Image.Image):
            return clipboard_content
    except Exception as e:
        print(f"⚠ Clipboard access error: {e}")
    return None

def get_image_hash(image):
    """Generate hash of image to detect changes"""
    try:
        # Convert image to bytes for hashing
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        return hashlib.md5(img_bytes).hexdigest()
    except Exception:
        return None

def clipboard_ocr_loop():
    global latest_text, ocr_instance, last_clipboard_hash
    
    print("🔄 Initializing OCR...")
    try:
        ocr_instance = MangaOcr()
        print("✓ OCR initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize OCR: {e}")
        return
    
    check_interval = config.get("check_interval", 0.5)
    
    print("📋 Monitoring clipboard for images...")
    print(f"⏱️ Check interval: {check_interval}s")
    print("\n💡 How to use:")
    print("   1. Take a screenshot (Windows: Win+Shift+S, Mac: Cmd+Shift+4)")
    print("   2. Screenshot is automatically copied to clipboard")
    print("   3. OCR will process it automatically")
    print("   4. View results in the web interface\n")

    while True:
        try:
            clipboard_image = get_clipboard_image()
            
            if clipboard_image:

                width, height = clipboard_image.size

                # Generate hash to check if this is a new image
                current_hash = get_image_hash(clipboard_image)
                
                if current_hash and current_hash != last_clipboard_hash:
                    print(f"📸 New clipboard image detected ({width}x{height})")
                    
                    try:
                        # Process with OCR
                        ocr_result = ocr_instance(clipboard_image)
                        
                        if ocr_result and ocr_result.strip():
                            latest_text = ocr_result
                            history.append({
                                "text": ocr_result,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                            # Limit history to last 50 items (optional)
                            if len(history) > 50:
                                history.pop(0)
                            print(f"📝 OCR result: {ocr_result[:100]}{'...' if len(ocr_result) > 100 else ''}")
                        else:
                            latest_text = "(No text detected)"
                            print("📝 No text detected in image")
                        
                        last_clipboard_hash = current_hash
                        
                    except Exception as e:
                        print(f"❌ Error processing clipboard image: {e}")
                        latest_text = f"Error processing image: {str(e)}"
                        
        except Exception as e:
            print(f"❌ Error in clipboard monitoring: {e}")
            
        time.sleep(check_interval)

def print_startup_info():
    """Print helpful startup information"""
    print("\n" + "="*60)
    print("🎌 Japanese OCR Server - Clipboard Mode")
    print("="*60)
    print("📋 Mode: Clipboard screenshot monitoring")
    print(f"🌐 Server: http://{config['host']}:{config['port']}")
    print(f"⏱️ Check interval: {config.get('check_interval', 0.5)}s")
    
    print("\n🖼️ Screenshot Instructions:")
    print("   • Windows: Win + Shift + S (Snipping Tool)")
    print("   • Mac: Cmd + Shift + 4 (Screenshot to clipboard)")
    print("   • Linux: Use your distro's screenshot tool with clipboard option")
    
    print("\n💡 Workflow:")
    print("   1. Take screenshot → automatically copies to clipboard")
    print("   2. OCR processes clipboard image automatically")
    print("   3. View extracted text in web interface")
    print("   4. Take new screenshot to process next image")
    
    print(f"\n⚙️ Configuration:")
    print(f"   • Edit {CONFIG_PATH} to customize settings")
    print("   • Press Ctrl+C to stop")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Japanese OCR Server using clipboard screenshots')
    parser.add_argument('--port', '-p', type=int, help='Server port (default: 5000)')
    parser.add_argument('--host', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--no-browser', action='store_true', help="Don't open browser automatically")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--interval', '-i', type=float, help='Clipboard check interval in seconds')
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.port:
        config['port'] = args.port
    if args.host:
        config['host'] = args.host
    if args.no_browser:
        config['open_browser'] = False
    if args.interval:
        config['check_interval'] = args.interval
    
    print_startup_info()
    
    # Start clipboard monitoring in background
    clipboard_thread = threading.Thread(target=clipboard_ocr_loop, daemon=True)
    clipboard_thread.start()
    
    # Open browser if configured
    if config.get("open_browser", True):
        threading.Timer(1.5, lambda: webbrowser.open(
            f"http://{config['host']}:{config['port']}"
        )).start()
    
    try:
        app.run(
            host=config["host"], 
            port=config["port"], 
            debug=args.debug if 'args' in locals() else False
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()