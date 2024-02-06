<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/" 
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns="http://purl.org/capitains/ns/1.0#"
    xmlns:owl="http://www.w3.org/2002/07/owl#" 
    xmlns:bib="http://bibliotek-o.org/1.0/ontology/"
    xmlns:bf="http://id.loc.gov/ontologies/bibframe/"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output
        name="general"
        method="xml"
        encoding="UTF-8"
        indent="yes"/>
    
    <xsl:template match="/tei:TEI/tei:text">
        
        <xsl:variable name="group" select="/tei:TEI/tei:text/tei:group/@xml:id"/>
        <xsl:variable name="label">
            <!--<xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:editionStmt/tei:edition/normalize-space(text())"/>
            <xsl:text>, aus </xsl:text>
            <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:sourceDesc/descendant::tei:monogr/tei:title"/>
            <xsl:text>, von </xsl:text>
            
            <!-\- If there is only one editor, his/her name will be used here. -\->
            <xsl:if test="/tei:TEI/tei:teiHeader/descendant::tei:monogr[count(tei:editor)=1]">
                <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:editor"/>
                <xsl:text>, </xsl:text>
            </xsl:if>
            
            <!-\- If there is more than one editor, their names will be added together separated with a coma (or "und" for the last two). -\->
            <xsl:if test="/tei:TEI/tei:teiHeader/descendant::tei:monogr[count(tei:editor)>1]">
                <xsl:for-each select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:editor[position()!=last() and position()!=(last()-1)]">
                    <xsl:value-of select="current()"/><xsl:text>, </xsl:text>
                </xsl:for-each>
                <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:editor[position()=(last()-1)]"/>
                <xsl:text> und </xsl:text>
                <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:editor[position()=last()]"/>
                <xsl:text>, </xsl:text>
            </xsl:if>
            
            <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:sourceDesc/descendant::tei:monogr/descendant::tei:pubPlace"/>
            <xsl:text>, </xsl:text>
            <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:sourceDesc/descendant::tei:monogr/descendant::tei:date[@n='originalAusgabe']"/>-->
            <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:title"/>
        </xsl:variable>
        <xsl:variable name="dateCopyrighted"><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date[1]/@when"/></xsl:variable>
        <xsl:variable name="otherEds" select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:editor"/>
        <xsl:variable name="bibliographicCitation">
            <xsl:for-each select="$otherEds">
                <xsl:choose>
                    <xsl:when test="contains(./text(), ',')">
                        <xsl:value-of select="substring-after(./text(), ', ')"/><xsl:text> &lt;span class="surname"&gt;</xsl:text><xsl:value-of select="substring-before(./text(), ', ')"/><xsl:text>&lt;/span&gt;</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:variable name="names" select="tokenize(./text(), '\s+')"/>
                        <xsl:value-of select="string-join(subsequence($names, 1, count($names) - 1), ' ')"/><xsl:text> &lt;span class="surname"&gt;</xsl:text><xsl:value-of select="$names[last()]"/><xsl:text>&lt;/span&gt;</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:if test="count($otherEds) > 1 and count($otherEds) != index-of($otherEds, .)">
                    <xsl:choose>
                        <xsl:when test="index-of($otherEds, .) != count($otherEds) - 1">
                            <xsl:text>, </xsl:text>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text> und </xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:if>
            </xsl:for-each>
            <xsl:text>, </xsl:text>
            <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:title/text()"/>
            <xsl:if test="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']">
                <xsl:text>Bd. </xsl:text><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']/text()"/>
            </xsl:if>
            <xsl:text>, </xsl:text><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:pubPlace/text()"/>
            <xsl:text> </xsl:text><xsl:value-of select="$dateCopyrighted"/>
            <xsl:if test="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']">
                <xsl:text>, [URI: &lt;a target="_blank" href="</xsl:text><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']/text()"/>
                <xsl:text>"&gt;</xsl:text><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']/text()"/>
                <xsl:text>&lt;/a&gt;]</xsl:text>
            </xsl:if>
        </xsl:variable>
        
        <xsl:for-each select="/tei:TEI/tei:text/tei:group/tei:text">
            <xsl:variable name="frontLang" select="./tei:front/@xml:lang"/>
            <xsl:variable name="isProblematic" select="descendant::tei:note[@n='forgery']/text()"/>
            <xsl:variable name="forgeryText" select="descendant::tei:note[@n='forgery']/text()"/>
            <xsl:result-document format="general" href="data/{ancestor::tei:group[@xml:id]/@xml:id}/{substring-after(@xml:id,'.')}/__capitains__.xml">
                <xsl:processing-instruction name="xml-model">href="../../../capitains.rng" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
                <xsl:element name="collection">
                    <xsl:namespace name="cts">http://chs.harvard.edu/xmlns/cts</xsl:namespace>
                    <xsl:namespace name="dct">http://purl.org/dc/terms/</xsl:namespace>
                    <xsl:namespace name="dc">http://purl.org/dc/elements/1.1/</xsl:namespace>
                    <xsl:namespace name="foaf">http://xmlns.com/foaf/0.1/</xsl:namespace>
                    <xsl:namespace name="bib">http://bibliotek-o.org/1.0/ontology/</xsl:namespace>
                    <xsl:namespace name="bf">http://id.loc.gov/ontologies/bibframe/</xsl:namespace>
                    <xsl:element name="identifier">urn:cts:formulae:<xsl:value-of select="@xml:id"/></xsl:element>
                    <xsl:element name="parent">urn:cts:formulae:<xsl:value-of select="ancestor::tei:group/@xml:id"/></xsl:element>
                    
                    <!-- Creating the title from the group location, the editor whose numbering we are using and the number itself. -->
                    <xsl:element name="dc:title">
                        <xsl:attribute name="xml:lang"><xsl:value-of select="$frontLang"/></xsl:attribute>
                        <xsl:text>Nr. </xsl:text><xsl:value-of select="node()/descendant::tei:div[@subtype='urkundennummer']"/>
                    </xsl:element>
                   <xsl:element name="dc:type">cts:work</xsl:element>
                   <xsl:element name="members">
                       <xsl:for-each select="descendant::tei:div[@type='edition']">
                           <xsl:variable name="urn"><xsl:value-of select="ancestor::tei:text[@xml:id]/@xml:id"/></xsl:variable>
                           <xsl:element name="collection">
                               <xsl:attribute name="readable">true</xsl:attribute>
                               <xsl:attribute name="path"><xsl:text>./</xsl:text><xsl:value-of select="tokenize(@n, ':')[last()]"/><xsl:text>.xml</xsl:text></xsl:attribute>
                               <xsl:element name="identifier"><xsl:value-of select="@n"/></xsl:element>
                               <xsl:element name="parent">urn:cts:formulae:<xsl:value-of select="$urn"/></xsl:element>
                               <xsl:element name="dc:title">
                                   <xsl:attribute name="xml:lang"><xsl:value-of select="$frontLang"/></xsl:attribute>
                                   <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:title"/>, <xsl:value-of select="ancestor::tei:text[@type='charta']/descendant::tei:div[@subtype='urkundennummer']/tei:p"/>
                               </xsl:element>
                               <xsl:choose>
                                   <xsl:when test="current()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='regest']/tei:p">
                                       <xsl:element name="dc:description"><xsl:attribute name="xml:lang"><xsl:value-of select="$frontLang"/></xsl:attribute><xsl:value-of select="current()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='regest']/tei:p"/></xsl:element>
                                   </xsl:when>
                                   <xsl:otherwise>
                                       <xsl:element name="dc:description"><xsl:attribute name="xml:lang"><xsl:value-of select="$frontLang"/></xsl:attribute><xsl:value-of select="$label"/></xsl:element>
                                   </xsl:otherwise>
                               </xsl:choose>
                               <xsl:element name="dc:language"><xsl:value-of select="@xml:lang"/></xsl:element>
                               <xsl:element name="dc:language"><xsl:value-of select="$frontLang"/></xsl:element>
                               <xsl:element name="dc:type">cts:edition</xsl:element>
                               <!-- Replace 'Morgane Pica' in the next @select with the name of the next encoder as it is written in the collection xml file. -->
                               <xsl:for-each select="/tei:TEI/tei:teiHeader/descendant::tei:respStmt/tei:persName">
                                   <xsl:element name="dc:contributor">
                                       <xsl:value-of select="current()"/>
                                   </xsl:element>
                               </xsl:for-each>
                               <xsl:element name="dc:publisher">
                                   <xsl:attribute name="xml:lang">
                                       <xsl:value-of select="/tei:TEI/descendant::tei:publicationStmt/tei:publisher/@xml:lang"/>
                                   </xsl:attribute>
                                   <xsl:value-of select="/tei:TEI/descendant::tei:publicationStmt/tei:publisher"/>
                               </xsl:element>
                               <xsl:element name="dc:format">application/tei+xml</xsl:element>
                               <xsl:element name="dc:source">
                                   <xsl:value-of select="/tei:TEI/descendant::tei:sourceDesc/descendant::tei:idno[@type='URI']"/>
                               </xsl:element>
                               
                               <xsl:element name="structured-metadata">
                                   <xsl:element name="dct:abstract"></xsl:element>
                                   <xsl:for-each select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/tei:editor">
                                       <xsl:element name="bib:editor">
                                           <xsl:value-of select="current()"/>
                                       </xsl:element>
                                   </xsl:for-each>
                                   <xsl:element name="dct:dateCopyrighted">
                                       <xsl:value-of select="$dateCopyrighted"/>
                                   </xsl:element>
                                   <xsl:element name="dct:created">
                                       <xsl:value-of select="/tei:TEI/tei:teiHeader/descendant::tei:publicationStmt/tei:date/@when"/>
                                   </xsl:element>
                                   <xsl:element name="dct:bibliographicCitation">
                                       <xsl:value-of select="$bibliographicCitation"/>
                                       <xsl:if test="current()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='seiten']"><xsl:text>, S.</xsl:text><xsl:value-of select="normalize-space(current()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='seiten']//text())"/><xsl:text>.</xsl:text></xsl:if>
                                       <xsl:if test="current()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='url']"><xsl:text> [</xsl:text><xsl:value-of select="normalize-space(current()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='url']//text())"/><xsl:text>].</xsl:text></xsl:if>
                                   </xsl:element>
                                   <xsl:element name="dct:temporal"><xsl:value-of select="normalize-space(string-join(/tei:TEI/tei:text/tei:group/tei:text[@xml:id=$urn]/tei:front/tei:dateline//text(), ' '))"/></xsl:element>
                                   <xsl:element name="dct:spatial"><xsl:value-of select="/tei:TEI/tei:text/tei:group/tei:text[@xml:id=$urn]/tei:front/tei:div[@subtype='ausstellungsort']/tei:p/text()"/></xsl:element>
                                   <xsl:if test="current()/ancestor::tei:text[@xml:id]/tei:front/tei:note[@type='source_edition']">
                                       <xsl:element name="dct:source"><xsl:value-of select="current()/ancestor::tei:text[@xml:id]/tei:front/tei:note[@type='source_edition']"/></xsl:element>
                                   </xsl:if>
                                   <xsl:choose>
                                       <xsl:when test="lower-case(current()/ancestor::tei:text[@xml:id]/tei:front/tei:note[@type='echtheit']/text()) = 'deperditum'">
                                           <xsl:element name="bf:status">deperditum</xsl:element>
                                       </xsl:when>
                                       <xsl:when test="$isProblematic">
                                           <xsl:element name="bib:Activity"><xsl:value-of select="$forgeryText"/></xsl:element>
                                       </xsl:when>
                                   </xsl:choose>
                               </xsl:element>
                           </xsl:element>
                       </xsl:for-each>
                   </xsl:element>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>
        
        <xsl:result-document format="general" href="data/{/tei:TEI/tei:text/tei:group/@xml:id}/__capitains__.xml">
            <xsl:processing-instruction name="xml-model">href="../../capitains.rng" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
            <xsl:element name="collection">
                <xsl:namespace name="cts">http://chs.harvard.edu/xmlns/cts</xsl:namespace>
                <xsl:namespace name="dct">http://purl.org/dc/terms/</xsl:namespace>
                <xsl:namespace name="dc">http://purl.org/dc/elements/1.1/</xsl:namespace>
                <xsl:namespace name="foaf">http://xmlns.com/foaf/0.1/</xsl:namespace>
                <xsl:namespace name="bib">http://bibliotek-o.org/1.0/ontology/</xsl:namespace>
                <xsl:element name="identifier">urn:cts:formulae:<xsl:value-of select="child::tei:group/@xml:id"/></xsl:element>
                
                <!-- NEW GROUPNAME NEEDED -> "Passau Urkunden"?
                    In which case get the tei:group@xml:id, format it with a capital letter,
                    and add "Urkunden"?-->
                <xsl:element name="dc:title">
                    <xsl:attribute name="xml:lang">deu</xsl:attribute>
                    <xsl:value-of select="upper-case(substring($group,1,1))"/>
                    <xsl:value-of select="substring($group,2)"/>
                    <xsl:text> Urkunden</xsl:text>
                </xsl:element>
                <xsl:element name="dc:type">cts:textgroup</xsl:element>
                <xsl:element name="members">
                    <xsl:for-each select="descendant::tei:text[@type='charta']">
                        <xsl:variable name="charter-id" select="@xml:id"/>
                        <xsl:element name="collection">
                            <xsl:attribute name="path"><xsl:text>./</xsl:text><xsl:value-of select="substring-after($charter-id, '.')"/><xsl:text>/__capitains__.xml</xsl:text></xsl:attribute>
                            <xsl:attribute name="identifier"><xsl:text>urn:cts:formulae:</xsl:text><xsl:value-of select="$charter-id"/></xsl:attribute>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:element>
            </xsl:element>
        </xsl:result-document>
    </xsl:template>
    
    <xsl:template name="makeEdName">
        <xsl:param name="element"/>
        <xsl:choose>
            <xsl:when test="$element/tei:surname">
                <xsl:value-of select="$element/tei:surname"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$element/substring-after(text(),' ')"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>