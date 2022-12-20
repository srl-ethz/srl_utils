#! /usr/bin/env python3
import math

import cv2
import numpy as np


def get_ROI_coordinates(pt: tuple, sizeImg: tuple, sizeROI: tuple):
    """Return ROI range based on the center point and size of ROI.

    Args:
        pt (tuple): center of ROI
        sizeImg (tuple ): Image Size
        sizeROI (tuple): Size of ROI

    Returns:
        tuple(int, int, int, int): ROI coordinates, defined as (x, y, w, h)
        x: x coordinates of top left corner
        y: y corrdinates of top left corner
        w: width of the ROI
        h: height of the ROI
    """
    roi = np.zeros(4)

    roi[0] = pt[0] - sizeROI[0] / 2
    if roi[0] < 0:
        roi[0] = 0

    roi[1] = pt[1] - sizeROI[1] / 2
    if roi[1] < 0:
        roi[1] = 0

    roi[2] = sizeROI[0]
    if roi[2] > sizeImg[0]:
        roi[2] = sizeImg[0]

    roi[3] = sizeROI[1]
    if roi[3] > sizeImg[1]:
        roi[3] = sizeImg[1]

    return roi.astype(np.int64)


def coord_xform_img_to_roi(pt: tuple, roi: tuple):
    """Coordinate Transformation form image frame to ROI frame.

    Args:
        pt (tuple): point of interest
        roi (tuple): tuple defining ROI (x, y, w, h)

    Returns:
        (int, int): coordinates of pt in ROI frame
    """
    corner_x, corner_y, lh, lw = roi
    px, py = pt
    return (int(px - corner_x), int(py - corner_y))


def coord_xform_roi_to_img(pt: tuple, roi: tuple):
    """Coordinate Transformation form ROI frame to image frame.

    Args:
        pt (tuple): point of interest
        roi (tuple): tuple defining ROI (x, y, w, h)

    Returns:
        (int, int): coordinates of pt in frmae frame
    """
    corner_x, corner_y, lh, lw = roi
    px, py = pt
    return (int(px + corner_x), int(py + corner_y))


