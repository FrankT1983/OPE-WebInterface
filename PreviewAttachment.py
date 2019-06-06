#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse

from OPP.classes import LogWriter


def preview_file(fileId, conn):
    name, data = GetAnnotationFileFromServer(conn,fileId)

    if (name.endswith(".txt")):
        return RenderTextAndWranInResult(data)
    if (name.endswith(".csv")):
        return TabelToDjangoRequest(CsvStringToArray(data))
    else:
        response = HttpResponse(content_type="image/png")
        response.content = data
        return response

    return user, password


import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import django
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageDraw, ImageFont

def CsvStringToArray(csvString):
    lines = str.split(str(csvString), "\n")
    result = []
    maxlen=0
    for i in range(len(lines)):
        col = lines[i].split(",")
        result.append(col)
        maxlen = max(maxlen, len(col))

    # bring to one sice
    for i in range(len(result)):
        line = result[i]
        while len(line) < maxlen:
            line.append("")

    return result

def TabelToDjangoRequest(clust_data):
    nrows, ncols = len(clust_data) + 1, len(clust_data[0])
    hcell, wcell = 0.17, 0.7        # in inch?
    hpad, wpad = 0, 0

    my_dpi = 300

    maxSizeInInch = 32767 /my_dpi

    figWidth = ncols * wcell + wpad
    figWidth = min(figWidth,maxSizeInInch)

    figHeight = nrows * hcell + hpad
    figHeight = min(figHeight, maxSizeInInch)

    fig = plt.figure(figsize=(figWidth, figHeight), dpi=my_dpi)
    ax = fig.add_subplot(111)
    ax.axis('off')
    # do the table
    the_table = ax.table(cellText=clust_data,
                         loc='center')

    canvas = FigureCanvas(fig)

    response = django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def RenderTextAndWranInResult(text):
    response = HttpResponse(content_type="image/png")
    # txt = "preview for " + str(runId) + str(blockId) + str(portId) + str(datasetId)
    image = Image.new("RGBA", (900, 150), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    fontPath = "OPP/static/font/Unique.ttf"
    if not os.path.exists(fontPath) :
        fontPath = "static/font/Unique.ttf"

    if not os.path.exists(fontPath):
        LogWriter.logError("can't find font " +  fontPath + " in " + os.path.dirname(__file__))

    font = ImageFont.truetype(fontPath, 100)

    draw.text((10, 0), text, (0, 0, 0), font=font)
    image.save(response, "PNG")
    return response


def GetAnnotationFileFromServer(connection, fileId):
    data = None
    name = ""
    try:
        ann = connection.getObject("FileAnnotation", fileId)
        name = ann.getFileName()
        for chunk in ann.getFileInChunks():
            if data is None:
                data = chunk
            else:
                data += chunk
    except:
        data=None

    return name, data

