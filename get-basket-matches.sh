#!/bin/bash
NUMPARTITE=(14 14 10 14 10 22 22 14)
read -a DESCRIZIONE <<< "Under\ 13 Under\ 14 Under\ 15 Under\ 16 Under\ 18 Under\ 20 Promozione Serie\ D"
read -a CAMPIONATO <<< "U13/M U14/M U15/M U16/M U18/M PM PM D"
read -a COD <<< "21498 20326 20992 20134 21141 23688 25216 26263"
read -a SQUADRA <<< "BC\ GARDOLO BC\ GARDOLO BC\ GARDOLO BC\ GARDOLO BC\ GARDOLO BC\ GARDOLO\ U20 BC\ GARDOLO BC\ GARDOLO"
read -a FASE <<< "2 1 2 1 2 5 7 1"
for i in `seq ${#DESCRIZIONE[@]}`
do
	INDEX=$i-1
	echo "---- ${DESCRIZIONE[$INDEX]} ----"
	for PARTITA in `seq ${NUMPARTITE[$INDEX]}`
	do
		if (( $PARTITA <= $((${NUMPARTITE[$INDEX]}/2)) )); then
			GIRONE=1
			TURNO=$PARTITA
		else
			GIRONE=0
			TURNO=$(($PARTITA-${NUMPARTITE[$INDEX]}/2))		
		fi
		URL="http://fip.it/AjaxGetDataCampionato.asp?com=RTN&camp=${CAMPIONATO[$INDEX]}&fase=${FASE[$INDEX]}&girone=${COD[$INDEX]}&ar=$GIRONE&turno=$TURNO"
		WEBCONTENT=`curl "$URL" -s`
		WEBDATA=`echo "$WEBCONTENT" | hxnormalize -x | hxselect -c 'div.risTr1 td' | lynx -stdin -dump -crawl`
		WEBDATA2=`echo "$WEBCONTENT" | hxnormalize -x | hxselect 'div.risTr2' | lynx -stdin -dump -width 200`
		LINES=$(echo "$WEBDATA" | wc -l)
		for j in `seq $(($LINES/6))`
		do
			LUOGO=`echo "$WEBDATA2" | sed "$((${j}*2-1))q;d" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'`
			SQUADRAA=`echo "$WEBDATA" | sed "$((${j}*6-4))q;d" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'`
			SQUADRAB=`echo "$WEBDATA" | sed "$((${j}*6-2))q;d" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'`
			DATA=`echo "$WEBDATA" | sed "$((${j}*6))q;d" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'`
			if [ "$SQUADRAA" == "${SQUADRA[$INDEX]}" ] || [ "$SQUADRAB" == "${SQUADRA[$INDEX]}" ]; then
				if [[ "$DATA" == *"/"* ]]; then
					TEMPARR=(${DATA//-/ })
					#cambio data da europea a americana
					GIORNO=`echo "${TEMPARR[0]}" | awk -F'[/]' '{printf "%s/%s/%s",$2,$1,$3}'`
					GIORNODOPO=`date -d"$GIORNO+1day" +'%m/%d/%Y'`
					ORA=${TEMPARR[1]}
					echo "    $SQUADRAA vs $SQUADRAB - $DATA"
					echo "        $LUOGO"
					if [[ `gcalcli search --calendar="Partite ${DESCRIZIONE[$INDEX]}" "${DESCRIZIONE[$INDEX]}" "$GIORNO" "$GIORNODOPO" --refresh` == *"No Events Found..."* ]]; then
						echo "        Inserisco la partita in Google Calendar"
						gcalcli --calendar "Partite ${DESCRIZIONE[$INDEX]}" --title "${DESCRIZIONE[$INDEX]}: $SQUADRAA vs $SQUADRAB" --when "$GIORNO $ORA" --duration 90 add --where "$LUOGO" --description "${DESCRIZIONE[$INDEX]}" --reminder 30 --refresh
					fi
					if [[ `gcalcli search --calendar="Partite" "${DESCRIZIONE[$INDEX]}" "$GIORNO" "$GIORNODOPO" --refresh` == *"No Events Found..."* ]]; then
						echo "        Inserisco la partita nel calendario generale"
						gcalcli --calendar "Partite" --title "${DESCRIZIONE[$INDEX]}: $SQUADRAA vs $SQUADRAB" --when "$GIORNO $ORA" --duration 90 add --where "$LUOGO" --description "${DESCRIZIONE[$INDEX]}" --reminder 30 --refresh
					fi
				else
					echo "$SQUADRAA vs $SQUADRAB - $DATA"
				fi
			fi		
		done
	done
done
