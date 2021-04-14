#!/bin/sh

# Skriver ut 'http-header' for 'plain-text' SOM SKAL VÆRE SLUTTEN AV HTTP HODET MED PÅFØLGENDE TOM LINJE FOR HTTP KROPPEN


#echo "Set-Cookie:yummycookie=$sessionidentity"
#echo "Content-type:application/xml;charset=utf-8"
#echo
# Lage en "innloggingsfunksjon" ved å sjekke passord mot e-postadresse, og sette sesjonsID
# Variabel som avgjør om bruker er "innlogget"| kanskje cookie kan erstatte den?
valid=1;
streng=$(head -c $CONTENT_LENGTH)
#echo STRENG: $streng

# En fil som mates med CLI XML fra klientens forespørsel
#echo "<?xml version="1.0"?>" > /usr/local/apache2/xml/transition.xml
#echo "<!DOCTYPE bruker SYSTEM \"http://localhost/transition.dtd\">" >> /usr/local/apache2/xml/transition.xml
echo $streng > /usr/local/apache2/xml/transition.xml

# Sjekke om det skal logges inn
bruker=$(xmlstarlet sel -t -v '//bruker' /usr/local/apache2/xml/transition.xml)
#echo BRUKER: $bruker

# Statiske variabler for XSD logikk
header="<?xml version=\"1.0\"?>"
rot=$(echo $streng | cut -d ">" -f 1)
default="xmlns=\"http://172.17.0.1\""
next="xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""

# Hvis cookie allerede er sendt med klientens forespørsel og ikke inneholder informasjon for ut-/innlogging
if [ -n "$HTTP_COOKIE" ] && [ -z "$bruker" ]; then
	
	#echo "Content-type:text/xml, application/xml;charset=utf-8"
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Methods: GET, PUT, POST, DELETE"
	echo "Access-Control-Allow-Credentials: true"
	echo "Set-Cookie: $HTTP_COOKIE"
	echo "Content-type:application/xml;charset=utf-8"
	echo
	#echo HTTP_COOKIE: $HTTP_COOKIE
	sesjonsID=$(echo $HTTP_COOKIE | cut -d = -f 2)
	#epost=$(xmlstarlet sel -t -v '//epostadresse' /usr/local/apache2/xml/transition.xml)
	#echo sesjonsID: $sesjonsID
	valid=0;
	#echo STRENG: $streng
	#echo EPOST: $epost
	#echo REQUEST_METHOD:	$REQUEST_METHOD
	#echo BRUKER: $bruker
	
