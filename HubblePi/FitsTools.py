import time
from .Toolbox import RoundToSignificantDigits
from astropy.io import fits


def RecodeUnicode(s):
    return s.encode("ascii", "replace").decode("ascii")

def SaveFits(FileName, Img, FileInfo={}):
    FitsHeader = [
        ("SIMPLE", True, "file does conform to FITS standard"),
        ("BITPIX", 16, "number of bits per data pixel"),
        ("NAXIS", 2, "number of data axes"),
        ("NAXIS1", Img.shape[1], "length of data axis 1"),
        ("NAXIS2", Img.shape[0], "length of data axis 2"),
        ("EXTEND", True, "FITS dataset may contain extensions"),
        ("COMMENT", RecodeUnicode(FileInfo.get("comment", ""))),
        ("BZERO", 32768, "offset data range to that of unsigned short"),
        ("BSCALE", 1, "default scaling factor"),
        ("FILENAME", FileName, "Original filename"),
        ("INSTRUME", "HubblePi", "CCD Name"),
        ("OBJECT", RecodeUnicode(FileInfo.get("comment", "")), "Object name"),
        ("EXPTIME", RoundToSignificantDigits(FileInfo.get("ExposureSpeed", 0.0) * 1e-6, n_d=3),
         "Total Exposure Time (s)"),
        # FRAME   = 'Light   '           / Frame Type
        ("XBAYROFF", 0, "X offset of Bayer array"),
        ("YBAYROFF", 0, "Y offset of Bayer array"),
        ("BAYERPAT", {1: "GBRG    ", 3: "BGGR    ", }[FileInfo.get("CameraType", 1)], "Bayer color pattern"),
        ("DATE-OBS", time.strftime("%Y-%m-%dT%H:%M:%S.000", time.gmtime(FileInfo.get("TimeStamp", 0.0))),
         "UTC start date of observation"),
        ("ISOSPEED", FileInfo.get("ISO", 0), "ISO Speed"),
        # more info from HubblePi camera
        ("AnaGain", FileInfo.get("AnalogGain", 0.0), "analog sensor gain"),
        ("CamType", FileInfo.get("CameraType", "unknown"), "camera sensor type"),
        ("ExpMode", FileInfo.get("ExpMode", ""), "exposure mode"),
    ]
    Scaling = {1: 2**(16-10), 3: 2**(16-12)}[FileInfo.get("CameraType", 1)]
    hdu = fits.PrimaryHDU(Img * Scaling)
    for FHdr in FitsHeader:
        if len(FHdr) > 2:
            hdu.header[FHdr[0]] = (FHdr[1], FHdr[2])
        else:
            hdu.header[FHdr[0]] = FHdr[1]
    hdul = fits.HDUList([hdu])
    hdul.writeto(FileName, overwrite=True)
