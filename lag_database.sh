#!/bin/bash

#Lager tabellene Bruker, Sesjon og Dikt
sqlite3 database.db < table_diktsamling.sql

./laghash.sh

echo "INSERT INTO Dikt (dikt, epostadresse) VALUES ('AM er kul', 'am.no');" | sqlite3 database.db

echo "INSERT INTO Dikt (dikt, epostadresse) VALUES ('dyoll hei hei', 'dyoll.no');" | sqlite3 database.db