# Hvis det er en variabel i bruker og metoden er POST så er det innlogging
# curl -c "cookies.txt" -v -d "<bruker><epostadresse>am.no</epostadresse><passordhash>ananas3pai</passordhash><fornavn>Kaare</fornavn><etternavn>Hagen</etternavn></bruker>" localhost:8080/sqlite/database.db/dikt
elif [ -n "$bruker" ] && [ "$REQUEST_METHOD" = "POST" ] && [ -z "$HTTP_COOKIE" ]; then
	
	# Sjekke validering mot XSD dokument på busyboxcontaineren fra mp2
	location="xsi:schemaLocation=\"http://172.17.0.1/www innlogging.xsd\">"
	
	#Droppe <bruker> fra XML strengen for å kunne referere på riktig måte til XSD dokumentet 
	ny_streng=$(echo $streng | cut -d ">" -f 2,3,4,5,6,7,8,9,10,11)
	innehald=$(printf "%s\n" "$header" "" "$rot" "$default" "$next" "$location" "$ny_streng")
	#echo "$innehald"
	#echo 
	
	#validator=$(curl -v -d "$innehald" http://172.17.0.1/innlogging.xsd)
	#validator=$(curl -v -d "$innehald" localhost/innlogging.xsd)
	#echo VALIDATOR: "$validator"
	
	# Hente epostadresse fra XML-fila (kommandolinja)
	epost=$(xmlstarlet sel -t -v '//epostadresse' /usr/local/apache2/xml/transition.xml)

	#echo EPOST: $epost

	# Hente passordet fra XML-fila (kommandolinja) og deretter kjøre MD5 for å sjekke hashen

	passord=$(xmlstarlet sel -t -v '//passordhash' /usr/local/apache2/xml/transition.xml)

	#echo PASSORD: $passord

	pwHash=$(echo -n $passord | md5sum)
	#echo pwHash: $pwHash

	pwDB=$(echo "SELECT passordhash FROM Bruker WHERE epostadresse='$epost';" | sqlite3 /usr/local/apache2/sqlite/database.db)
	#echo pwDB : $pwDB

	# Sjekke om hashene matcher hverandre

	if [ "$pwHash" = "$pwDB" ]; then
		#echo "Strings are equal."
		# Generere sesjonsID og cookie og blir da i praksis innlogget
		echo "INSERT INTO Sesjon (epostadresse) VALUES ('$epost');" | sqlite3 /usr/local/apache2/sqlite/database.db
		sessionidentity=$(echo "SELECT max(sesjonsID) FROM Sesjon;" | sqlite3 /usr/local/apache2/sqlite/database.db)
		echo "Access-Control-Allow-Origin: http://localhost"
		echo "Access-Control-Allow-Methods: GET, PUT, POST, DELETE"
		echo "Access-Control-Allow-Credentials: true"
		echo "Set-Cookie: yummycookie=$sessionidentity;"
		echo "Content-type:application/xml;charset=utf-8"
		echo
		
		#echo SESSIONIDENTITY: $sessionidentity
		valid=0;
		
		#echo "Content-type:text/xml, application/xml;charset=utf-8"
		#echo "Content-type:application/xml;charset=utf-8"
		#echo
		#echo "SELECT * FROM Sesjon;" | sqlite3 /usr/local/apache2/sqlite/database.db
		#echo VALID: $valid
		#echo HTTP_COOKIE: $HTTP_COOKIE
		#echo STRENG: $streng
		#echo EPOST: $epost
		#echo REQUEST_METHOD: $REQUEST_METHOD
		#echo BRUKER: $bruker
	else
		#echo "Content-type:text/xml, application/xml;charset=utf-8"
		echo "Access-Control-Allow-Origin: http://localhost"
		echo "Access-Control-Allow-Methods: GET, POST, PUT, DELETE"
		echo "Access-Control-Allow-Credentials: true"
		echo "Content-type:application/xml;charset=utf-8"
		echo
		#echo "Incorrect password."
    fi
# Hvis det er en variabel i bruker, en cookie i headeren og metoden er DELETE så er det utlogging
# curl -b "cookies.txt" -X DELETE -d "<bruker><epostadresse>am.no</epostadresse><passordhash>ananas3pai</passordhash></bruker>" localhost:8080/sqlite/database.db/dikt
elif [ -n "$bruker" ] && [ "$REQUEST_METHOD" = "DELETE" ] && [ -n "$HTTP_COOKIE" ]; then
	
	# Hente epostadresse fra XML-fila (kommandolinja)
	epost=$(xmlstarlet sel -t -v '//epostadresse' /usr/local/apache2/xml/transition.xml)
	
	sesjonsID=$(echo $HTTP_COOKIE | cut -d = -f 2)
	#echo sesjonsID: $sesjonsID
	
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Methods: GET, PUT, POST, DELETE"
	echo "Access-Control-Allow-Credentials: true"
	echo "Content-type:application/xml;charset=utf-8"
	echo
	
	echo "DELETE FROM Sesjon WHERE sesjonsID='$sesjonsID';" | sqlite3 /usr/local/apache2/sqlite/database.db
	valid=1
	#echo "Slette OK."
	echo "SELECT * FROM Sesjon;" | sqlite3 /usr/local/apache2/sqlite/database.db
	
else
	#echo "Content-type:text/xml, application/xml;charset=utf-8"
	echo "Access-Control-Allow-Origin: http://localhost"
	echo "Access-Control-Allow-Methods: GET, POST, PUT, DELETE"
	echo "Access-Control-Allow-Credentials: true"
	echo "Content-type:application/xml;charset=utf-8"
	echo
	#echo "hoy"
fi

