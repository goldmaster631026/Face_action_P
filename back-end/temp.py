import cv2 as cv
import time
import json

def main_facial_api(video, facial_unit, caption_unit):
    global frame_number, frame_json

    frame_number = 0
    frame_json = {}
    
    # Uncomment these lines if you are using GPU
    # if args["gpu"] > 0:
    #     print("setting preferable backend and target to CUDA...")
    #     gp.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
    #     gp.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

    video_capture = cv.VideoCapture(video)
    fps = video_capture.get(cv.CAP_PROP_FPS)
    start_time = time.time()
    
    fps = int(fps)
    print("fps: " + str(fps))
    print(start_time)
    cap_img = ' '

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        # Process frame every 132 frames
        if frame_number % 132 == 0:
            frame_resized = cv.resize(frame, (800, 600))
            frame_time = frame_number / fps
            Face_capture(frame_resized, frame_time)

            # Check if the key "person 0" is present in the dictionary
            if "person 0" in frame_json.get("Frame_" + str(frame_time) + "/s", {}):
                frame_json["Frame_" + str(frame_time) + "/s"]["Caption of Frame"] = cap_img
            else:
                frame_json["Frame_" + str(frame_time) + "/s"]["Caption of Frame"] = "There is no person in this frame."

        # Process caption every 132 frames as well
        if frame_number % 132 == 0:
            frame_resized = cv.resize(frame, (256, 256))
            cap_img = main_image_caption(frame_resized)
            print("Image_caption: " + cap_img)

        frame_number += 1

    video_capture.release()
    # Uncomment if you're using video writer
    # video_writer.release()
    frame_number = 0
    end_time = time.time()
    print(end_time - start_time)
    return json.dumps(frame_json, cls=NumpyEncoder, indent=4)