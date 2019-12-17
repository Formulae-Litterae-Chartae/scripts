<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/" 
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns="http://purl.org/ns/capitains"
    xmlns:owl="http://www.w3.org/2002/07/owl#" 
    xmlns:bib="http://bibliotek-o.org/1.0/ontology/"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    
    
    <xsl:template match="/">
        <xsl:param name="urn" select="tokenize(/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
        <xsl:param name="title" select="normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text())"/>
        <xsl:param name="folderName"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '')"/></xsl:param>
        <xsl:processing-instruction name="xml-model">href="../../../capitains.rng" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
        <collection>
            <xsl:namespace name="cts">http://chs.harvard.edu/xmlns/cts</xsl:namespace>
            <xsl:namespace name="dct">http://purl.org/dc/terms/</xsl:namespace>
            <xsl:namespace name="dc">http://purl.org/dc/elements/1.1/</xsl:namespace>
            <xsl:namespace name="foaf">http://xmlns.com/foaf/0.1/</xsl:namespace>
            <xsl:namespace name="bib">http://bibliotek-o.org/1.0/ontology/</xsl:namespace>
            <identifier><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></identifier>
            <parent><xsl:value-of select="$urn[1]"/></parent>
            <dc:title>
                <xsl:attribute name="xml:lang">lat</xsl:attribute>
                <xsl:value-of select="$title"/>
            </dc:title>
            <dc:type>cts:work</dc:type>
            <members>
                <xsl:for-each select="collection(concat($folderName, '?select=*.xml;on-error=ignore'))">
                    <xsl:if test="not(matches(document-uri(.), '__capitains__|__cts__'))">
                        <xsl:call-template name="createCTS">
                            <xsl:with-param name="textURI"><xsl:value-of select="document-uri(.)"/></xsl:with-param>
                        </xsl:call-template>
                    </xsl:if>
                </xsl:for-each>
            </members>
        </collection>
    </xsl:template>
    
    <xsl:template name="createCTS">
        <xsl:param name="textURI"/>
        <xsl:param name="textFile" select="document($textURI)"/>
        <xsl:param name="urn" select="tokenize($textFile/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
        <xsl:param name="lang" select="$textFile/tei:TEI/tei:text/tei:body/tei:div/@xml:lang"/>
        <xsl:param name="title">
            <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/>
        </xsl:param>
        <xsl:param name="author">
            <xsl:variable name="authors" select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author"/>
            <xsl:choose>
                <xsl:when test="count($authors) = 1">
                    <xsl:value-of select="substring-after($authors[1]/text(), ' ')"/>
                    <xsl:text>, </xsl:text>
                    <xsl:value-of select="substring-before($authors[1]/text(), ' ')"/>
                </xsl:when>
                <xsl:when test="count($authors) = 2">
                    <xsl:value-of select="substring-after($authors[1]/text(), ' ')"/>
                    <xsl:text>, </xsl:text>
                    <xsl:value-of select="substring-before($authors[1]/text(), ' ')"/>
                    <xsl:text> und </xsl:text>
                    <xsl:value-of select="$authors[2]"/>
                </xsl:when>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="creatorTags">
            <xsl:for-each select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author/text()">
                <dc:creator><xsl:value-of select="."/></dc:creator>
            </xsl:for-each>
        </xsl:param>
        <xsl:param name="date"><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/text()"/></xsl:param>
        <xsl:param name="metadata">
            <xsl:copy-of select="$creatorTags"/>
            <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
            <dc:language><xsl:value-of select="$lang"/></dc:language>
            <dc:format>application/tei+xml</dc:format>
            <structured-metadata>
                <dct:bibliographicCitation>
                    <xsl:value-of select="$author"/>
                    <xsl:text>, "</xsl:text><xsl:copy-of select="$title"/>
                    <xsl:text>", in: Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg (</xsl:text>
                    <xsl:value-of select="$date"/>
                    <xsl:text>), [URL: https://werkstatt.formulae.uni-hamburg.de/texts/</xsl:text><xsl:value-of select="string-join($urn, '.')"/><xsl:text>/passage/all]</xsl:text>
                </dct:bibliographicCitation>
                <dct:created><xsl:value-of select="$date"/></dct:created>
            </structured-metadata>
        </xsl:param>
        <xsl:param name="markedUpTitle">
            <xsl:value-of select="string-join($title//text(), '')"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="$lang"/>
            <xsl:text>)</xsl:text>
        </xsl:param>
        <xsl:param name="dateCopyrighted">
            <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/@when"/>            
        </xsl:param>
        
        <collection>
            <xsl:attribute name="readable">true</xsl:attribute>
            <xsl:attribute name="path"><xsl:text>./</xsl:text><xsl:value-of select="tokenize($textURI, '/')[last()]"/></xsl:attribute>
            <identifier><xsl:value-of select="string-join($urn, '.')"/></identifier>
            <parent><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></parent>
            <dc:title>
                <xsl:attribute name="xml:lang"><xsl:value-of select="$lang"/></xsl:attribute>
                <xsl:value-of select="$markedUpTitle"/>
            </dc:title>
            <dc:type>cts:edition</dc:type>
            <xsl:copy-of select="$metadata"/>
        </collection>
        
        
    </xsl:template>
    
</xsl:stylesheet>