# Skriver ut 'http-header' for 'plain-text' SOM SKAL VÆRE SLUTTEN AV HTTP HODET MED PÅFØLGENDE TOM LINJE FOR HTTP KROPPEN
#echo "Set-Cookie:yummycookie=$sessionidentity"
#echo "Content-type:text/plain;charset=utf-8"

# Skriver ut tom linje for å skille hodet fra kroppen
#echo

#echo REQUEST_URI:	$REQUEST_URI
#echo REQUEST_METHOD:	$REQUEST_METHOD
#echo QUERY_STRING:	$QUERY_STRING
#echo CONTENT_LENGTH:	$CONTENT_LENGTH
#echo CONTENT_TYPE       $CONTENT_TYPE
#echo HTTP_ACCEPT: $HTTP_ACCEPT
#echo HTTP_COOKIE:       $HTTP_COOKIE

# GET skal kunne gjøres uten å være innlogget, både ett bestemt dikt eller alle dikt
# curl localhost:8080/sqlite/database.db/dikt/1
if [ "$REQUEST_METHOD" = "GET" ]; then
    #echo $REQUEST_URI skal hentes
    database=$(echo $REQUEST_URI | cut -d / -f 3)
    #echo DATABASE:  $database
    tabell=$(echo $REQUEST_URI | cut -d / -f 4)
    #echo TABELL:    $tabell
    id=$(echo $REQUEST_URI | cut -d / -f 5)
    #echo ID:        $id

    # Dirigere serveren til å hente ressursen/alle ressursene
    if [[ -n "${id}" ]]; then
		dikt=$(echo "SELECT $tabell FROM $tabell WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db)
		epostadresse=$(echo "SELECT epostadresse FROM $tabell where diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db)
		xmlcont="<dikt><diktID>$id</diktID><diktu>$dikt</diktu><epostadresse>$epostadresse</epostadresse></dikt>"
		
		# Sjekke validering mot XSD dokument på busyboxcontaineren fra mp2
		location="xsi:schemaLocation=\"http://172.17.0.1/www hentdikt.xsd\">"
		#Droppe <dikt> fra XML strengen for å kunne referere på riktig måte til XSD dokumentet 
		rot=$(echo $xmlcont | cut -d ">" -f 1)
		#echo ROT: $rot
		ny_streng=$(echo $xmlcont | cut -d ">" -f 2,3,4,5,6,7,8,9)
		#echo NY_STRENG: $ny_streng
		innehald=$(printf "%s\n" "$header" "" "$rot" "$default" "$next" "$location" "$ny_streng")
		#echo INNEHALD: "$innehald"
		#echo 
		
		echo $xmlcont
    else
		antall=$(echo "SELECT MAX(diktID) FROM $tabell;" | sqlite3 /usr/local/apache2/sqlite/database.db)
		#echo ANTALL: $antall
		dikttall=1
		#echo DIKTTALL: $dikttall
		while [ $dikttall -le $antall ]
		do
			dikt=$(echo "SELECT $tabell FROM $tabell WHERE diktID=$dikttall;" | sqlite3 /usr/local/apache2/sqlite/database.db)
			epostadresse=$(echo "SELECT epostadresse FROM $tabell where diktID=$dikttall;" | sqlite3 /usr/local/apache2/sqlite/database.db)
			if [ -z $dikt ]; then
				let "dikttall += 1"
				continue
			fi
			xmlcont="<dikt><diktID>$dikttall</diktID><diktu>$dikt</diktu><epostadresse>$epostadresse</epostadresse></dikt>"
			# Sjekke validering mot XSD dokument på busyboxcontaineren fra mp2
			location="xsi:schemaLocation=\"http://localhost/www hentdikt.xsd\">"
	
			#Droppe <dikt> fra XML strengen for å kunne referere på riktig måte til XSD dokumentet 
			rot=$(echo $xmlcont | cut -d ">" -f 1)
			#echo ROT: $rot
			ny_streng=$(echo $xmlcont | cut -d ">" -f 2,3,4,5,6,7,8,9)
			#echo NY_STRENG: $ny_streng
			innehald=$(printf "%s\n" "$header" "" "$rot" "$default" "$next" "$location" "$ny_streng")
			#echo INNEHALD: "$innehald"
			#echo 
			echo $xmlcont
			# Gjør så diktene blir skrevet ut penere i webgrensesnittet
			#echo "<br></br>"
			let "dikttall += 1"
		done
    fi
fi

# Må være innlogget for å kunne gjøre POST (legge til nytt dikt)
# curl -d "<dikt><tittel>Med iskrem i hånd</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
# curl -b "cookies.txt" -v -d "<dikt><tittel>Gooli cute cute</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
if [ "$REQUEST_METHOD" = "POST" ] && [ "$valid" == "0" ] && [ -z "$bruker" ]; then
   echo Følgende skal settes inn i $REQUEST_URI:
   echo
   #echo VALID: $valid

   # skriver HTTP-hode
   # streng=$(head -c $CONTENT_LENGTH)
   #echo $streng
   
   # Hvis det må over på XML logikk
   #echo $streng > /usr/local/apache2/transition.xml
   
   # Sjekke validering mot XSD dokument på busyboxcontaineren fra mp2
   location="xsi:schemaLocation=\"http://172.17.0.1/www hentdikt.xsd\">"
   #Droppe <bruker> fra XML strengen for å kunne referere på riktig måte til XSD dokumentet 
   #echo ROT: $rot
   ny_streng=$(echo $streng | cut -d ">" -f 2,3,4,5)
   #echo NY_STRENG: $ny_streng
   innehald=$(printf "%s\n" "$header" "" "$rot" "$default" "$next" "$location" "$ny_streng")
   #echo INNEHALD: "$innehald"
   #echo 
   
   epost=$(echo "SELECT epostadresse FROM Sesjon WHERE sesjonsID=$sesjonsID;" | sqlite3 /usr/local/apache2/sqlite/database.db)
   #echo EPOST: $epost
   
   samling=$(echo $streng | awk -F"<" '{print $2}' | cut -d ">" -f 0)
   #echo SAMLING: $samling

   dikt=$(echo $streng | awk -F"<" '{print $3}' | cut -d ">" -f 2)
   #echo DIKT: $dikt

   database=$(echo $REQUEST_URI | cut -d / -f 2)
   #echo DATABASE: $database
   tabell=$(echo $REQUEST_URI | cut -d / -f 3)
   #echo TABELL: $tabell

   # Diktet må få epostadressen til brukeren som legger det inn! 
   echo "INSERT INTO Dikt (dikt, epostadresse) VALUES ('$dikt', '$epost');" | sqlite3 /usr/local/apache2/sqlite/database.db
fi

# Må være innlogget for å kunne gjøre PUT (Endre egne dikt)
# curl -b "cookies.txt" -X PUT -v -d "<dikt><tittel>Bjørne børne</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
if [ "$REQUEST_METHOD" = "PUT" ] && [ "$valid" == "0" ] && [ -z "$bruker" ]; then
   echo $REQUEST_URI skal endres slik:
   echo

   # skriver-hode
   #streng=$(head -c $CONTENT_LENGTH)
   #echo
   #echo STRENG: $streng
   
   # Sjekke validering mot XSD dokument på busyboxcontaineren fra mp2
   location="xsi:schemaLocation=\"http://172.17.0.1/www hentdikt.xsd\">" 
   #Droppe <bruker> fra XML strengen for å kunne referere på riktig måte til XSD dokumentet 
   #echo ROT: $rot
   ny_streng=$(echo $streng | cut -d ">" -f 2,3,4,5,6,7,8,9,10,11)
   innehald=$(printf "%s\n" "$header" "" "$rot" "$default" "$next" "$location" "$ny_streng")
   #echo INNEHALD: "$innehald"
   #echo 
   
   # eposten tilhørende sesjonen
   ichiepost=$(echo "SELECT epostadresse FROM Sesjon WHERE sesjonsID=$sesjonsID;" | sqlite3 /usr/local/apache2/sqlite/database.db)
   
   samling=$(echo $streng | awk -F"<" '{print $2}' | cut -d ">" -f 0)
   #echo SAMLING: $samling

   dikt=$(echo $streng | awk -F"<" '{print $3}' | cut -d ">" -f 2)
   #echo DIKT: $dikt

   database=$(echo $REQUEST_URI | cut -d / -f 3)
   #echo DATABASE: $database
   tabell=$(echo $REQUEST_URI | cut -d / -f 4)
   #echo TABELL: $tabell
   id=$(echo $REQUEST_URI | cut -d / -f 5)
   #echo ID:        $id
   
   # eposten tilhørende den som har lagd diktet
   niepost=$(echo "SELECT epostadresse FROM Dikt WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db)

   # Kun der hvor epostadressen samsvarer med sesjon og dikttabell!
	if [ $niepost = $ichiepost ]; then
		echo "UPDATE Dikt SET dikt='$dikt' WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db
	else
		echo "Action is not allowed."
	fi
fi

# Må være innlogget for å kunne gjøre DELETE (Slette et eget dikt eller alle egne dikt)
if [ "$REQUEST_METHOD" = "DELETE" ] && [ "$valid" == "0" ] && [ -z "$bruker" ]; then
    echo $REQUEST_URI skal slettes
    echo
    
    # eposten tilhørende sesjonen
    ichiepost=$(echo "SELECT epostadresse FROM Sesjon WHERE sesjonsID=$sesjonsID;" | sqlite3 /usr/local/apache2/sqlite/database.db)
    #echo ICHIEPOST: $ichiepost

    database=$(echo $REQUEST_URI | cut -d / -f 3)
    #echo DATABASE: $database
    tabell=$(echo $REQUEST_URI | cut -d / -f 4)
    #echo TABELL: $tabell
    id=$(echo $REQUEST_URI | cut -d / -f 5)
    #echo ID:        $id
    
    # eposten tilhørende den som har lagd diktet
    niepost=$(echo "SELECT epostadresse FROM Dikt WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db)
    #echo NIEPOST: $niepost
    
    if [[ -n "${id}" ]]; then
		# Slett spesifikt dikt pekt på med diktID
		if [ $niepost = $ichiepost ]; then
			#antall=$(echo "SELECT count(dikt) FROM Dikt;" | sqlite3 /usr/local/apache2/sqlite/database.db)
			#echo ANTALL: $antall
			echo "DELETE FROM Dikt WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db # Slette et eget dikt, epostadresse må også samsvare?
			#echo "VACUUM;" | sqlite3 /usr/local/apache2/sqlite/database.db
			#echo "ALTER TABLE Dikt AUTO_INCREMENT=$antall;" | sqlite3 /usr/local/apache2/sqlite/database.db
		else 
			echo "Action is not allowed."
		fi
		#else echo "DELETE FROM Dikt WHERE epostadresse='$epost';" | sqlite3 /usr/local/apache/sqlite/database.db # Slette alle egne dikt, epostadresse må også samsvare?
	else 
		echo "DELETE FROM Dikt WHERE epostadresse='$ichiepost';" | sqlite3 /usr/local/apache2/sqlite/database.db
	fi
		
    # curl -X DELETE localhost:8080/sqlite/database.db/2
fi

if [ "$valid" != "0" ]; then
	#echo "You are not logged in."
fi

	  # GET
      #// curl localhost:8080/sqlite/database.db/dikt
      #// POST
      #// curl -d "<dikt><tittel>Med iskrem i hånd</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
      #// curl -b "cookies.txt" -v -d "<dikt><tittel>Gooli cute cute</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
      #// PUT 
      #// curl -b "cookies.txt" -X PUT -v -d "<dikt><tittel>Bjørne børne</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
      #// DELETE 
      #// curl -b "cookies.txt" -X DELETE -v localhost:8080/sqlite/database.db/dikt
      
      #// passord og epostadresse
	#// curl -c "cookies.txt" -v -d "<bruker><epostadresse>am.no</epostadresse><passordhash>ananas3pai</passordhash><fornavn>Kaare</fornavn><etternavn>Hagen</etternavn></bruker>" localhost:8080/sqlite/database.db/dikt
