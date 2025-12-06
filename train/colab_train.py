"""
YOLOv8 Training for Google Colab with async checkpoint saving to Google Drive
"""

import os
import shutil
import threading
from pathlib import Path
from google.colab import drive
from ultralytics import YOLO


def create_gdrive_callback(gdrive_dir, save_interval=5):
    """Create callback for async checkpoint saving to Google Drive"""
    
    def _save_async(src, dst, label):
        """Copy file to Google Drive (async)"""
        try:
            shutil.copy2(src, dst)
            print(f"✓ {label} → Google Drive")
            os.remove(src)
        except Exception as e:
            print(f"✗ Save failed: {e}")
    
    def on_train_epoch_end(trainer):
        """Save checkpoint every N epochs"""
        if (trainer.epoch + 1) % save_interval == 0:
            epoch = trainer.epoch + 1
            src = trainer.last / 'weights' / 'last.pt'
            
            if src.exists():
                temp = os.path.join(gdrive_dir, f'._tmp_epoch_{epoch:03d}.pt')
                try:
                    shutil.copy2(str(src), temp)
                except Exception as e:
                    print(f"✗ Temp copy failed: {e}")
                    return
                
                dst = os.path.join(gdrive_dir, f'checkpoint_epoch_{epoch:03d}.pt')
                thread = threading.Thread(
                    target=_save_async,
                    args=(temp, dst, f"Epoch {epoch}"),
                    daemon=True
                )
                thread.start()
    
    return on_train_epoch_end


def main():
    """Train YOLOv8 with Google Drive integration"""
    
    # Mount Google Drive
    print("Mounting Google Drive...")
    drive.mount('/content/drive')
    
    gdrive_dir = '/content/drive/MyDrive/handWash_models'
    os.makedirs(gdrive_dir, exist_ok=True)
    
    # Copy dataset from Google Drive to Colab local space for faster training
    print("Copying dataset to local Colab space...")
    gdrive_dataset = '/content/drive/MyDrive/handWash/dataset'
    dataset_path = '/content/dataset'
    
    if os.path.exists(gdrive_dataset):
        if not os.path.exists(dataset_path):
            shutil.copytree(gdrive_dataset, dataset_path)
            print(f"✓ Dataset copied to {dataset_path}")
        else:
            print(f"✓ Dataset already exists at {dataset_path}")
    else:
        print(f"Dataset not found at {gdrive_dataset}")
        return
    
    # Train
    model = YOLO('yolov8n-cls.pt')
    callback = create_gdrive_callback(gdrive_dir, save_interval=5)
    model.add_callback('on_train_epoch_end', callback)
    
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
        name='handWash_classifier'
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
