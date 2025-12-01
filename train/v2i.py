import cv2
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def video_to_images(args):
    """
    Converts a video into images, maintains folder structure, and splits into train/val sets.
    """
    video_path, dataset_path, FPS, val_split = args
    vidcap = cv2.VideoCapture(video_path)
    original_fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(1, int(original_fps / int(FPS)))

    success, image = vidcap.read()
    frame_num=0
    count = 0
    # Create the output directory if it doesn't exist
    # output_dir = os.path.join(dataset_path, "train", os.path.dirname(video_path))  # Get relative path
    output_dir = os.path.join(dataset_path, "train", video_path.strip("./").split('/')[1])
    os.makedirs(output_dir, exist_ok=True)

    while success:
        if (frame_num % frame_interval == 0):
            frame_path = os.path.join(output_dir, f"{os.path.basename(video_path).split('.')[0]}_{count:04d}.jpg")
            # print(video_path, frame_path)
            cv2.imwrite(frame_path, image)

            # Randomly assign to validation set
            if (count%int(100//val_split)) == 0:
                val_dir = output_dir.replace("train", "val")  # Replace 'train' with 'val'
                os.makedirs(val_dir, exist_ok=True)
                val_frame_path = frame_path.replace("train", "val")
                os.rename(frame_path, val_frame_path) 
            count += 1
        
        success, image = vidcap.read()
        frame_num += 1

def process_videos(video_path, dataset_path, FPS=10, val_split=20):
    """
    Processes all videos in a directory tree.
    """
    video_paths = []
    for dirpath, _, filenames in os.walk(video_path):
        for filename in filenames:
            if filename.endswith((".mp4", ".avi", ".mov")):  # Add more video formats if needed
                _video_path = os.path.join(dirpath, filename)
                video_paths.append( (_video_path, dataset_path, FPS, val_split) )
                # video_to_images((_video_path, dataset_path, FPS, val_split))

    # print(video_paths)
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        # executor.map(video_to_images, video_paths)
        list(tqdm(executor.map(video_to_images, video_paths), total=len(video_paths), desc="Processing Videos"))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", help="root path of video files", default='.')
    parser.add_argument("--dataset_path", help="Output path for dataset", default='.')
    parser.add_argument("--FPS", help="Frames per second", default=10)
    parser.add_argument("--val_split", help="percent of val dataset", default=25)
    args = parser.parse_args()
    print(args.video_path, args.dataset_path)

    process_videos(video_path=args.video_path, dataset_path=args.dataset_path, FPS=args.FPS, val_split=args.val_split)

    ### yolo classify train data=/g/Python/Projects/handWash/dataset model=yolov8n-cls.pt epochs=30 imgsz=256 batch=81 dropout=0.3 name=/g/Python/Projects/handWash/classifier_ optimizer=Adam plots=True hsv_h=0.030 hsv_s=0.14 hsv_v=0.8 fliplr=0.3 perspective=0.0004 degrees=15 shear=0.2 perspective=0.005 mixup=1.0 pretrained=yolov8n-cls.pt
