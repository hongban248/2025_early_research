import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup



html_content="""
<tr><td>HD 213893</td> <td>  </td> <td>M0 IIIb</td> <td></td>  <td> 0.81-5.07 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M0IIIb_HD213893.fits"> FITS </a></td><td><a href="../Data/M0IIIb_HD213893.txt"> Text </a></td><td><a href="../Data/M0IIIb_HD213893.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 19305</td> <td>  </td> <td>M0 V</td> <td></td>  <td> 0.81-5.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M0V_HD19305.fits"> FITS </a></td><td><a href="../Data/M0V_HD19305.txt"> Text </a></td><td><a href="../Data/M0V_HD19305.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 236697</td> <td>  </td> <td>M0.5 Ib</td> <td>Lc</td>  <td> 0.81-4.10 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M0.5Ib_HD236697.fits"> FITS </a></td><td><a href="../Data/M0.5Ib_HD236697.txt"> Text </a></td><td><a href="../Data/M0.5Ib_HD236697.png">  PNG </a></td> <td><a href="../Data/M0.5Ib_HD236697_ext.fits"> FITS </a></td><td><a href="../Data/M0.5Ib_HD236697_ext.txt"> Text </a></td><td><a href="../Data/M0.5Ib_HD236697_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 209290</td> <td> Gl 846 </td> <td>M0.5 V</td> <td></td>  <td> 0.81-5.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M0.5V_HD209290.fits"> FITS </a></td><td><a href="../Data/M0.5V_HD209290.txt"> Text </a></td><td><a href="../Data/M0.5V_HD209290.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 339034</td> <td> NR Vul </td> <td>M1 Ia</td> <td>Lc</td>  <td> 0.81-5.02 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1Ia_HD339034.fits"> FITS </a></td><td><a href="../Data/M1Ia_HD339034.txt"> Text </a></td><td><a href="../Data/M1Ia_HD339034.png">  PNG </a></td> <td><a href="../Data/M1Ia_HD339034_ext.fits"> FITS </a></td><td><a href="../Data/M1Ia_HD339034_ext.txt"> Text </a></td><td><a href="../Data/M1Ia_HD339034_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 14404</td> <td> PR Per </td> <td>M1- Iab-Ib</td> <td>Lc</td>  <td> 0.81-4.17 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1-Iab-Ib_HD14404.fits"> FITS </a></td><td><a href="../Data/M1-Iab-Ib_HD14404.txt"> Text </a></td><td><a href="../Data/M1-Iab-Ib_HD14404.png">  PNG </a></td> <td><a href="../Data/M1-Iab-Ib_HD14404_ext.fits"> FITS </a></td><td><a href="../Data/M1-Iab-Ib_HD14404_ext.txt"> Text </a></td><td><a href="../Data/M1-Iab-Ib_HD14404_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>HD 39801</td> <td> Betelgeuse </td> <td>M1-M2 Ia-Iab</td> <td>SRc</td>  <td> 0.81-5.02 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1-M2Ia-Iab_HD39801.fits"> FITS </a></td><td><a href="../Data/M1-M2Ia-Iab_HD39801.txt"> Text </a></td><td><a href="../Data/M1-M2Ia-Iab_HD39801.png">  PNG </a></td> <td><a href="../Data/M1-M2Ia-Iab_HD39801_ext.fits"> FITS </a></td><td><a href="../Data/M1-M2Ia-Iab_HD39801_ext.txt"> Text </a></td><td><a href="../Data/M1-M2Ia-Iab_HD39801_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 204724</td> <td> 2 Peg </td> <td>M1+ III</td> <td>var</td>  <td> 0.80-5.05 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1+III_HD204724.fits"> FITS </a></td><td><a href="../Data/M1+III_HD204724.txt"> Text </a></td><td><a href="../Data/M1+III_HD204724.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 42581</td> <td> Gl 229 A </td> <td>M1 V</td> <td>UV</td>  <td> 0.81-4.91 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1V_HD42581.fits"> FITS </a></td><td><a href="../Data/M1V_HD42581.txt"> Text </a></td><td><a href="../Data/M1V_HD42581.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 35601</td> <td>  </td> <td>M1.5 Iab-Ib</td> <td>Lc</td>  <td> 0.81-4.18 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1.5Iab-Ib_HD35601.fits"> FITS </a></td><td><a href="../Data/M1.5Iab-Ib_HD35601.txt"> Text </a></td><td><a href="../Data/M1.5Iab-Ib_HD35601.png">  PNG </a></td> <td><a href="../Data/M1.5Iab-Ib_HD35601_ext.fits"> FITS </a></td><td><a href="../Data/M1.5Iab-Ib_HD35601_ext.txt"> Text </a></td><td><a href="../Data/M1.5Iab-Ib_HD35601_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>BD +60 265</td> <td>  </td> <td>M1.5 Ib</td> <td></td>  <td> 0.80-5.05 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1.5Ib_BD+60_265.fits"> FITS </a></td><td><a href="../Data/M1.5Ib_BD+60_265.txt"> Text </a></td><td><a href="../Data/M1.5Ib_BD+60_265.png">  PNG </a></td> <td><a href="../Data/M1.5Ib_BD+60_265_ext.fits"> FITS </a></td><td><a href="../Data/M1.5Ib_BD+60_265_ext.txt"> Text </a></td><td><a href="../Data/M1.5Ib_BD+60_265_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 36395</td> <td> Gl 205 </td> <td>M1.5 V</td> <td>BY:</td>  <td> 0.81-5.43 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M1.5V_HD36395.fits"> FITS </a></td><td><a href="../Data/M1.5V_HD36395.txt"> Text </a></td><td><a href="../Data/M1.5V_HD36395.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 206936</td> <td> &mu Cep </td> <td>M2- Ia</td> <td>SRc</td>  <td> 0.80-5.03 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2-Ia_HD206936.fits"> FITS </a></td><td><a href="../Data/M2-Ia_HD206936.txt"> Text </a></td><td><a href="../Data/M2-Ia_HD206936.png">  PNG </a></td> <td><a href="../Data/M2-Ia_HD206936_ext.fits"> FITS </a></td><td><a href="../Data/M2-Ia_HD206936_ext.txt"> Text </a></td><td><a href="../Data/M2-Ia_HD206936_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 10465</td> <td>  </td> <td>M2 Ib</td> <td>Lc</td>  <td> 0.81-5.00 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2Ib_HD10465.fits"> FITS </a></td><td><a href="../Data/M2Ib_HD10465.txt"> Text </a></td><td><a href="../Data/M2Ib_HD10465.png">  PNG </a></td> <td><a href="../Data/M2Ib_HD10465_ext.fits"> FITS </a></td><td><a href="../Data/M2Ib_HD10465_ext.txt"> Text </a></td><td><a href="../Data/M2Ib_HD10465_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>HD 23475</td> <td> BE Cam </td> <td>M2 II</td> <td>Lc</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2II_HD23475.fits"> FITS </a></td><td><a href="../Data/M2II_HD23475.txt"> Text </a></td><td><a href="../Data/M2II_HD23475.png">  PNG </a></td> <td><a href="../Data/M2II_HD23475_ext.fits"> FITS </a></td><td><a href="../Data/M2II_HD23475_ext.txt"> Text </a></td><td><a href="../Data/M2II_HD23475_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 120052</td> <td> 87 Vir </td> <td>M2 III</td> <td>var</td>  <td> 0.81-4.95 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2III_HD120052.fits"> FITS </a></td><td><a href="../Data/M2III_HD120052.txt"> Text </a></td><td><a href="../Data/M2III_HD120052.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 95735</td> <td> Gl 411 </td> <td>M2 V</td> <td>BY:</td>  <td> 0.81-5.40 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2V_HD95735.fits"> FITS </a></td><td><a href="../Data/M2V_HD95735.txt"> Text </a></td><td><a href="../Data/M2V_HD95735.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 806</td> <td>  </td> <td>M2 V</td> <td>var</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2V_Gl806.fits"> FITS </a></td><td><a href="../Data/M2V_Gl806.txt"> Text </a></td><td><a href="../Data/M2V_Gl806.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 219734</td> <td> 8 And </td> <td>M2.5 III Ba0.5</td> <td>var</td>  <td> 0.81-5.00 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2.5IIIBa0.5_HD219734.fits"> FITS </a></td><td><a href="../Data/M2.5IIIBa0.5_HD219734.txt"> Text </a></td><td><a href="../Data/M2.5IIIBa0.5_HD219734.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 381</td> <td>  </td> <td>M2.5 V</td> <td>var</td>  <td> 0.81-4.96 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2.5V_Gl381.fits"> FITS </a></td><td><a href="../Data/M2.5V_Gl381.txt"> Text </a></td><td><a href="../Data/M2.5V_Gl381.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>Gl 581</td> <td> HO Lib </td> <td>M2.5 V</td> <td>BY</td>  <td> 0.81-5.07 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M2.5V_Gl581.fits"> FITS </a></td><td><a href="../Data/M2.5V_Gl581.txt"> Text </a></td><td><a href="../Data/M2.5V_Gl581.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>RW Cyg</td> <td>  </td> <td>M3 to M4 Ia-Iab</td> <td>SRc</td>  <td> 0.81-4.09 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3toM4Ia-Iab_RW_Cyg.fits"> FITS </a></td><td><a href="../Data/M3toM4Ia-Iab_RW_Cyg.txt"> Text </a></td><td><a href="../Data/M3toM4Ia-Iab_RW_Cyg.png">  PNG </a></td> <td><a href="../Data/M3toM4Ia-Iab_RW_Cyg_ext.fits"> FITS </a></td><td><a href="../Data/M3toM4Ia-Iab_RW_Cyg_ext.txt"> Text </a></td><td><a href="../Data/M3toM4Ia-Iab_RW_Cyg_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>CD -31 4916</td> <td>  </td> <td>M3 Iab-Ia</td> <td>Lc</td>  <td> 0.81-4.18 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3Iab-Ia_CD-31_49.fits"> FITS </a></td><td><a href="../Data/M3Iab-Ia_CD-31_49.txt"> Text </a></td><td><a href="../Data/M3Iab-Ia_CD-31_49.png">  PNG </a></td> <td><a href="../Data/M3Iab-Ia_CD-31_49_ext.fits"> FITS </a></td><td><a href="../Data/M3Iab-Ia_CD-31_49_ext.txt"> Text </a></td><td><a href="../Data/M3Iab-Ia_CD-31_49_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 14469</td> <td> SU Per </td> <td>M3-M4 Iab</td> <td>SRc</td>  <td> 0.81-5.00 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3-M4Iab_HD14469.fits"> FITS </a></td><td><a href="../Data/M3-M4Iab_HD14469.txt"> Text </a></td><td><a href="../Data/M3-M4Iab_HD14469.png">  PNG </a></td> <td><a href="../Data/M3-M4Iab_HD14469_ext.fits"> FITS </a></td><td><a href="../Data/M3-M4Iab_HD14469_ext.txt"> Text </a></td><td><a href="../Data/M3-M4Iab_HD14469_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>HD 40239</td> <td> &pi Aur </td> <td>M3 IIb</td> <td>Lc</td>  <td> 0.81-4.91 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3IIb_HD40239.fits"> FITS </a></td><td><a href="../Data/M3IIb_HD40239.txt"> Text </a></td><td><a href="../Data/M3IIb_HD40239.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 39045</td> <td>  </td> <td>M3      III</td> <td>Lb:</td>  <td> 0.81-4.91 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3III_HD39045.fits"> FITS </a></td><td><a href="../Data/M3III_HD39045.txt"> Text </a></td><td><a href="../Data/M3III_HD39045.png">  PNG </a></td> <td><a href="../Data/M3III_HD39045_ext.fits"> FITS </a></td><td><a href="../Data/M3III_HD39045_ext.txt"> Text </a></td><td><a href="../Data/M3III_HD39045_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>Gl 388</td> <td> AD Leo </td> <td>M3 V</td> <td>UV</td>  <td> 0.81-5.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3V_Gl388.fits"> FITS </a></td><td><a href="../Data/M3V_Gl388.txt"> Text </a></td><td><a href="../Data/M3V_Gl388.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 14488</td> <td> RS Per </td> <td>M3.5 Iab Fe-1 var?</td> <td>SRc</td>  <td> 0.80-5.05 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3.5IabFe-1var?_HD14488.fits"> FITS </a></td><td><a href="../Data/M3.5IabFe-1var?_HD14488.txt"> Text </a></td><td><a href="../Data/M3.5IabFe-1var?_HD14488.png">  PNG </a></td> <td><a href="../Data/M3.5IabFe-1var?_HD14488_ext.fits"> FITS </a></td><td><a href="../Data/M3.5IabFe-1var?_HD14488_ext.txt"> Text </a></td><td><a href="../Data/M3.5IabFe-1var?_HD14488_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>HD 28487</td> <td>  </td> <td>M3.5 III Ca-0.5</td> <td>SRc:</td>  <td> 0.81-5.02 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3.5IIICa-0.5_HD28487.fits"> FITS </a></td><td><a href="../Data/M3.5IIICa-0.5_HD28487.txt"> Text </a></td><td><a href="../Data/M3.5IIICa-0.5_HD28487.png">  PNG </a></td> <td><a href="../Data/M3.5IIICa-0.5_HD28487_ext.fits"> FITS </a></td><td><a href="../Data/M3.5IIICa-0.5_HD28487_ext.txt"> Text </a></td><td><a href="../Data/M3.5IIICa-0.5_HD28487_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 273</td> <td> Luyten's Star </td> <td>M3.5 V</td> <td></td>  <td> 0.81-4.91 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M3.5V_Gl273.fits"> FITS </a></td><td><a href="../Data/M3.5V_Gl273.txt"> Text </a></td><td><a href="../Data/M3.5V_Gl273.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 19058</td> <td> &rho Per </td> <td>M4+ IIIa</td> <td>SRb</td>  <td> 0.81-4.18 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4+IIIa_HD19058.fits"> FITS </a></td><td><a href="../Data/M4+IIIa_HD19058.txt"> Text </a></td><td><a href="../Data/M4+IIIa_HD19058.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 214665</td> <td>  </td> <td>M4+ III</td> <td>Lb</td>  <td> 0.81-4.09 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4+III_HD214665.fits"> FITS </a></td><td><a href="../Data/M4+III_HD214665.txt"> Text </a></td><td><a href="../Data/M4+III_HD214665.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 4408</td> <td> 57 Psc </td> <td>M4 III</td> <td>SRs</td>  <td> 0.81-5.00 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4III_HD4408.fits"> FITS </a></td><td><a href="../Data/M4III_HD4408.txt"> Text </a></td><td><a href="../Data/M4III_HD4408.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 27598</td> <td> DG Eri </td> <td>M4- III</td> <td>SRb</td>  <td> 0.81-5.02 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4-III_HD27598.fits"> FITS </a></td><td><a href="../Data/M4-III_HD27598.txt"> Text </a></td><td><a href="../Data/M4-III_HD27598.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>Gl 213</td> <td>  </td> <td>M4 V</td> <td>BY</td>  <td> 0.81-5.43 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4V_Gl213.fits"> FITS </a></td><td><a href="../Data/M4V_Gl213.txt"> Text </a></td><td><a href="../Data/M4V_Gl213.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 299</td> <td>  </td> <td>M4 V</td> <td>BY:</td>  <td> 0.81-5.43 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4V_Gl299.fits"> FITS </a></td><td><a href="../Data/M4V_Gl299.txt"> Text </a></td><td><a href="../Data/M4V_Gl299.png">  PNG </a></td> <td><a href="../Data/M4V_Gl299_ext.fits"> FITS </a></td><td><a href="../Data/M4V_Gl299_ext.txt"> Text </a></td><td><a href="../Data/M4V_Gl299_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>HD 204585</td> <td> NV Peg </td> <td>M4.5 IIIa</td> <td>SRb</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4.5IIIa_HD204585.fits"> FITS </a></td><td><a href="../Data/M4.5IIIa_HD204585.txt"> Text </a></td><td><a href="../Data/M4.5IIIa_HD204585.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 268AB</td> <td> QY Aur </td> <td>M4.5 V</td> <td>UV</td>  <td> 0.81-5.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M4.5V_Gl268AB.fits"> FITS </a></td><td><a href="../Data/M4.5V_Gl268AB.txt"> Text </a></td><td><a href="../Data/M4.5V_Gl268AB.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 156014</td> <td> &alpha^1 Her A </td> <td>M5 Ib-II</td> <td>SRc</td>  <td> 0.81-4.19 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M5Ib-II_HD156014.fits"> FITS </a></td><td><a href="../Data/M5Ib-II_HD156014.txt"> Text </a></td><td><a href="../Data/M5Ib-II_HD156014.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 175865</td> <td> 13 R Lyr </td> <td>M5 III</td> <td>SRb</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M5III_HD175865.fits"> FITS </a></td><td><a href="../Data/M5III_HD175865.txt"> Text </a></td><td><a href="../Data/M5III_HD175865.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>Gl 51</td> <td>  </td> <td>M5 V</td> <td>UV</td>  <td> 0.81-4.40 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M5V_Gl51.fits"> FITS </a></td><td><a href="../Data/M5V_Gl51.txt"> Text </a></td><td><a href="../Data/M5V_Gl51.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 866ABC</td> <td> EZ Aqr </td> <td>M5 V</td> <td>UV+BY</td>  <td> 0.81-4.11 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M5V_Gl866ABC.fits"> FITS </a></td><td><a href="../Data/M5V_Gl866ABC.txt"> Text </a></td><td><a href="../Data/M5V_Gl866ABC.png">  PNG </a></td> <td><a href="../Data/M5V_Gl866ABC_ext.fits"> FITS </a></td><td><a href="../Data/M5V_Gl866ABC_ext.txt"> Text </a></td><td><a href="../Data/M5V_Gl866ABC_ext.png">  PNG </a></td> <td> R09 </td> </tr>

<tr><td>HD 94705</td> <td> VY Leo </td> <td>M5.5 III:</td> <td>Lb:</td>  <td> 0.81-4.92 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M5.5III:_HD94705.fits"> FITS </a></td><td><a href="../Data/M5.5III:_HD94705.txt"> Text </a></td><td><a href="../Data/M5.5III:_HD94705.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 196610</td> <td> EU Del </td> <td>M6 III</td> <td>SRb</td>  <td> 0.81-5.02 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M6III_HD196610.fits"> FITS </a></td><td><a href="../Data/M6III_HD196610.txt"> Text </a></td><td><a href="../Data/M6III_HD196610.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 18191</td> <td> &rho^2 Ari </td> <td>M6- III:</td> <td>SRb</td>  <td> 0.81-5.00 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M6-III:_HD18191.fits"> FITS </a></td><td><a href="../Data/M6-III:_HD18191.txt"> Text </a></td><td><a href="../Data/M6-III:_HD18191.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 406</td> <td> CN Leo </td> <td>M6 V</td> <td>UV</td>  <td> 0.81-5.46 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M6V_Gl406.fits"> FITS </a></td><td><a href="../Data/M6V_Gl406.txt"> Text </a></td><td><a href="../Data/M6V_Gl406.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr><td>GJ 1111</td> <td> DX Cnc </td> <td>M6.5 V</td> <td>UV</td>  <td> 0.81-5.43 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M6.5V_GJ1111.fits"> FITS </a></td><td><a href="../Data/M6.5V_GJ1111.txt"> Text </a></td><td><a href="../Data/M6.5V_GJ1111.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 14386</td> <td> Mira </td> <td>M5e-M9e III</td> <td>M</td>  <td> 0.81-5.01 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M5e-M9eIII_HD14386.fits"> FITS </a></td><td><a href="../Data/M5e-M9eIII_HD14386.txt"> Text </a></td><td><a href="../Data/M5e-M9eIII_HD14386.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 108849</td> <td> BK Vir </td> <td>M7- III:</td> <td>SRb</td>  <td> 0.81-4.95 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M7-III:_HD108849.fits"> FITS </a></td><td><a href="../Data/M7-III:_HD108849.txt"> Text </a></td><td><a href="../Data/M7-III:_HD108849.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>HD 207076</td> <td> EP Aqr </td> <td>M7- III:</td> <td>SRb</td>  <td> 0.81-5.03 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M7-III:_HD207076.fits"> FITS </a></td><td><a href="../Data/M7-III:_HD207076.txt"> Text </a></td><td><a href="../Data/M7-III:_HD207076.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>Gl 644C</td> <td> vB 8 </td> <td>M7 V</td> <td>UV</td>  <td> 0.81-4.15 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M7V_Gl644C.fits"> FITS </a></td><td><a href="../Data/M7V_Gl644C.txt"> Text </a></td><td><a href="../Data/M7V_Gl644C.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>MY Cep</td> <td>  </td> <td>M7-M7.5 I</td> <td>SRc</td>  <td> 0.81-4.98 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M7-M7.5I_MY_Cep.fits"> FITS </a></td><td><a href="../Data/M7-M7.5I_MY_Cep.txt"> Text </a></td><td><a href="../Data/M7-M7.5I_MY_Cep.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>HD 69243</td> <td> R Cnc </td> <td>M6e-M9e III</td> <td>M</td>  <td> 0.81-5.06 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M6e-M9eIII_HD69243.fits"> FITS </a></td><td><a href="../Data/M6e-M9eIII_HD69243.txt"> Text </a></td><td><a href="../Data/M6e-M9eIII_HD69243.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>BRI B2339-0447</td> <td>  </td> <td>M7-8 III</td> <td></td>  <td> 0.81-4.18 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M7-8III_BRIB2339-0447.fits"> FITS </a></td><td><a href="../Data/M7-8III_BRIB2339-0447.txt"> Text </a></td><td><a href="../Data/M7-8III_BRIB2339-0447.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>IRAS 01037+1219</td> <td> WX Psc </td> <td>M8 III</td> <td>M (OH/IR)</td>  <td> 0.81-5.06 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M8III_IRAS01037+1219.fits"> FITS </a></td><td><a href="../Data/M8III_IRAS01037+1219.txt"> Text </a></td><td><a href="../Data/M8III_IRAS01037+1219.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>Gl 752B</td> <td> vB 10 </td> <td>M8 V</td> <td>UV:</td>  <td> 0.81-4.14 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M8V_Gl752B.fits"> FITS </a></td><td><a href="../Data/M8V_Gl752B.txt"> Text </a></td><td><a href="../Data/M8V_Gl752B.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr><td>LP 412-31</td> <td>  </td> <td>M8 V</td> <td></td>  <td> 0.81-4.11 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M8V_LP412-31.fits"> FITS </a></td><td><a href="../Data/M8V_LP412-31.txt"> Text </a></td><td><a href="../Data/M8V_LP412-31.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>IRAS 21284-0747</td> <td> HY Aqr </td> <td>M8-9 III</td> <td>M</td>  <td> 0.81-5.05 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M8-9III_IRAS21284-0747.fits"> FITS </a></td><td><a href="../Data/M8-9III_IRAS21284-0747.txt"> Text </a></td><td><a href="../Data/M8-9III_IRAS21284-0747.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>IRAS 14436-0703</td> <td> AQ Vir </td> <td>M8-9 III</td> <td>M</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M8-9III_IRAS14436-0703.fits"> FITS </a></td><td><a href="../Data/M8-9III_IRAS14436-0703.txt"> Text </a></td><td><a href="../Data/M8-9III_IRAS14436-0703.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>IRAS 14303-1042</td> <td>  </td> <td>M8-9 III</td> <td>M</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M8-9III_IRAS14303-1042.fits"> FITS </a></td><td><a href="../Data/M8-9III_IRAS14303-1042.txt"> Text </a></td><td><a href="../Data/M8-9III_IRAS14303-1042.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>IRAS 15060+0947</td> <td> FV Boo </td> <td>M9 III</td> <td>M</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9III_IRAS15060+0947.fits"> FITS </a></td><td><a href="../Data/M9III_IRAS15060+0947.txt"> Text </a></td><td><a href="../Data/M9III_IRAS15060+0947.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>BRI B1219-1336</td> <td> VX Crv </td> <td>M9 III</td> <td>M</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9III_BRIB1219-1336.fits"> FITS </a></td><td><a href="../Data/M9III_BRIB1219-1336.txt"> Text </a></td><td><a href="../Data/M9III_BRIB1219-1336.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr><td>DENIS-P J104814.7-395606.1</td> <td>  </td> <td>M9 V</td> <td></td>  <td> 0.81-4.12 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9V_DENIS-PJ1048-3956.fits"> FITS </a></td><td><a href="../Data/M9V_DENIS-PJ1048-3956.txt"> Text </a></td><td><a href="../Data/M9V_DENIS-PJ1048-3956.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>LP 944-20</td> <td>  </td> <td>M9 V</td> <td></td>  <td> 0.81-4.13 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9V_LP944-20.fits"> FITS </a></td><td><a href="../Data/M9V_LP944-20.txt"> Text </a></td><td><a href="../Data/M9V_LP944-20.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr><td>LHS 2065</td> <td>  </td> <td>M9 V</td> <td>UV</td>  <td> 0.81-2.41 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9V_LHS2065.fits"> FITS </a></td><td><a href="../Data/M9V_LHS2065.txt"> Text </a></td><td><a href="../Data/M9V_LHS2065.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>LHS 2924</td> <td>  </td> <td>M9 V</td> <td>UV</td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9V_LHS2924.fits"> FITS </a></td><td><a href="../Data/M9V_LHS2924.txt"> Text </a></td><td><a href="../Data/M9V_LHS2924.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr><td>BRI B0021-0214</td> <td>  </td> <td>M9.5 V</td> <td>BY</td>  <td> 0.81-4.12 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M9.5V_BRIB0021-0214.fits"> FITS </a></td><td><a href="../Data/M9.5V_BRIB0021-0214.txt"> Text </a></td><td><a href="../Data/M9.5V_BRIB0021-0214.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> C05, R09 </td> </tr>

<tr style="background-color:#F0F8FF"><td>IRAS 14086-0703</td> <td> IO Vir </td> <td>M10+ III</td> <td></td>  <td> 0.81-2.42 <FONT FACE="Symbol">&#x3BC;</FONT>m</td> <td><a href="../Data/M10+III_IRAS14086-0703.fits"> FITS </a></td><td><a href="../Data/M10+III_IRAS14086-0703.txt"> Text </a></td><td><a href="../Data/M10+III_IRAS14086-0703.png">  PNG </a></td> <td> &hellip; </td><td> &hellip; </td><td> &hellip; </td><td> R09 </td> </tr>


"""
# 解析HTML
soup = BeautifulSoup(html_content, 'html.parser')
rows = soup.find_all('tr')

