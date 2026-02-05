from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import numpy as np
from astropy.io import fits
from astropy.time import Time
import astropy.units as u




    ## load observing MJD
astropy_time = Time("2024-02-04T06:06:25.539", format="isot", scale="utc")
    ## load observatory

aaaa=EarthLocation.get_site_names()
#print(aaaa)

loc = EarthLocation.of_site('Gemini South')
    ## load coordinates
sc = SkyCoord(ra=117.30085246178 * u.deg, dec=-76.70272278517 * u.deg)


#et_site_names
    ## compute barrybarycentric correction
bary_out = sc.radial_velocity_correction(obstime=astropy_time, location=loc).value


print("Barycentric correction (m/s): ", bary_out)




