#base image med alpinelinux og http demon Apache
FROM httpd:alpine

#Installer sqlite3, xmlstarlet og libcap funksjonalitet i containeren
RUN apk add sqlite
RUN apk add xmlstarlet
RUN apk add curl
RUN apk add libcap

#Eventuelle HTML-dokumenter
#COPY ./public-html/ /usr/local/apache2/htdocs/

# Begrens prosessorbruk til ca 50%
#RUN cpu-shares 512

#Konfigurasjonsfil som først måtte hentes ned, for så å kopieres inn containeren
# den gjør slik at det blir tillatt CGI
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf

#Hente inn CGI-skript til containeren
COPY ./cgi-bin/* /usr/local/apache2/cgi-bin/

#Hente inn sqlite database til containeren
COPY ./database.db /usr/local/apache2/sqlite/

#Hente inn placeholder XML fil
COPY ./transition.xml /usr/local/apache2/xml/

#Endre rettigheter til databasen så Apachedemonen kan gjøre POST_REQUEST
#RUN groupadd sqlite
RUN chgrp -R daemon /usr/local/apache2/sqlite
#RUN usermod -a -G sqlite daemon
RUN chmod -R g+rwX /usr/local/apache2/sqlite

#Endre rettigheter til placeholder XML slik at den kan brukes av Apachedemonen
RUN chgrp -R daemon /usr/local/apache2/xml/
RUN chmod -R +rwX /usr/local/apache2/xml/

EXPOSE 80