# 基础URL（根据实际路径调整）
base_url = "https://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/References_files/M.html"  # 替换为实际的基础URL

# 创建下载目录
os.makedirs('models/other_V', exist_ok=True)

# 提取并下载
for row in rows:
    cells = row.find_all('td')
    if len(cells) < 3:
        continue
    
    # 提取星名（优先Gliese名，没有则用HD名）
    hd_name = cells[0].get_text(strip=True)
    gl_name = cells[1].get_text(strip=True)
    star_name = gl_name if gl_name else hd_name
    
    # 提取光谱类型
    spectral_type = cells[2].get_text(strip=True)
    
    # 检查是否是V型星
    if 'V' not in spectral_type:
        continue
    
    # 查找txt下载链接
    txt_link = None
    for link in row.find_all('a', href=True):
        if link['href'].endswith('.txt'):
            txt_link = link['href']
            break
    
    if txt_link:
        # 构建完整URL
        full_url = urljoin(base_url, txt_link)
        
        # 清理文件名中的特殊字符
        clean_name = re.sub(r'[^\w\s-]', '', star_name).replace(' ', '_')
        clean_type = spectral_type.replace(' ', '')
        filename = f"{clean_name}_{clean_type}.txt"
        filepath = os.path.join('models/other_V', filename)
        
        # 下载文件
        try:
            response = requests.get(full_url)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 已下载: {filename}")
        except Exception as e:
            print(f"❌ 下载失败: {filename} - {str(e)}")

print("\n下载完成！文件保存在 'downloaded_spectra' 目录中")