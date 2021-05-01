#base image med alpinelinux og http demon Apache
FROM httpd:alpine

#Installer sqlite3 og xmlstarlet funksjonalitet i containeren
RUN apk add curl

#Konfigurasjonsfil som først måtte hentes ned, for så å kopieres inn containeren
# den gjør slik at det blir tillatt CGI
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf

#Hente inn CGI-skript til containeren
COPY ./cgi-bin/* /usr/local/apache2/cgi-bin/

#Hente inn placeholder XML fil
RUN mkdir /usr/local/apache2/xml/

EXPOSE 80
