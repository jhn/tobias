import requests

json_resp = requests.post( 'http://api.sightcorp.com/api/detect/',
              data   = { 'app_key'   : '0cf15ecbf14444f1a74c86be27e7a63e',
                         'client_id' : '31939259487b4ce59c07b54b6ffd733d' },
              files  = { 'img'       : ( 'filename', open( '1.jpg', 'rb' ) ) } )

print "Response : ", json_resp.text