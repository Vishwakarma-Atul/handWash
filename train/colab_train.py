"""
YOLOv8 Training for Google Colab with concurrent backup to Google Drive
"""

import os
import shutil
import threading
import time
from google.colab import drive
from ultralytics import YOLO

# Global flag to stop backup thread
STOP_BACKUP = False


def train_model(dataset_path, training_name='handWash_classifier'):
    """Train YOLOv8 model locally"""
    print("Starting YOLOv8 training...")
    model = YOLO('yolov8n-cls.pt')
    
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
        name=training_name
    )
    
    print("✓ Training completed!")
    return results


def backup_weights(training_name, gdrive_backup_dir, interval=120):
    """Sync entire runs directory to Google Drive every 120 seconds"""
    print(f"✓ Backup thread started (interval: {interval}s)")
    
    while not STOP_BACKUP:
        try:
            time.sleep(interval)
            
            if not os.path.exists(training_name):
                continue
            
            # Sync entire directory to Google Drive
            try:
                shutil.copytree(training_name, gdrive_backup_dir, dirs_exist_ok=True)
                print(f"✓ Synced runs directory to Google Drive")
            except Exception as e:
                print(f"✗ Sync failed: {e}")
        
        except Exception as e:
            print(f"✗ Backup thread error: {e}")
    
    print("✓ Backup thread stopped")


def main():
    """Main: Run training and backup concurrently"""
    global STOP_BACKUP

    gdrive_backup_dir = '/content/drive/MyDrive/handWash/backups'
    os.makedirs(gdrive_backup_dir, exist_ok=True)
    
    # Copy dataset
    print("Copying dataset to local Colab space...")
    gdrive_dataset = '/content/drive/MyDrive/handWash/dataset'
    dataset_path = '/content/dataset'
    training_name = '/content/classify/handWash_classifier'
    
    if os.path.exists(gdrive_dataset):
        if not os.path.exists(dataset_path):
            shutil.copytree(gdrive_dataset, dataset_path)
            print(f"✓ Dataset copied")
        else:
            print(f"✓ Dataset already exists")
    else:
        print(f"Dataset not found at {gdrive_dataset}")
        return
    
    # Start backup thread
    backup_thread = threading.Thread(
        target=backup_weights,
        args=(training_name, gdrive_backup_dir, 120),
        daemon=True
    )
    backup_thread.start()
    
    # Start training
    try:
        results = train_model(dataset_path, training_name)
        
        # Final upload
        print("\nFinal upload to Google Drive...")
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        
        best_src = results.save_dir / 'weights' / 'best.pt'
        last_src = results.save_dir / 'weights' / 'last.pt'
        
        if best_src.exists():
            shutil.copy2(best_src, os.path.join(gdrive_backup_dir, f'best_{timestamp}.pt'))
            print(f"✓ Best model saved")
        
        if last_src.exists():
            shutil.copy2(last_src, os.path.join(gdrive_backup_dir, f'last_{timestamp}.pt'))
            print(f"✓ Last model saved")
    
    finally:
        STOP_BACKUP = True
        backup_thread.join(timeout=5)
    
    # List backups
    print(f"\nBackups in Google Drive:")
    for f in sorted(os.listdir(gdrive_backup_dir), reverse=True):
        size = os.path.getsize(os.path.join(gdrive_backup_dir, f)) / (1024*1024)
        print(f"  {f:<50} {size:>6.2f}MB")


if __name__ == "__main__":
    main()
