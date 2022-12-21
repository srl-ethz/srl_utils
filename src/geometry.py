"""Utilities that involves geometry calculation."""

import cv2
import numpy as np


def camera_unproject_pixel_to_world(
    points2d: np.array,
    z_depth: np.array,
    camera_intrinsic_matrix: np.array,
    distortion_coefficients: np.array,
):  # pylint: disable=invalid-name
    # Justification:
    # the variable names here are a proper representation in mathematical expressions
    """Unproject 2d points in pixel coordinates to 3d points in camera frame with known depth z.

    source:
    https://stackoverflow.com/questions/51272055/opencv-unproject-2d-points-to-3d-with-known-depth-z

    Args:
        points2d (array(N*2)): array of 2d points in pixel coordinates
        Z (array(1,) or array(N,)): known depth of the object plane
        camera_intrinsic_matrix (array(3*3)): camera intrinsic matrix
        distortion (array(5,)): distortion coefficients
    Returns:
        array(N*3): array of 3d points in camera frame
    """
    # f_x,  f_y: the pixel focal length
    # c_x,  c_y: offsets of the principal point from the top-left corner of the image frame
    f_x = camera_intrinsic_matrix[0, 0]
    f_y = camera_intrinsic_matrix[1, 1]
    c_x = camera_intrinsic_matrix[0, 2]
    c_y = camera_intrinsic_matrix[1, 2]
    # Step 1. Undistort.
    points_undistorted = np.array([])
    if len(points2d) > 0:
        points_undistorted = cv2.undistortPoints(
            np.expand_dims(points2d, axis=1).astype(np.float64),
            camera_intrinsic_matrix,
            distortion_coefficients,
            P=camera_intrinsic_matrix,
        )
    points_undistorted = np.squeeze(points_undistorted, axis=1)

    # Step 2. Reproject.
    result = np.array([])
    for idx in range(points_undistorted.shape[0]):
        z = z_depth[0] if len(z_depth) == 1 else z_depth[idx]
        x = (points_undistorted[idx, 0] - c_x) / f_x * z
        y = (points_undistorted[idx, 1] - c_y) / f_y * z
        result = np.append(result, [x, y, z])
    return result


def camera_project_3d_to_pixel(point_3d: np.array, intrinsics: np.array):
    """Project a 3d point in camera frame to pixel coordinates using camera intrinsics.

    Args:
        point_3d (array(N*3)): array of 3d points in camera frame
        intrinsics (array(3*3)): Camera intrinsic matrix

    Returns:
        array(N*2): array of 2d pixel coordinates
    """
    point_2d = intrinsics @ point_3d
    point_2d /= point_2d[2]
    return point_2d[:2]


def project_points_to_plane(
    points3d: np.array, center: np.array, S: np.array
):  # pylint: disable=invalid-name too-many-locals
    # Justification:
    # the variable name here are a proper representation in mathematical expressions
    # Extra local variable to be consistent with the mathematical expressions
    """Use pinhole projection model to project a point to plane S.

    Reprojected point can be defined as the intersection point between the line L and surface S,
    where L is defined by the point of interest and optical center.
    For a line L : (x, y, z) = (x0, y0, z0) + p (l, m, n),
                    where (x0, y0, z0) are a reference point,
                          ( l,  m,  n) are directional vector,
                    p is a parameter
    And a surface a*x + b*y + c*z + d = 0,
                    where a, b, c, d are the parameters

    Intersection point is when p satisfies following condition:
            a*x0 + b*y0 + c*z0 + d
    p = -----------------------------
              a*l + b*m + c*n

    Args:
        points3d (array(N*3)): 3d coordinates of the point to project
        center (array(1*3)): optical center of the pinhole projection model
        S (array(4,1)): surface to be projected [a,b,c,d],
                        where surface equation is a*x + b*y + c*z + d = 0

    Returns:
        array(N*3): 3d coordinates of the projected points on surface S
    """
    result = np.array([])
    x0, y0, z0 = center
    a, b, c, d = S
    # directional vector of the line vec = (l, m, n)
    l, m, n = points3d - center
    p = -(a * x0 + b * y0 + c * z0 + d) / (a * l + b * m + c * n)
    x = x0 + p * l
    y = y0 + p * m
    z = z0 + p * n

    result = np.array([x, y, z])

    return result


# https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def normalize(vector: np.array):
    """Return the unit vector of the vector."""
    norm=np.linalg.norm(vector)
    if norm==0:  # use eps to avoid zero division
        norm=np.finfo(vector.dtype).eps
    return vector / norm


def angle_between(vector1: np.array, vector2: np.array):
    """Return the angle in radians between vectors 'v1' and 'v2'.

    Examples:
        >>> angle_between((1, 0, 0), (0, 1, 0))
        1.5707963267948966
        >>> angle_between((1, 0, 0), (1, 0, 0))
        0.0
        >>> angle_between((1, 0, 0), (-1, 0, 0))
        3.141592653589793
    Args:
        v1(array(N*1)): n-dimensional vector 1
        v1(array(N*1)): n-dimensional vector 2

    Returns:
        float: angle between two vectors in radians
    """
    vector1_u = normalize(vector1)
    vector2_u = normalize(vector2)
    return np.arccos(np.clip(np.dot(vector1_u, vector2_u), -1.0, 1.0))


def quaternion_distance(quat1: np.array, quat2: np.array):
    """Return the angular distance between two quaternions q1 and q2.

    source: https://math.stackexchange.com/a/90098

    Args:
        q1 (array(4*1)): quaternion 1, (x, y, z, w)
        q2 (array(4*1)): quaternion 2, (x, y, z, w)

    Returns:
        float: angular distance between q1 and q2 in radians
    """
    quat1_dot_quat2 = np.dot(quat1, quat2)
    # angular distance
    return np.arccos(2 * np.power(quat1_dot_quat2, 2) - 1)
