dbhost = 'localhost'
dbuser = 'postgres'
dbpass = 'admin'
dbname = 'sap'
#DB_URI = 'postgresql://postgres:admin@127.0.0.1:5432/sap'
DB_URI = 'postgresql://' + dbuser + ':' + dbpass + '@' + dbhost + '/' +dbname