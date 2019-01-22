# template script to implement a computer vision feature via surround
import logging
import cv2
import face_recognition as fr


# function(s) to pre-process
def bgr_to_rgb(bgr_img_array):
    # convert BGR --> RGB space
    rgb_img_array = cv2.cvtColor(bgr_img_array, cv2.COLOR_BGR2RGB)
    return rgb_img_array


# generic template to apply inference on an image array
def inference_frame(img_array, config_settings=None):
    """
    Do something with the `img_array'
    :param img_array:
    :param config_settings:
    :return: Inference information
    """
    # replicate the inference of a face location algorithm
    face_coords = fr.face_locations(img_array)
    return face_coords


def main():
    logging.info("This is the main function ...")
    # skeleton for video stream
    video_stream = cv2.VideoCapture(0)
    # iteration to grab frames from the video
    while True:
        # grab the frame array
        boolean_flag, frame_img_bgr = video_stream.read()
        # pre-process the frame - rescale
        frame_img_bgr_resized = cv2.resize(frame_img_bgr, None, fx=0.5, fy=0.5)
        # map to rgb space
        frame_img_rgb = bgr_to_rgb(frame_img_bgr_resized)
        # apply face location
        face_locations = fr.face_locations(frame_img_rgb)
        # visual display of faces bounding boxes
        for (y1, x2, y2, x1) in face_locations:
            cv2.rectangle(frame_img_bgr_resized, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # show the processed frame
        cv2.imshow('Frame', frame_img_bgr_resized)
        # stop the video stream via the keyboard: "q"
        keyboard_event_stop = cv2.waitKey(1) & 0xFF
        if keyboard_event_stop == ord("q"):
            break


if __name__ == '__main__':
    main()
