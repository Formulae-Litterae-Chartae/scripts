#!/bin/bash
for f in $( cat /home/matt/docx_tei_cte_conversion/tei_folder_list.txt );
do
    for i in $f*.xml; 
    do 
        o=$( echo $i | sed -e 's/\.xml/_CTE_in\.xml/' ); 
        o=$( echo $o | sed -e 's/\/home\/matt\/results/\/home\/matt\/results\/CTE_XML_INPUT/' );
        d=$( echo $f | sed -e 's/\/home\/matt\/results/\/home\/matt\/results\/CTE_XML_INPUT/' );
        mkdir -p $d;
        if [[ "$f" =~ .*/Kommentiert.* ]];
        then
            java -jar /home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar "$i" /home/matt/docx_tei_cte_conversion/transform_latin.xsl -o:"$o" ; 
        else
            java -jar /home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar "$i" /home/matt/docx_tei_cte_conversion/transform_translation.xsl -o:"$o" ;
        fi
    done;
done
