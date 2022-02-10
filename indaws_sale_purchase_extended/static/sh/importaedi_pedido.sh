#!/bin/bash
## export LANG=C.UTF-8
LANG="es_ES.UTF-8"
export LANG

AYER="$(date  --date='1 days ago' +%Y-%m-%d)"
FECHAA="$1"
# Postgres
PGSQLDB="JOVIMERSL"
PGSERVER="localhost"
PGUSER="jovimer12"
PGPASSWD="irisxvm"

# Control de Errores de Sistema
ERRORLOG="ERROR"
WARNLOG="WARN"
FECHAHORALOG="$(date +'%b %d %H:%M:%S') $HOSTNAME Alertas:"
SYSLOG="/var/log/syslog"

# Controles y Bucles
ESPERA="/bin/sleep"
SEGESPERA="0"


USREX="$(whoami)"
if [ "$USREX" == "root" ]; then
 echo "Eres Root! :)"
 PREEXECUTE="sudo -u postgres -H -- /usr/bin/"
else
 echo "No eres root... :'("
 PREEXECUTE="/usr/bin/"
fi


REC="$1"
if [ "$REC" == "" ]; then
 echo "Sin Argumentos SALGO"
 exit 0
fi


FICHEROEDI="/opt/jovimer12/ediimport/edi_$REC.txt"
rm /opt/jovimer12/ediimport/edi_$REC.txt -f
FILESTORE="$(${PREEXECUTE}psql -d $PGSQLDB -t -c "select store_fname from ir_attachment where res_id='$REC' ORDER BY id DESC LIMIT 1" | awk {'print $1'})"
cp /opt/jovimer12/.local/share/Odoo/filestore/JOVIMERSL/$FILESTORE /tmp/edi_file_$REC.tmp
iconv -f ISO-8859-1 -t UTF-8  /tmp/edi_file_$REC.tmp > $FICHEROEDI
rm /tmp/edi_file_$REC.tmp -f



echo "Leyendo Fichero"

### cat $FICHEROEDI | head -2

LINEAS="$(cat $FICHEROEDI | grep -a 'LIN  ')"
NUMLIN="$(cat $FICHEROEDI | grep -a 'LIN  ' | wc -l)"

echo ""
echo ""
echo "################################################################"
echo ""
echo ""

TIPOEDI="$(cat $FICHEROEDI | head -1 | grep 96AORDERSP | cut -c20- | awk {'print $1'})"
if [ "$TIPOEDI" == "" ]; then
 echo "Fichero No válido"
 exit 0
else
 echo "FIchero Válido: $TIPOEDI"
fi


## BOrramos lo Existente
${PREEXECUTE}psql -d $PGSQLDB -t -c "DELETE FROM sale_order_line WHERE order_id='$REC'"



EDICONTACTJOVIMER="$(cat $FICHEROEDI | head -1 | cut -c4-17 | awk {'print $1'})"
EDICONTACT="$(cat $FICHEROEDI | head -2 | tail -1 | cut -c27-40 | awk {'print $1'})"

FECHAPEDIDO="$(cat $FICHEROEDI | head -2 | tail -1 | cut -c18-26 | awk {'print $1'})"
FECHALLEGADA="$(cat $FICHEROEDI | head -2 | tail -1 | cut -c112-120 | awk {'print $1'})"

echo "Leyendo Cabecera: "
echo "ID EDI JOVIMER: $EDICONTACTJOVIMER"
echo "ID EDI CLIENTE: $EDICONTACT"
echo "FECHA PEDIDO:   $FECHAPEDIDO"
echo "FECHA LLEGADA:  $FECHALLEGADA"
echo "Num LIN:        $NUMLIN"

PARTNERID="$(${PREEXECUTE}psql -d $PGSQLDB -t -c "select partner_id from sale_order where id='$REC'" | awk {'print $1'})"
 


for i in $(seq 1 $NUMLIN); do 
 num=$(( $i + 2 ))
 echo ""
 ## cat $FICHEROEDI | head -${num} | tail -1 | cut -c1-100
 IDPROD="$(cat $FICHEROEDI | head -${num} | tail -1 | cut -c35-42 | awk {'print $1'})"
 

 
 PLANTILLABR="$(${PREEXECUTE}psql -d $PGSQLDB -t -c "select id,product,variedad from jovimer_plantillaproductos where partner='$PARTNERID' AND codproducto='$IDPROD'")"
  ## echo ">$PLANTILLABR< >$IDPROD<"

  if [ "$PLANTILLABR" == "" ]; then
  PLANTILLABR="$(${PREEXECUTE}psql -d $PGSQLDB -t -c "select id,product,variedad from jovimer_plantillaproductos where id=604")"
 fi


 IDPLANTILLA="$(echo ${PLANTILLABR[0]} | cut -d'|' -f1 | awk {'print $1'})"
 IDPRODUCTO="$(echo ${PLANTILLABR[0]} | cut -d'|' -f2 | awk {'print $1'})"
 IDVARIEDAD="$(echo ${PLANTILLABR[0]} | cut -d'|' -f3 | awk {'print $1'})"

 if [ "$IDPLANTILLA" == "" ]; then
  exit 0
 fi

 CANTIDAD="$(cat $FICHEROEDI | head -${num} | tail -1 | cut -c65-71 | awk {'print $1'})"
 UNIDAD="$(cat $FICHEROEDI | head -${num} | tail -1 | cut -c72-75 | awk {'print $1'})"

  DESPROD="$(cat $FICHEROEDI | head -${num} | tail -1 | cut -c75-125 )"
  CONVPROD="$(cat $FICHEROEDI | head -${num} | tail -1 | cut -c555- | awk {'print $1'})"
 if [ "$UNIDAD" == "CT" ]; then
  IDUNIDAD="24"
 fi
 if [ "$UNIDAD" == "PCE" ]; then
  IDUNIDAD="1"
 fi
 if [ "$UNIDAD" == "KGM" ]; then
  IDUNIDAD="27"
 fi
 if [ "$IDUNIDAD" == "" ]; then
  IDUNIDAD="1"
 fi
 echo "--------------------------------------------------------------"
 echo "IDSALE:    $REC"
 echo "IDPARTNER: $PARTNERID"
 echo "IDPROD:    >$IDPROD<  >$IDPLANTILLA<"
 echo "DETALLES:  $IDPRODUCTO $IDVARIEDAD"
 echo "CANTIDAD:  >$CANTIDAD<"
 echo "UNIDAD:    >$UNIDAD< >$IDUNIDAD<"
 echo "Linea:     $DESPROD"
 echo "--------------------------------------------------------------" 
 PEDIDOLIN="$(/opt/jovimer12/bin/webservice/create_sale_order_line_edi.py $REC $PARTNERID $IDPLANTILLA $IDPRODUCTO $CANTIDAD $IDUNIDAD)"
 ${PREEXECUTE}psql -d $PGSQLDB -t -c "UPDATE sale_order_line SET edideslin='$IDPROD >> $DESPROD UxB: $CONVPROD -----  $IDPROD - $CANTIDAD / $UNIDAD',unidabulto='$IDUNIDAD' WHERE id='$PEDIDOLIN'"


done

exit 0
