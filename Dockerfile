#base image med alpinelinux og http demon Apache
FROM httpd:alpine

#Installer sqlite3 og xmlstarlet funksjonalitet i containeren
RUN apk add sqlite
RUN apk add xmlstarlet

#Eventuelle HTML-dokumenter
#COPY ./public-html/ /usr/local/apache2/htdocs/

#Konfigurasjonsfil som først måtte hentes ned, for så å kopieres inn containeren
# den gjør slik at det blir tillatt CGI
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf

#Hente inn CGI-skript til containeren
COPY ./cgi-bin/* /usr/local/apache2/cgi-bin/

#Hente inn sqlite database til containeren
COPY ./database.db /usr/local/apache2/sqlite/

#Hente inn placeholder xml fil
COPY ./transition.xml /usr/local/apache2/

#Endre rettigheter til databasen så det går an for Apache å gjøre POST_REQUEST
#RUN groupadd sqlite
RUN chgrp -R daemon /usr/local/apache2/sqlite
#RUN usermod -a -G sqlite daemon
RUN chmod -R g+rwX /usr/local/apache2/sqlite

EXPOSE 80