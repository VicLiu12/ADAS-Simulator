import cv2
import numpy as np
import socket
import json
import os
import math

UDP_IP = "127.0.0.1"
UNP_PORT = 5052

Marker_Pixels = 150
Marker_Real_Size = 0.1
Poxel_To_Meter = Marker_Real_Size / Marker_Pixels

BEV_Width, BEV_Height = 400, 500


