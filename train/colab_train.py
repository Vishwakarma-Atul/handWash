"""
YOLOv8 Training for Google Colab with async checkpoint saving to Google Drive
"""

import os
import shutil
import threading
from pathlib import Path
from google.colab import drive
from ultralytics import YOLO
from ultralytics.utils.callbacks import Callbacks


class GoogleDriveCallback(Callbacks):
    """Async checkpoint saving to Google Drive"""
    
    def __init__(self, gdrive_dir, save_interval=5):
        self.gdrive_dir = gdrive_dir
        self.save_interval = save_interval
    
    def _save_async(self, src, dst, label):
        """Copy file to Google Drive (async)"""
        try:
            shutil.copy2(src, dst)
            print(f"✓ {label} → Google Drive")
            os.remove(src)  # Clean up temp
        except Exception as e:
            print(f"✗ Save failed: {e}")
    
    def on_train_epoch_end(self, trainer):
        """Save checkpoint every N epochs"""
        if (trainer.epoch + 1) % self.save_interval == 0:
            epoch = trainer.epoch + 1
            src = trainer.last / 'weights' / 'last.pt'
            
            if src.exists():
                # Copy to temp (sync, fast)
                temp = os.path.join(self.gdrive_dir, f'._tmp_epoch_{epoch:03d}.pt')
                try:
                    shutil.copy2(str(src), temp)
                except Exception as e:
                    print(f"✗ Temp copy failed: {e}")
                    return
                
                # Upload async
                dst = os.path.join(self.gdrive_dir, f'checkpoint_epoch_{epoch:03d}.pt')
                thread = threading.Thread(
                    target=self._save_async,
                    args=(temp, dst, f"Epoch {epoch}"),
                    daemon=True
                )
                thread.start()


def main():
    """Train YOLOv8 with Google Drive integration"""
    
    # Mount Google Drive
    print("Mounting Google Drive...")
    drive.mount('/content/drive')
    
    gdrive_dir = '/content/drive/MyDrive/handWash_models'
    os.makedirs(gdrive_dir, exist_ok=True)
    
    # Load dataset
    dataset_path = '/content/drive/MyDrive/handWash/dataset'
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return
    
    # Train
    model = YOLO('yolov8n-cls.pt')
    callback = GoogleDriveCallback(gdrive_dir, save_interval=5)
    
    results = model.train(
        data=dataset_path,
        epochs=30,
        imgsz=256,
        batch=81,
        dropout=0.3,
        optimizer='Adam',
        plots=True,
        hsv_h=0.030,
        hsv_s=0.14,
        hsv_v=0.8,
        fliplr=0.3,
        perspective=0.005,
        degrees=15,
        shear=0.2,
        mixup=1.0,
        pretrained=True,
        device=0,
        name='handWash_classifier',
        callbacks=[callback]
    )
    
    # Save final models
    print("\nFinal save...")
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    
    best_src = results.save_dir / 'weights' / 'best.pt'
    if best_src.exists():
        shutil.copy2(best_src, os.path.join(gdrive_dir, f'best_final_{timestamp}.pt'))
        print(f"✓ Best model saved")
    
    # List saved models
    print(f"\nSaved models in {gdrive_dir}:")
    for f in sorted(os.listdir(gdrive_dir)):
        size = os.path.getsize(os.path.join(gdrive_dir, f)) / (1024*1024)
        print(f"  {f:<45} {size:>6.2f} MB")


if __name__ == "__main__":
    main()
