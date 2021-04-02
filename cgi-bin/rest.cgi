#!/bin/sh

# Skriver ut 'http-header' for 'plain-text' SOM SKAL VÆRE SLUTTEN AV HTTP HODET MED PÅFØLGENDE TOM LINJE FOR HTTP KROPPEN


#echo "Set-Cookie:yummycookie=$sessionidentity"
#echo "Content-type:text/plain;charset=utf-8"
#echo
# Lage en "innloggingsfunksjon" ved å sjekke passord mot e-postadresse, og sette sesjonsID
# Variabel som avgjør om bruker er "innlogget"| kanskje cookie kan erstatte den?
valid=1;
streng=$(head -c $CONTENT_LENGTH)
#echo STRENG: $streng

# En fil som mates med CLI XML fra klientens forespørsel
echo $streng > /usr/local/apache2/xml/transition.xml

# Sjekke om det skal logges inn
bruker=$(xmlstarlet sel -t -v '//bruker' /usr/local/apache2/xml/transition.xml)
#echo BRUKER: $bruker

# Hvis cookie allerede er sendt med klientens forespørsel 
if [ -n "$HTTP_COOKIE" ]; then
	
	echo "Set-Cookie:yummycookie='$HTTP_COOKIE'"
	echo "Content-type:text/plain;charset=utf-8"
	echo
	echo HTTP_COOKIE: $HTTP_COOKIE
	valid=0;
	
	
elif [ -n "$bruker" ] && [ "$REQUEST_METHOD" = "POST" ]; then
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
		#echo SESSIONIDENTITY: $sessionidentity
		valid=0;
		echo "Set-Cookie:yummycookie='$sessionidentity'"
		echo "Content-type:text/plain;charset=utf-8"
		echo
		#echo VALID: $valid
		#echo HTTP_COOKIE: $HTTP_COOKIE
	else
		echo "Content-type:text/plain;charset=utf-8"
		echo
		echo "Incorrect password."
    fi
else
	echo "Content-type:text/plain;charset=utf-8"
	echo
	echo "nub"
fi

# Skriver ut 'http-header' for 'plain-text' SOM SKAL VÆRE SLUTTEN AV HTTP HODET MED PÅFØLGENDE TOM LINJE FOR HTTP KROPPEN
#echo "Set-Cookie:yummycookie=$sessionidentity"
#echo "Content-type:text/plain;charset=utf-8"

# Skriver ut tom linje for å skille hodet fra kroppen
#echo

echo REQUEST_URI:	$REQUEST_URI
echo REQUEST_METHOD:	$REQUEST_METHOD
echo QUERY_STRING:	$QUERY_STRING
echo CONTENT_LENGTH:	$CONTENT_LENGTH
#echo CONTENT_TYPE       $CONTENT_TYPE
#echo HTTP_COOKIE:       $HTTP_COOKIE

# GET skal kunne gjøres uten å være innlogget, både ett bestemt dikt eller alle dikt
if [ "$REQUEST_METHOD" = "GET" ]; then
    echo $REQUEST_URI skal hentes
    database=$(echo $REQUEST_URI | cut -d / -f 3)
    echo DATABASE:  $database
    tabell=$(echo $REQUEST_URI | cut -d / -f 4)
    echo TABELL:    $tabell
    id=$(echo $REQUEST_URI | cut -d / -f 5)
    echo ID:        $id
    
    #[ -z "$id" ] && echo "NULL"

    # Dirigere serveren til å hente ressursen
    if [[ -n "${id}" ]]; then
		echo SELECT diktID, $tabell FROM $tabell where diktID=$id | sqlite3 /usr/local/apache2/sqlite/database.db
    else
		echo SELECT diktID, $tabell FROM $tabell | sqlite3 /usr/local/apache2/sqlite/database.db
    fi
fi

# Må være innlogget for å kunne gjøre POST (legge til nytt dikt)
if [ "$REQUEST_METHOD" = "POST" ] && [ "$valid" == "0" ] && [ -z "$bruker" ]; then
   echo Følgende skal settes inn i $REQUEST_URI:
   echo
   echo VALID: $valid

   # skriver HTTP-hode
   # streng=$(head -c $CONTENT_LENGTH)
   echo
   echo STRENG: $streng
   
   #echo $streng > /usr/local/apache2/transition.xml

   samling=$(echo $streng | awk -F"<" '{print $2}' | cut -d ">" -f 0)
   echo SAMLING: $samling

   dikt=$(echo $streng | awk -F"<" '{print $3}' | cut -d ">" -f 2)
   echo DIKT: $dikt

   database=$(echo $REQUEST_URI | cut -d / -f 2)
   echo DATABASE: $database
   tabell=$(echo $REQUEST_URI | cut -d / -f 3)
   echo TABELL: $tabell

   # Diktet må få epostadressen til brukeren som legger det inn! 
   echo "INSERT INTO Dikt (dikt, epostadresse) VALUES ('$dikt', 'nob@nob1.com');" | sqlite3 /usr/local/apache2/sqlite/database.db
fi

# Må være innlogget for å kunne gjøre PUT (Endre egne dikt)
if [ "$REQUEST_METHOD" = "PUT" ] && [ "$valid" == "0" ]; then
   echo $REQUEST_URI skal endres slik:
   echo

   # skriver-hode
   #streng=$(head -c $CONTENT_LENGTH)
   echo
   echo STRENG: $streng

   samling=$(echo $streng | awk -F"<" '{print $2}' | cut -d ">" -f 0)
   echo SAMLING: $samling

   dikt=$(echo $streng | awk -F"<" '{print $3}' | cut -d ">" -f 2)
   echo DIKT: $dikt

   database=$(echo $REQUEST_URI | cut -d / -f 3)
   echo DATABASE: $database
   tabell=$(echo $REQUEST_URI | cut -d / -f 4)
   echo TABELL: $tabell
   id=$(echo $REQUEST_URI | cut -d / -f 5)
   echo ID:        $id

   # Kun der hvor epostadressen samsvarer med sesjon og brukertabell!
   echo "UPDATE Dikt SET dikt = '$dikt' WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db
fi

# Må være innlogget for å kunne gjøre DELETE (Slette et eget dikt eller alle egne dikt)
if [ "$REQUEST_METHOD" = "DELETE" ] && [ "$valid" == "0" ]; then
    echo $REQUEST_URI skal slettes
    echo

   database=$(echo $REQUEST_URI | cut -d / -f 3)
   echo DATABASE: $database
   tabell=$(echo $REQUEST_URI | cut -d / -f 4)
   echo TABELL: $tabell
   id=$(echo $REQUEST_URI | cut -d / -f 5)
   echo ID:        $id
   
    if [[ -n "${id}" ]]; then
	echo "DELETE FROM Dikt WHERE diktID=$id;" | sqlite3 /usr/local/apache2/sqlite/database.db # Slette et eget dikt, epostadresse må også samsvare?
    fi
	#else echo "DELETE FROM Dikt WHERE epostadresse='$epost';" | sqlite3 /usr/local/apache/sqlite/database.db # Slette alle egne dikt, epostadresse må også samsvare?

    # curl -X DELETE localhost:8080/sqlite/database.db/2
fi

if [ "$valid" != "0" ]; then
	echo "You are not logged in."
fi

