#!/bin/sh

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/plain;charset=utf-8"

# Skriver ut tom linje for å skille hodet fra kroppen
echo

echo REQUEST_URI:	$REQUEST_URI
echo REQUEST_METHOD:	$REQUEST_METHOD
echo QUERY_STRING:	$QUERY_STRING
echo CONTENT_LENGTH:	$CONTENT_LENGTH
echo

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
	#echo .headers on | sqlite3 /usr/local/apache2/$database
	#echo .mode csv | sqlite3 /usr/local/apache2/$database
	#echo .output data.csv | sqlite3 /usr/local/apache2/$database
	echo SELECT $tabell FROM $tabell where diktID=$id | sqlite3 /usr/local/apache2/sqlite/database.db
	#echo .quit | sqlite3 /usr/local/apache2/$database
    else
	echo SELECT $tabell FROM $tabell | sqlite3 /usr/local/apache2/sqlite/database.db
    fi
fi

if [ "$REQUEST_METHOD" = "POST" ]; then
   echo Følgende skal settes inn i $REQUEST_URI:
   echo

   # skriver HTTP-hode
   streng=$(head -c $CONTENT_LENGTH)
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

if [ "$REQUEST_METHOD" = "PUT" ]; then
   echo $REQUEST_URI skal endres slik:
   echo

   # skriver-hode
   streng=$(head -c $CONTENT_LENGTH)
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

if [ "$REQUEST_METHOD" = "DELETE" ]; then
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
	#else echo "DELETE FROM Dikt WHERE epostadresse=??;" | sqlite3 /usr/local/apache/sqlite/database.db # Slette alle egne dikt, epostadresse må også samsvare?

    # curl -X DELETE localhost:8080/sqlite/database.db/2
fi
