import sys
import pygvoicelib

print "Calling", sys.argv[1]
username="asampr2@gmail.com "
apppass="MIMEBase"
auth_token="DQAAANMAAAAuOX8FoKMFwYbsUXV9Zqwmcs1xgXz19xxV1ht0LEORC1OxdAe3hFLbTZ_8D9Rcbarhee5Q3p_N1cytLWFb5eRfpOiJ1flrqpwdRSXynbXgaS7TvxC5bv-TWwEEEWBLTXn3TpHMgi4i6FZBOpdF-ClC4JQ7vi5G_Am7eZT7Pu_qzDWKLMcCYLTNMzqToY7VKiig_vzdtBXQ9CpYQcYC82TRA5pQlYn1teWuNisu7IZEgLv0ilTHvuGuFruBR91-HpdDXzaUAMVC3NB4g-e53j39RXIjgjVdG86Pnt2MNB_Mvg"
rnr_se="FP0NVlMKidybBW+Nh4H8vfo1xtI="
client = pygvoicelib.GoogleVoice(username,apppass,auth_token,rnr_se)
# call
client.call(sys.argv[1], 3472793040)