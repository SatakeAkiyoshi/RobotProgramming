#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
from itertools import product
import numpy as np

wbunbo = 4
hbunbo = wbunbo


def cldic(ldic):
    c = False
    for l in ldic:
        if ldic[l] in ldic:
            ldic[l] = ldic[ldic[l]]
            c = True

    if c:
        ldic = cldic(ldic)
    return ldic


def renseiri(data, h, w):
    c = False
    ldic = {}  # reference
    for x, y in product(range(1, h-1), range(1, w-1)):
        if data[x, y, 1] > 0:
            for a, b in zip([-1, 0, 0, 1], [0, -1, 1, 0]):
                if data[x, y, 1] > data[x+a, y+b, 1] > 0 \
                        and (not data[x, y, 1] in ldic or
                             ldic[data[x, y, 1]] > data[x+a, y+b, 1]):
                    ldic[data[x, y, 1]] = data[x+a, y+b, 1]
                    c = True

    if c:
        ldic = cldic(ldic)
        for x, y in product(range(h), range(w)):
            if data[x, y, 1] in ldic:
                data[x, y, 1] = ldic[data[x, y, 1]]
        data = renseiri(data, h, w)
    return data


def anaume(data, n, h, w, countl):
    c = False
    for x, y in product(range(1, h-1), range(1, w-1)):
        if data[x, y, 1] == 0:
            for a, b in zip([-1, 0, 0, 1], [0, -1, 1, 0]):
                if data[x+a, y+b, 1] > 0 and \
                        countl[int(data[x+a, y+b, 1])-1][2] == n:
                    data[x, y, 1] = data[x+a, y+b, 1]
                    c = True
                    break

    if c:
        data = anaume(data, n, h, w, countl)
    return data


def segment(img):
    org_img = img

    width, height = org_img.size
    wrange = width//wbunbo  # resize
    hrange = height//hbunbo
    recw = wrange//22  # rectangle
    rech = hrange//64

    org_img = org_img.resize((wrange, hrange))
    org = np.array(org_img, dtype=np.float32)
    label = np.zeros([hrange, wrange, 2])
    for h, w in product(range(hrange), range(wrange)):
        if np.sum(org[h, w]) < 735:  # gasochi hantei
            label[h, w, 0] = 1

    # ryouiki no sitei
    renid = 1  # renketu ID
    for h, w in product(range(hrange-rech), range(wrange-recw)):
        if label[h, w, 0] == 1:
            if label[h, w, 1] == 0:
                label[h, w, 1] = renid
                renid += 1
            hr = 0
            wr = 0
            # hani kime
            for hi, wi in product(range(1, rech), (1, recw)):
                if label[h+hi, w+wi, 0] == 1:
                    if hi > hr:
                        hr = hi
                    if wi > wr:
                        wr = wi
            # hani wo label tuke
            for hi, wi in product(range(hr+1), range(wr+1)):
                if label[h+hi, w+wi, 1] == 0\
                        or label[h+hi, w+wi, 1] > label[h, w, 1]:
                    label[h+hi, w+wi, 1] = label[h, w, 1]

    # haikei wo label tuke
    stack = set()
    stack.add((0, 0))
    while stack:
        sp = stack.pop()  # search point
        for i, j in zip([-1, 0, 0, 1], [0, -1, 1, 0]):
            if hrange > sp[0]+i >= 0 and wrange > sp[1]+j >= 0\
                    and label[sp[0]+i, sp[1]+j, 1] == 0\
                    and (sp[0]+i, sp[1]+j) not in stack:
                stack.add((sp[0]+i, sp[1]+j))
        label[sp][1] = -1

    # renketu seibun wo tougou
    label = renseiri(label, hrange, wrange)

    # renketu ID wo seiri
    renids = set()
    for h, w in product(range(hrange), range(wrange)):
        if label[h, w, 1] > -1:
            renids.add(label[h, w, 1])

    lmax = int
    for i, j in zip(renids, range(len(renids))):
        for h, w in product(range(hrange), range(wrange)):
            if label[h, w, 1] == i:
                label[h, w, 1] = j
        lmax = j

    # moji ka zu no hantei
    # len(counts) == len(renids) - 1 (id 0 ga nai)
    counts = [[0, 0, 0] for i in range(lmax)]
    for h, w in product(range(hrange), range(wrange)):
        if label[h, w, 1] > 0:
            counts[int(label[h, w, 1]) - 1][0] += 1
            if label[h, w, 0] == 1:
                counts[int(label[h, w, 1]) - 1][1] += 1

    for count in counts:
        if count[1] / count[0] > 0.54:
            count[2] = 1

    for h, w in product(range(hrange), range(wrange)):
        if label[h, w, 1] > 0 and counts[int(label[h, w, 1])-1][0]\
                < wrange*hrange/1000:
            label[h, w, 1] = 0

    # ana wo label tuke
    hoge = 0
    huga = 0
    for h, w in product(range(hrange), range(wrange)):
        if label[h, w, 1] == 0:
            hoge += 1
        if label[h, w, 1] == -1:
            huga += 1

    for mojiorzu in [1, 0]:
        label = anaume(label, mojiorzu, hrange, wrange, counts)

    # syuturyoku gazou no iro tuke
    dst = np.empty([hrange, wrange, 3])
    dst.flags.writeable = True
    for h, w in product(range(hrange), range(wrange)):
        if label[h, w, 1] == 0:
            dst[h, w, :] = 0
        elif label[h, w, 1] == -1:
            dst[h, w, :] = 0
        else:
            if counts[int(label[h, w, 1])-1][2] == 0:
                dst[h, w, :] = 255
            else:
                dst[h, w, :] = 127

    dst = np.array(dst.clip(0, 255), dtype=np.uint8)
    dst_img = Image.fromarray(dst)
    dst_img = dst_img.resize((width, height))
    return dst_img
