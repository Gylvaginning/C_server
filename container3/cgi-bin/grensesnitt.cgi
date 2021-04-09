#!/bin/sh

#echo "Content-type:text/html;charset=utf-8"
#echo

read BODY

metodevalg=$(echo $BODY | awk -F "metodevalg=" '{print $2}')

if [ "$metodevalg" == "Logg+inn" ]; then
	epost=$(echo $BODY | awk -F "epost=" '{print $2}')
	epost=$(echo $epost | awk -F "&" '{print $1}')
	#echo EPOST: $epost
	
	#echo -e "|||"
	passord=$(echo $BODY | awk -F "passord=" '{print $2}')
	passord=$(echo $passord | awk -F "&" '{print $1}')
	#echo PASSORD: $passord
	#echo "Du forsøker logge inn med eposten: $epost og passordet: $passord"
	
	# Send oppgitte data til REST API på container numerounodocker http://172.17.0.3/sqlite/database.db/dikt
	# echo curl -d "<bruker><epostadresse>$epost</epostadresse><passordhash>$passord</passordhash></bruker>" http://localhost:8081/sqlite/database.db/dikt
	responseheaders=$(curl -i -d "<bruker><epostadresse>$epost</epostadresse><passordhash>$passord</passordhash></bruker>" http://172.17.0.3/sqlite/database.db/dikt)
	#echo RESPONSEHEADERS: $responseheaders
	
	# Hente ut cookie verdien satt av server
	cookie=$(echo $responseheaders | awk -F "Set-Cookie:" '{print $2}')
	cookie=$(echo $cookie | awk -F " " '{print $1}')
	#echo COOKIE: $cookie
	echo "Set-Cookie:$cookie"
	#echo "Content-type:text/html;charset=utf-8"
	#echo
	
elif [ "$metodevalg" == "Logg+ut" ]; then
	epost=$(echo $BODY | awk -F "epost=" '{print $2}')
	epost=$(echo $epost | awk -F "&" '{print $1}')
	
	passord=$(echo $BODY | awk -F "passord=" '{print $2}')
	passord=$(echo $passord | awk -F "&" '{print $1}')
	#echo "Du forsøker logge ut med eposten: $epost og passordet: $passord"
	
	# Hente ut cookie verdi sendt av klient
	#responseheader=$(curl -i http://127.0.0.1/cgi-bin/grensesnitt.cgi)
	#responseheader=$(curl -b "$COOKIE" -X DELETE -i -d "<bruker><epostadresse>$epost</epostadresse><passordhash>$passord</passordhash></bruker>" http://172.17.0.3/sqlite/database.db/dikt)
	respons=$(curl -b "$HTTP_COOKIE" -X DELETE -d "<bruker><epostadresse>$epost</epostadresse><passordhash>$passord</passordhash></bruker>" http://172.17.0.3/sqlite/database.db/dikt)
	
	echo "Set-Cookie:yummycookie=; expires=Thu, 01 Jan 1970 00:00:00 GMT"
	#echo "Content-type:text/html;charset=utf-8"
	#echo
	
else  
	metode=$(echo "$metodevalg" | awk -F "&" '{print $1}')
	#echo METODE: $metode
	#echo -e "|||"
	#echo "Content-type:text/html;charset=utf-8"
	#echo
fi

echo "Content-type:text/html;charset=utf-8"
echo

#echo RESPONSEHEADER: $responseheader
#echo BODY: $body

cat << EOF
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<link rel="stylesheet" href="http://url/stil.css">
		<title>Startside</title>
	</head>

	<body>

	<p><a href="http://172.17.0.1/index.html"> Besøk nettsiden vår!</a></p>

	<h2>Innlogging</h2>
	
	<!-- Form taggen benyttes for å ha lage et HTML skjema for brukerinput -->
	<form method="POST">
	      <label for="epost">Epostadresse:</label><br>
	      <input type="text" id="epost" name="epost" value"Skrive epostadresse her"><br>
	      <label for="passord">Passord:</label><br>
	      <input type="password" id="passord" name="passord"><br>
	      <input type="submit" name="metodevalg" value="Logg inn">
	      <input type="submit" name="metodevalg" value="Logg ut">
	</form>

	<h2>Handlinger</h2>

	<form method="POST">
		<input type="radio" id="hentdikt" name="metodevalg" value="GET">
		<label for="hentdikt">Hent dikt</label><br>
		<input type="text" id="diktid" name="diktid" value="skriv diktID her, eller la være tom"><br>
		<br>
		
		<input type="radio" id="publiserdikt" name="metodevalg" value="POST">
		<label for="publiserdikt">Publiser dikt</label><br>
		<input type="text" id="dikt" name="dikt" value="Skriv diktet ditt her" size="50"><br>
		<br>
		
		<input type="radio" id="endredikt" name="metodevalg" value="PUT">
		<label for="endredikt">Endre dikt</label><br>
		<input type="text" id="diktid" name="diktid" value="skriv DiktID"><br>
		<input type="text" id="dikt" name="dikt" value="Skriv diktet på nytt her" size="50"><br>
		<br>
		
		<input type="radio" id="slettdikt" name="metodevalg" value="DELETE">
		<label for="slettdikt">Slett dikt</label><br>
		<input type="text" id="diktid" name="diktid" value="skriv diktID her, eller la være tom"><br><br>
		<input type="submit" name="submit" value="submit"><br><br>

	</form>
	
	</body>
	
</html>
EOF
   
# echo $BODY
#echo -e "|||"
# metodevalg=$(echo $BODY | awk -F "metodevalg=" '{print $2}')
# echo METODEVALG: $metodevalg
#echo -e "|||"
	
		
	if [ "$metode" == "GET" ]; then
		diktID=$(echo $BODY | awk -F "diktid=" '{print $2}')
		diktID=$(echo $diktID | awk -F "&" '{print $1}')
		echo DIKTID: $diktID
		#if [ "$diktID" == "skriv diktID her, eller la være tom" ]; then
		#	echo "Alle dikt skal slettes."
	
	elif [ "$metode" == "POST" ]; then
		dikt=$(echo $BODY | awk -F "dikt=" '{print $2}')
		dikt=$(echo $dikt | awk -F "&" '{print $1}')
		dikt=$(echo $dikt | tr + ' ' )
		echo DIKT: $dikt
		#dikt=$(echo $BODY | awk -F "dikt=" '{print $2}')
		
	elif [ "$metode" == "PUT" ]; then
		diktID=$(echo $BODY | awk -F "diktid=" '{print $3}')
		diktID=$(echo $diktID | awk -F "&" '{print $1}')
		echo diktID: $diktID
		echo -e "|||"
		
		dikt=$(echo $BODY | awk -F "dikt=" '{print $3}')
		dikt=$(echo $dikt | awk -F "&" '{print $1}')
		dikt=$(echo $dikt | tr + ' ' )
		echo DIKT: $dikt
		
	elif [ "$metode" == "DELETE" ]; then
		diktID=$(echo $BODY | awk -F "diktid=" '{print $4}')
		diktID=$(echo $diktID | awk -F "&" '{print $1}')
		echo diktID: $diktID
	else
		
	fi



#echo "nubs"
# if metodevalg="Logg inn"
# curl -c "cookies.txt" -v -d "<bruker><epostadresse>am.no</epostadresse><passordhash>ananas3pai</passordhash></bruker>" localhost:8080/sqlite/database.db/dikt

# elif metodevalg = logg ut
# curl -b "cookies.txt" -v -X DELETE -d "<bruker><epostadresse>am.no</epostadresse><passordhash>ananas3pai</passordhash></bruker>" localhost:8080/sqlite/database.db/dikt

# elif metodevalg = hentdikt
# curl localhost:8080/sqlite/database.db/dikt

# elif metodevalg = postdikt
# curl -d "<dikt><tittel>Med iskrem i hånd</tittel></dikt>" localhost:8080/sqlite/database.db/dikt
# curl -b "cookies.txt" -v -d "<dikt><tittel>Gooli cute cute</tittel></dikt>" localhost:8080/sqlite/database.db/dikt

# elif metodevalg = endredikt
# curl -b "cookies.txt" -X PUT -v -d "<dikt><tittel>Bjørne børne</tittel></dikt>" localhost:8080/sqlite/database.db/dikt

# elif metodevalg = slettdikt
# if diktid
# curl -b "cookies.txt" -X DELETE -v localhost:8080/sqlite/database.db/dikt/$diktID
# else 
# curl -b "cookies.txt" -X DELETE -v localhost:8080/sqlite/database.db/dikt
