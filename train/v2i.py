import cv2
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def combine_frames_mean(frames):
    """
    Merges multiple frames at pixel level using simple mean.
    """
    if not frames:
        return None
    
    stacked = np.array(frames, dtype=np.float32)
    return np.mean(stacked, axis=0).astype(np.uint8)

def combine_frames_weighted(frames, alpha=0.1):
    """
    Exponential Moving Average (EMA) across frames.
    F'_n = alpha*F_n + (1-alpha)*F'_{n-1}
    Latest frame gets more weight with exponential decay to older frames.
    """
    if not frames:
        return None
    
    n_frames = len(frames)
    
    # Calculate exponential weights: [alpha*(1-alpha)^4, ..., alpha*(1-alpha), alpha]
    weights = np.array([alpha * ((1 - alpha) ** (n_frames - 1 - i)) for i in range(n_frames)], dtype=np.float32)
    # Normalize so weights sum to 1
    weights = weights / np.sum(weights)
    
    # Weighted average
    stacked = np.array(frames, dtype=np.float32)
    weights = weights.reshape(n_frames, 1, 1, 1)
    return np.sum(stacked * weights, axis=0).astype(np.uint8)

def combine_frames(frames):
    """
    Wrapper function to choose between averaging methods.
    """
    # return combine_frames_mean(frames)
    return combine_frames_weighted(frames)  # Uncomment to use weighted average

def video_to_images(args):
    """
    Converts a video into images, maintains folder structure, and splits into train/val sets.
    Optionally combines frames.
    """
    video_path, dataset_path, FPS, val_split, COMB_FRAMES, COMB_PER_SEC = args
    vidcap = cv2.VideoCapture(video_path)
    original_fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(1, int(original_fps / int(FPS)))
    
    # For combining: group_interval defines where each combination group starts
    group_interval = max(1, int(original_fps / int(COMB_PER_SEC))) if COMB_FRAMES > 1 else frame_interval

    success, image = vidcap.read()
    frame_num = 0
    count = 0
    frame_buffer = []
    group_start_frame = 0
    
    # Create the output directory if it doesn't exist
    output_dir = os.path.join(dataset_path, "train", video_path.strip("./").split('/')[1])
    os.makedirs(output_dir, exist_ok=True)

    while success:
        if COMB_FRAMES > 1:
            # Combine frames mode: take COMB_FRAMES consecutive frames starting at group boundaries
            if frame_num >= group_start_frame and frame_num < group_start_frame + COMB_FRAMES:
                frame_buffer.append(image)
                
                if len(frame_buffer) == COMB_FRAMES:
                    combined = combine_frames(frame_buffer)
                    frame_path = os.path.join(output_dir, f"{os.path.basename(video_path).split('.')[0]}_{count:04d}.jpg")
                    cv2.imwrite(frame_path, combined)
                    
                    # Randomly assign to validation set
                    if (count % int(100 // val_split)) == 0:
                        val_dir = output_dir.replace("train", "val")
                        os.makedirs(val_dir, exist_ok=True)
                        val_frame_path = frame_path.replace("train", "val")
                        os.rename(frame_path, val_frame_path)
                    
                    count += 1
                    frame_buffer = []
                    group_start_frame += group_interval
        else:
            # Original mode: save individual frames
            if frame_num % frame_interval == 0:
                frame_path = os.path.join(output_dir, f"{os.path.basename(video_path).split('.')[0]}_{count:04d}.jpg")
                cv2.imwrite(frame_path, image)

                # Randomly assign to validation set
                if (count % int(100 // val_split)) == 0:
                    val_dir = output_dir.replace("train", "val")
                    os.makedirs(val_dir, exist_ok=True)
                    val_frame_path = frame_path.replace("train", "val")
                    os.rename(frame_path, val_frame_path)
                count += 1
        
        success, image = vidcap.read()
        frame_num += 1

def process_videos(video_path, dataset_path, FPS=10, val_split=20, COMB_FRAMES=1, COMB_PER_SEC=2):
    """
    Processes all videos in a directory tree.
    Args:
        FPS: Frame rate for saving individual frames
        COMB_FRAMES: Number of frames to combine into one (1 = no combining)
        COMB_PER_SEC: Number of combinations per second
    """
    video_paths = []
    for dirpath, _, filenames in os.walk(video_path):
        for filename in filenames:
            if filename.endswith((".mp4", ".avi", ".mov")):  # Add more video formats if needed
                _video_path = os.path.join(dirpath, filename)
                video_paths.append((_video_path, dataset_path, FPS, val_split, COMB_FRAMES, COMB_PER_SEC))

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(video_to_images, video_paths), total=len(video_paths), desc="Processing Videos"))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", help="root path of video files", default='.')
    parser.add_argument("--dataset_path", help="Output path for dataset", default='.')
    parser.add_argument("--FPS", help="Frames per second for individual frame saving", default=30, type=int)
    parser.add_argument("--val_split", help="percent of val dataset", default=25, type=int)
    parser.add_argument("--COMB_FRAMES", help="Number of frames to combine (1=no combining)", default=5, type=int)
    parser.add_argument("--COMB_PER_SEC", help="Number of frame combinations per second", default=2, type=int)
    args = parser.parse_args()
    print(args.video_path, args.dataset_path)

    process_videos(video_path=args.video_path, dataset_path=args.dataset_path, FPS=args.FPS, 
                   val_split=args.val_split, COMB_FRAMES=args.COMB_FRAMES, COMB_PER_SEC=args.COMB_PER_SEC)

    ### python -m train.v2i --video_path "./HandWashDataset" --dataset_path "./dataset"

    ### yolo classify train data=/g/Python/Projects/handWash/dataset model=yolov8n-cls.pt epochs=30 imgsz=256 batch=81 dropout=0.3 name=/g/Python/Projects/handWash/classifier_ optimizer=Adam plots=True hsv_h=0.030 hsv_s=0.14 hsv_v=0.8 fliplr=0.3 perspective=0.0004 degrees=15 shear=0.2 perspective=0.005 mixup=1.0 pretrained=yolov8n-cls.pt
