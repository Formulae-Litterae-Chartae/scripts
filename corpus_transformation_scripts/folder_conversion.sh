#!/bin/bash
for f in $( cat /home/matt/docx_tei_cte_conversion/folder_list.txt );
do
    for i in $f*.docx; 
    do 
        o=$( echo $i | sed -e 's/\.docx/\.xml/' ); 
        o=$( echo $o | sed -e 's/\/media\/matt\/uhhdisk\/Geschichte\/Projekte/\/home\/matt\/results/' );
        d=$( echo $f | sed -e 's/\/media\/matt\/uhhdisk\/Geschichte\/Projekte/\/home\/matt\/results/' );
        mkdir -p $d;
        curl -s -o "$o" -F upload=@"$i" http://localhost:8080/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/; 
    done;
done