class Detector:
    def __init__(self) -> None:
        # default parameters for Hough Transformations
        self.min = 10
        self.max = 20
        self.param2 = 25
        self.min_dist = 10
        self.hough_line_threshold = 10
        self.circles = np.array([])

    def read_file(self, file_name: str):
        """Read image from a file.

        Args:
            file_name (string): path to the file to be read.
        """
        self.file = file_name
        self.img = cv2.imread(self.file)
        self.width = int(np.shape(self.img)[0] / 2)
        self.height = int(np.shape(self.img)[1] / 2)
        self.detected = False

    def set_image(self, img: np.array):
        """Set image to be detected

        Args:
            img (array): image array
        """
        self.img = img
        self.width = int(np.shape(self.img)[0] / 2)
        self.height = int(np.shape(self.img)[1] / 2)
        self.detected = False

    def set_radii_range(self, min: int, max: int):
        """Set radius range of hough circle transformation.

        Args:
            min (int): mininum radius to be detected, in pixel.
            max (int): maximum radius to be detected, in pixel.
        """
        self.min = min
        self.max = max

    def set_param2_kpt(self, p: float):
        """Set parameter 2 for hough circle transformation.

        Args:
            p (float):  param2 in hough circle transformation
                        It is the accumulator threshold for the circle centers at the detection stage.
                        The smaller it is, the more false circles may be detected.
        """
        self.param2 = p

    def set_min_dist(self, d: float):
        """Set minimum distance for hough circle transformation.

        Args:
            d (float): minimum distance between the centers of the detected circles
        """
        self.min_dist = d

    def set_hough_line_threshold(self, th: int):
        """Set threshold for hough line transformation.

        Args:
            th (int): Accumulator threshold parameter. Only those lines are returned that get enough votes
        """
        self.hough_line_threshold = th

    def detect_kpt(self, num: int):
        """Detect markers using Hough Transformation

        Args:
            num (int): number of the markers desired

        Returns:
            cv2.Mat, int: Image with detected features, number of the point detected
        """
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        imageSize = np.shape(self.img)
        gray_blured = cv2.GaussianBlur(gray, (7, 7), 1.2)

        # First step, HoughCircle Detection to find the location of the marker

        # If there are detected circles saved previously, using previously detected circle to define a smaller ROI
        # Do the circle detection within the ROI to speed up detection
        # If there are no circles saved, do the circle detection on the full image

        region = 4
        if self.circles.size > 3:
            x_list = self.circles[:, :, 0][0]
            y_list = self.circles[:, :, 1][0]
            r_list = self.circles[:, :, 2][0]
            updated_x_list = []
            updated_y_list = []
            updated_r_list = []
            for i in range(len(x_list)):
                roi = get_ROI_coordinates(
                    (x_list[i], y_list[i]),
                    imageSize,
                    (region * r_list[i], region * r_list[i]),
                )
                local_gray_blured = gray_blured[
                    int(roi[1]) : int(roi[1] + roi[3]),
                    int(roi[0]) : int(roi[0] + roi[2]),
                ]
                local_circles = cv2.HoughCircles(
                    local_gray_blured,
                    cv2.HOUGH_GRADIENT,
                    1,
                    self.min_dist,
                    param1=50,
                    param2=self.param2,
                    minRadius=self.min,
                    maxRadius=self.max,
                )
                if local_circles is not None:
                    for local_circle in local_circles[0, :]:
                        cx, cy = coord_xform_roi_to_img(
                            (local_circle[0], local_circle[1]), roi
                        )
                        updated_x_list.append(cx)
                        updated_y_list.append(cy)
                        updated_r_list.append(local_circle[2])

            circles = np.array(
                [np.stack([updated_x_list, updated_y_list, updated_r_list]).T]
            )
            self.circles = circles

            if self.circles.size / 3 != num:
                self.circles = np.array([])
                return self.img, 0

        else:
            circles = cv2.HoughCircles(
                gray_blured,
                cv2.HOUGH_GRADIENT,
                1,
                self.min_dist,
                param1=50,
                param2=self.param2,
                minRadius=self.min,
                maxRadius=self.max,
            )
            self.circles = np.array(circles)

        # Convert the detection results to interger array
        try:
            circles = np.uint16(np.around(self.circles))
        except TypeError:
            # print("No circle detected")
            return self.img, 0

        # print(circles)
        self.center_x_list = []
        self.center_y_list = []

        # Second step, using the HoughLine to find the intersection point within the circle

        # Construct ROI list along with images, HoughLine will be performed on these smaller ROI
        img_shape = np.shape(self.img)
        roi_imgs = []
        for circle in circles[0, :]:
            # print(f"one circle : {circle}")
            cx, cy, rad = circle
            dia = 2 * rad
            cv2.circle(self.img, (cx, cy), rad, (255, 0, 0), 1)
            roi = get_ROI_coordinates(
                (cx, cy), img_shape, (1.1 * dia, 1.1 * dia)
            )
            corner_x, corner_y, lh, lw = roi
            cropped_img = gray_blured[
                corner_y : corner_y + lw, corner_x : corner_x + lh
            ]
            roi_imgs.append([roi, cropped_img])

        roi_imgs = [x for x in roi_imgs if len(x[0])]

        def get_center_from_ROI(roi_img):
            """Get center of the marker using Hough Transformation.
                Hough transformation will be performed on a ring-area in the ROI

            Args:
                roi_img ([(x, y, w, h), cv2.Mat]): ROI and corresponding image array

            Returns:
                list: detected center of the markers
            """
            roi, img = roi_img
            corner_x, corner_y, lh, lw = roi
            center_approx = (int(lw / 2), int(lh / 2))
            rad_approx = min(lw, lh) / (2 + 1.1)
            # Taken the ring-area from images
            outer_mask = np.zeros_like(img)
            outer_mask = cv2.circle(
                outer_mask,
                center_approx,
                int(0.9 * rad_approx),
                (255, 255, 255),
                -1,
            )
            result = img & outer_mask
            # otsu thresholding to make edges more clear
            # ret2,result = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            cdst = cv2.Canny(result, 50, 100, L2gradient=True)  # , None, 3)
            outer_mask = np.zeros_like(img)
            outer_mask = cv2.circle(
                outer_mask,
                center_approx,
                int(0.8 * rad_approx),
                (255, 255, 255),
                -1,
            )
            outer_mask = cv2.circle(
                outer_mask, center_approx, int(0.2 * rad_approx), (0, 0, 0), -1
            )
            cdst = cdst & outer_mask

            lines = cv2.HoughLines(
                cdst,
                rho=1,
                theta=1 * np.pi / 180,
                threshold=self.hough_line_threshold,
            )
            # lines = cv2.HoughLinesP(cdst, rho = 1, theta = 1 * np.pi / 180, threshold = 5, minLineLength = 3, maxLineGap=1)

            # Find the point which has the closest to all the detected line
            # https://math.stackexchange.com/questions/36398/point-closest-to-a-set-four-of-lines-in-3d/55286#55286
            A = np.zeros((2, 2))
            b = np.zeros(2)

            if lines is not None:
                for line in lines:
                    # get line parameters if HoughLines is used :
                    # line parameters : rho, theta (polar coordinates system)
                    rho = line[0][0]
                    theta = line[0][1]
                    a_line = math.cos(theta)
                    b_line = math.sin(theta)
                    x0 = a_line * rho
                    y0 = b_line * rho
                    pt1 = np.array([x0 + 10 * (-b_line), y0 + 10 * (a_line)])
                    pt2 = np.array([x0 - 10 * (-b_line), y0 - 10 * (a_line)])
                    # Draw the line on the image
                    # pt1_w = coord_xform_roi_to_img([pt1[0], pt1[1]], roi)
                    # pt2_w = coord_xform_roi_to_img([pt2[0], pt2[1]], roi)
                    # cv2.line(self.img, pt1_w, pt2_w, (0,255,0), 1, cv2.LINE_AA)

                    # get line parameters if HoughLinesP is used :
                    # line parameters : (x0, y0, x1, y1) coodinates of two points on the line
                    # x0, y0, x1, y1 = line[0]
                    # pt1 = np.array([x0, y0])
                    # pt2 = np.array([x1, y1])
                    # pt1_w = coord_xform_roi_to_img([x0, y0], roi)
                    # pt2_w = coord_xform_roi_to_img([x1, y1], roi)
                    # cv2.line(self.img, pt1_w, pt2_w, (0,255,0), 1, cv2.LINE_AA)

                    line_len = np.linalg.norm(pt2 - pt1)
                    if line_len < 1e-3:  # make sure the line is valid
                        print(
                            f"Line len: {line_len}\t pt1: {pt1}\t pt2: {pt2}"
                        )
                        print(f"Line: {line}")
                        continue
                    ui = ((pt2 - pt1) / line_len).T
                    uiuiT = np.array(
                        [
                            [ui[0] ** 2, ui[0] * ui[1]],
                            [ui[0] * ui[1], ui[1] ** 2],
                        ]
                    )

                    I_minus_uiuiT = np.identity(2) - uiuiT
                    A += I_minus_uiuiT
                    b += I_minus_uiuiT @ pt2

                res = np.linalg.pinv(A) @ b
                # if the line intersection is too far from the center,
                # center of the detected circle will be used
                # this usually means line on one direction is detected
                # try tune the parameters, e.g. threshold in HoughLines
                if np.linalg.norm(res - center_approx) > 0.8 * rad_approx:
                    center_x, center_y = coord_xform_roi_to_img(
                        center_approx, roi
                    )
                    # print("Estimated center is too far from center of the detected circle")
                else:
                    center_x, center_y = coord_xform_roi_to_img(res, roi)

            else:
                print("No line detected")
                center_x, center_y = coord_xform_roi_to_img(center_approx, roi)

            return center_x, center_y

        results = []
        for roi_img in roi_imgs:
            results.append(get_center_from_ROI(roi_img))

        for res in results:
            cv2.circle(
                self.img, (int(res[0]), int(res[1])), 3, (0, 0, 255), -1
            )
        results = np.array(results).T

        self.center_x_list = results[0, :]
        self.center_y_list = results[1, :]

        self.detected = True

        length = len(self.center_x_list)

        return self.img, length

    def get_center_x_list(self):
        return self.center_x_list

    def get_center_y_list(self):
        return self.center_y_list
