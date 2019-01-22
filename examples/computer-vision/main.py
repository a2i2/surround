# template script to implement a computer vision feature via surround
import logging
import cv2


def main():
    logging.info("This is the main function ...")
    # skeleton for video stream
    video_stream = cv2.VideoCapture(0)
    # iteration to grab frames from the video
    while True:
        # grab the frame array
        boolean_flag, frame_img_bgr = video_stream.read()
        # show the frame
        cv2.imshow('Frame', frame_img_bgr)
        # stop the video stream via the keyboard: "q"
        keyboard_event_stop = cv2.waitKey(1) & 0xFF
        if keyboard_event_stop == ord("q"):
            break


if __name__ == '__main__':
    main()
