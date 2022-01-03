import numpy as np
import json
import colour_demosaicing

def LoadRaw(FN):
    """
    DEPRECATED!
    load and unpack RAW image

    :params FN: file name
    """
    data = np.load(FN)
    shape = data.shape
    if shape == (1944, 3240):
        CameraType = 1
    elif shape == (2464, 4100):
        CameraType = 2
    elif shape == (3040, 6084):
        CameraType = 3
    else:
        raise ValueError("unknown raw data")
    if CameraType in [1, 2]:
        # Horizontally, each row consists of 10-bit values. Every four bytes are
        # the high 8-bits of four values, and the 5th byte contains the packed low
        # 2-bits of the preceding four values. In other words, the bits of the
        # values A, B, C, D and arranged like so:
        #
        #  byte 1   byte 2   byte 3   byte 4   byte 5
        # AAAAAAAA BBBBBBBB CCCCCCCC DDDDDDDD AABBCCDD
        #
        # Here, we convert our data into a 16-bit array, shift all values left by
        # 2-bits and unpack the low-order bits from every 5th byte in each row,
        # then remove the columns containing the packed bits
        data = data.astype(np.uint16) << 2
        for byte in range(4):
            data[:, byte::5] |= ((data[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
        data = np.delete(data, np.s_[4::5], 1)
    else:
        # HQ camera
        data = data.astype(np.uint16)
        UD = np.zeros((shape[0], shape[1] // 3 * 2), dtype=np.uint16)
        UD[:, ::2] = (data[:, ::3] << 4) + (data[:, 2::3] & 0x0F)
        UD[:, 1::2] = (data[:, 1::3] << 4) + ((data[:, 2::3] >> 4) & 0x0F)
        data = UD
    return data


def LoadInfo(FN):
    with open(FN, "r") as fh:
        infos = json.load(fh)
    return infos


def SplitBayerChannels(data):
    """
    split BGGR raw image in single channels

    :params data: raw data
    """
    if data.shape == (1944, 2592):
        # version 1 camera has data of shape (1944, 2592) and GBRG pattern
        r  = data[1::2, 0::2]  # Red
        g0 = data[0::2, 0::2]  # Green
        g1 = data[1::2, 1::2]  # Green
        b  = data[0::2, 1::2]  # Blue
    elif data.shape == (3040, 4056):
        # HQ camera has data of shape (3040, 4056) and BGGR pattern
        r  = data[1::2, 1::2]  # Red
        g0 = data[0::2, 1::2]  # Green
        g1 = data[1::2, 0::2]  # Green
        b  = data[0::2, 0::2]  # Blue
    else:
        raise ValueError("unknown data shape")
    return {"r": r, "g0": g0, "g1": g1, "b" :b}


def RoundToSignificantDigits(f, n_d=3):
    if f > 0:
        factor = 10 ** -(np.floor(np.log10(f)) - (n_d-1))
        return np.round(f * factor) / factor
    else:
        return f


def PostProcess(
    Raw, Bits=10,
    Black=0.0, Flat=1.0,
    Pattern=u"GBRG", Debayer="bilinear",
    RGB_gains=(1.5,1.0,1.5),
    OutOffset = 0.0,
    OutGain = 1.0
):
    """
    process RAW image
    Version 1 camera has GBRG pattern, HQ camera is BGGR
    """
    # Black and Flat correction
    Img = (Raw - Black) * (np.mean(Flat) / Flat)
    # normalize scaling
    Img = Img / float(2 ** Bits)
    # debayer
    if Debayer=="bilinear":
        Img = colour_demosaicing.demosaicing_CFA_Bayer_bilinear(Img, pattern=Pattern)
    elif Debayer=="Malvar2004":
        Img = colour_demosaicing.demosaicing_CFA_Bayer_Malvar2004(Img, pattern=Pattern)
    elif Debayer=="Menon2007":
        Img = colour_demosaicing.demosaicing_CFA_Bayer_Menon2007(Img, pattern=Pattern)
    elif Debayer=="DDFAPD":
        Img = colour_demosaicing.demosaicing_CFA_Bayer_DDFAPD(Img, pattern=Pattern)
    else:
        # from picamera example
        rgb = np.zeros(Img.shape + (3,), dtype=Img.dtype)
        rgb[1::2, 0::2, 0] = Img[1::2, 0::2] # Red
        rgb[0::2, 0::2, 1] = Img[0::2, 0::2] # Green
        rgb[1::2, 1::2, 1] = Img[1::2, 1::2] # Green
        rgb[0::2, 1::2, 2] = Img[0::2, 1::2] # Blue
        # Below we present a fairly naive de-mosaic method that simply
        # calculates the weighted average of a pixel based on the pixels
        # surrounding it. The weighting is provided by a byte representation of
        # the Bayer filter which we construct first:
        bayer = np.zeros(rgb.shape, dtype=np.uint8)
        bayer[1::2, 0::2, 0] = 1 # Red
        bayer[0::2, 0::2, 1] = 1 # Green
        bayer[1::2, 1::2, 1] = 1 # Green
        bayer[0::2, 1::2, 2] = 1 # Blue
        # Allocate an array to hold our output with the same shape as the input
        # data. After this we define the size of window that will be used to
        # calculate each weighted average (3x3). Then we pad out the rgb and
        # bayer arrays, adding blank pixels at their edges to compensate for the
        # size of the window when calculating averages for edge pixels.
        output = np.empty(rgb.shape, dtype=rgb.dtype)
        window = (3, 3)
        borders = (window[0] - 1, window[1] - 1)
        border = (borders[0] // 2, borders[1] // 2)
        rgb = np.pad(rgb, [
            (border[0], border[0]),
            (border[1], border[1]),
            (0, 0),
            ], 'constant')
        bayer = np.pad(bayer, [
            (border[0], border[0]),
            (border[1], border[1]),
            (0, 0),
            ], 'constant')
        # For each plane in the RGB data, we use a nifty numpy trick
        # (as_strided) to construct a view over the plane of 3x3 matrices. We do
        # the same for the bayer array, then use Einstein summation on each
        # (np.sum is simpler, but copies the data so it's slower), and divide
        # the results to get our weighted average:
        for plane in range(3):
            p = rgb[..., plane]
            b = bayer[..., plane]
            pview = np.lib.stride_tricks.as_strided(p, shape=(
                p.shape[0] - borders[0],
                p.shape[1] - borders[1]) + window, strides=p.strides * 2)
            bview = np.lib.stride_tricks.as_strided(b, shape=(
                b.shape[0] - borders[0],
                b.shape[1] - borders[1]) + window, strides=b.strides * 2)
            psum = np.einsum('ijkl->ij', pview)
            bsum = np.einsum('ijkl->ij', bview)
            output[..., plane] = psum // bsum
        Img = output
    # white balance
    Img[:,:,0] *= RGB_gains[0]
    Img[:,:,1] *= RGB_gains[1]
    Img[:,:,2] *= RGB_gains[2]
    # output rescaling
    Img = (Img - OutOffset) * OutGain
    # finish
    return Img


def ExtractRawFromJpgData(JpgData, CameraType = 3):
    frame_len = len(JpgData)
    offset = {
        1: 6404096,
        2: 10270208,
        3: 18711040,
    }[CameraType]
    preview_len = frame_len - offset
    JpgData = JpgData[preview_len:]
    assert JpgData[:4] == bytes('BRCM', encoding="latin2")
    JpgData = JpgData[32768:]
    RawData = np.frombuffer(JpgData, dtype=np.uint8)
    reshape, crop = {
        1: ((1952, 3264), (1944, 3240)),
        2: ((2480, 4128), (2464, 4100)),
        3: ((3040 + 16, 6084 + 28), (3040, 6084)),
    }[CameraType]
    data = RawData.reshape(reshape)[:crop[0], :crop[1]]
    #
    if CameraType in [1, 2]:
        # Horizontally, each row consists of 10-bit values. Every four bytes are
        # the high 8-bits of four values, and the 5th byte contains the packed low
        # 2-bits of the preceding four values. In other words, the bits of the
        # values A, B, C, D and arranged like so:
        #
        #  byte 1   byte 2   byte 3   byte 4   byte 5
        # AAAAAAAA BBBBBBBB CCCCCCCC DDDDDDDD AABBCCDD
        #
        # Here, we convert our data into a 16-bit array, shift all values left by
        # 2-bits and unpack the low-order bits from every 5th byte in each row,
        # then remove the columns containing the packed bits
        data = data.astype(np.uint16) << 2
        for byte in range(4):
            data[:, byte::5] |= ((data[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
        data = np.delete(data, np.s_[4::5], 1)
    else:
        # HQ camera
        data = data.astype(np.uint16)
        shape = data.shape
        UD = np.zeros((shape[0], shape[1] // 3 * 2), dtype=np.uint16)
        if True:
            UD[:, ::2] = (data[:, ::3] << 4) + (data[:, 2::3] & 0x0F)
            UD[:, 1::2] = (data[:, 1::3] << 4) + ((data[:, 2::3] >> 4) & 0x0F)
            data = UD
        elif False:
            UD[:, 1::2] = (data[:, 1::3] << 4) + (data[:, 2::3] & 0x0F)
            UD[:, ::2] = (data[:, ::3] << 4) + ((data[:, 2::3] >> 4) & 0x0F)
            data = UD
        else:
            data[:, 0::3] = data[:, 0::3] << 4
            data[:, 0::3] |= ((data[:, 1::3] >> 4) & 0x0f)
            data[:, 1::3] = data[:, 1::3] << 4
            data[:, 1::3] |= (data[:, 1::3] & 0x0f)
            data = np.delete(data, np.s_[2::3], 1)
    return data


def LoadRawJpg(FN, CameraType=3):
    """
    load and unpack RAW JPG image

    :params FN: file name
    """
    with open(FN, "rb") as fh:
        JpgData = fh.read()
    Raw = ExtractRawFromJpgData(JpgData=JpgData, CameraType=CameraType)
    return Raw
