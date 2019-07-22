<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/" 
    xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    
    <xsl:template match="/">
        <xsl:param name="folderName"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '')"/></xsl:param>
        <xsl:param name="urn" select="tokenize(/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
        <xsl:param name="title">
            <xsl:choose>
                <xsl:when test="contains(lower-case(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()), 'formula andeca')">
                    Formula Andecavensis <xsl:value-of select="tokenize(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text(), '\s+')[3]"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:element name="ti:work" namespace="http://chs.harvard.edu/xmlns/cts">
            <xsl:attribute name="groupUrn"><xsl:value-of select="$urn[1]"/></xsl:attribute>
            <xsl:attribute name="xml:lang"><xsl:value-of select="/tei:TEI/tei:text/tei:body/tei:div/@xml:lang"/></xsl:attribute>
            <xsl:attribute name="urn"><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></xsl:attribute>
            <xsl:element name="ti:title" namespace="http://chs.harvard.edu/xmlns/cts">
                <xsl:attribute name="xml:lang">lat</xsl:attribute>
                <xsl:value-of select="normalize-space($title)"/>
            </xsl:element>
            <xsl:for-each select="collection(concat($folderName, '?select=*.xml;on-error=ignore'))">
                <xsl:if test="tokenize(document-uri(.), '/')[last()] != '__cts__.xml'">
                    <xsl:call-template name="createCTS">
                        <xsl:with-param name="textURI"><xsl:value-of select="document-uri(.)"/></xsl:with-param>
                    </xsl:call-template>
                </xsl:if>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>
    
    <xsl:template name="createCTS">
        <xsl:param name="textURI"/>
        <xsl:param name="textFile" select="document($textURI)"/>
        <xsl:param name="urn" select="tokenize($textFile/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
        <xsl:param name="title">
            <xsl:choose>
                <xsl:when test="contains(lower-case($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()), 'formula andeca')">
                    Formula Andecavensis <xsl:value-of select="tokenize($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text(), '\s+')[3]"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="short-regest">
            <xsl:value-of select="document(concat(replace($textURI, '/data/.*', '/regesten/'), $urn[1], '_regesten.xml'))/xml/regest[@docId=concat($urn[1], '.', $urn[2])]/shortDesc/text()"/>
        </xsl:param>
        <xsl:param name="long-regest">
            <xsl:value-of select="document(concat(replace($textURI, '/data/.*', '/regesten/'), $urn[1], '_regesten.xml'))/xml/regest[@docId=concat($urn[1], '.', $urn[2])]/longDesc/text()"/>
        </xsl:param>
        <xsl:param name="dateCopyrighted">
            <xsl:choose>
                <xsl:when test="matches($textURI, 'andecavensis|markulf')">
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/@when"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date/@when"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="allEds">
            <xsl:choose>
                <xsl:when test="matches($textURI, 'andecavensis|markulf')">
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:editor/text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:editor/text()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="bibliographicCitation">
            <xsl:choose>
                <xsl:when test="matches($textURI, 'andecavensis|markulf')">
                    <xsl:value-of select="replace(replace($title, ' +\(.*\)', ''), 'Deutsch', '(Deutsch)')"/><xsl:text>, </xsl:text>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:publisher/text()"/><xsl:text>. </xsl:text>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:pubPlace/text()"/><xsl:text> </xsl:text>
                    <xsl:value-of select="$dateCopyrighted"/>
                    <xsl:text>, [URL: https://werkstatt.formulae.uni-hamburg.de/texts/</xsl:text><xsl:value-of select="string-join($urn, '.')"/><xsl:text>/passage/all]</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:variable name="editorStr">
                        <xsl:for-each select="$allEds">
                            <xsl:choose>
                                <xsl:when test="contains(., ',')">
                                    <xsl:value-of select="substring-after(., ', ')"/><xsl:text> </xsl:text><xsl:value-of select="substring-before(., ', ')"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="."/>
                                </xsl:otherwise>
                            </xsl:choose>
                            <xsl:if test="count($allEds) > 1 and count($allEds) != index-of($allEds, .)">
                                <xsl:choose>
                                    <xsl:when test="index-of($allEds, .) != count($allEds) - 1">
                                        <xsl:text>, </xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:text> und </xsl:text>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:if>
                        </xsl:for-each>
                    </xsl:variable>
                    <xsl:value-of select="replace($title, ' +\(.*\)', '')"/><xsl:text>, in: </xsl:text><xsl:value-of select="$editorStr"/><xsl:text>, </xsl:text>
                    <xsl:value-of select="string-join($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:title/text(), ': ')"/>
                    <xsl:if test="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']">
                        <xsl:text> Bd. </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']/text()"/>
                    </xsl:if>
                    <xsl:text>, </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:pubPlace/text()"/>
                    <xsl:text> </xsl:text><xsl:value-of select="$dateCopyrighted"/>
                    <xsl:if test="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']">
                        <xsl:text>, [URI: </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']/text()"/><xsl:text>]</xsl:text>
                    </xsl:if>
                    <xsl:text>, S. </xsl:text>
                    <xsl:value-of select="normalize-space($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pp']/text())"/>
                    <xsl:text>.</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="metadata">
            <cpt:structured-metadata xml:lang="deu">
                <dc:title><xsl:value-of select="replace($title, 'Deutsch', '(Deutsch)')"/></dc:title>
                <dct:abstract><xsl:value-of select="$short-regest"/></dct:abstract>
                <xsl:for-each select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:editionStmt/tei:respStmt/tei:persName/text()">
                    <dc:contributor><xsl:value-of select="."/></dc:contributor>
                </xsl:for-each>
                <xsl:for-each select="$allEds">
                    <dc:editor><xsl:value-of select="."/></dc:editor>
                </xsl:for-each>
                <xsl:choose>
                    <xsl:when test="not(matches($textURI, 'andecavensis|markulf'))">
                        <dct:dateCopyrighted><xsl:value-of select="$dateCopyrighted"/></dct:dateCopyrighted>
                        <dct:created><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/text()"/></dct:created>
                    </xsl:when>
                    <xsl:otherwise>
                        <dct:created><xsl:value-of select="$dateCopyrighted"/></dct:created>
                    </xsl:otherwise>
                </xsl:choose>
                <dct:bibliographicCitation><xsl:value-of select="$bibliographicCitation"/></dct:bibliographicCitation>
                <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae Projekt</dc:publisher>
                <dc:format>application/tei+xml</dc:format>
            </cpt:structured-metadata>
        </xsl:param>
        
        <xsl:choose>
            <xsl:when test="contains(string-join($urn, '.'), 'deu')">
                <xsl:element name="ti:translation" namespace="http://chs.harvard.edu/xmlns/cts">
                    <xsl:attribute name="xml:lang"><xsl:value-of select="$textFile/tei:TEI/tei:text/tei:body/tei:div/@xml:lang"/></xsl:attribute>
                    <xsl:attribute name="urn"><xsl:value-of select="string-join($urn, '.')"/></xsl:attribute>
                    <xsl:attribute name="workUrn"><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></xsl:attribute>
                    <xsl:element name="ti:label" namespace="http://chs.harvard.edu/xmlns/cts">
                        <xsl:attribute name="xml:lang">deu</xsl:attribute>
                        <xsl:value-of select="replace(normalize-space($title), ' Deutsch', '')"/>
                    </xsl:element>
                    <xsl:element name="ti:description" namespace="http://chs.harvard.edu/xmlns/cts">
                        <xsl:attribute name="xml:lang">deu</xsl:attribute>
                        <xsl:copy-of select="normalize-space($long-regest)"/>
                    </xsl:element>
                    <xsl:copy-of select="$metadata"/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="ti:edition" namespace="http://chs.harvard.edu/xmlns/cts">
                    <xsl:attribute name="urn"><xsl:value-of select="string-join($urn, '.')"/></xsl:attribute>
                    <xsl:attribute name="workUrn"><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></xsl:attribute>
                    <xsl:element name="ti:label" namespace="http://chs.harvard.edu/xmlns/cts">
                        <xsl:attribute name="xml:lang">lat</xsl:attribute>
                        <xsl:value-of select="normalize-space($title)"/>
                    </xsl:element>
                    <xsl:element name="ti:description" namespace="http://chs.harvard.edu/xmlns/cts">
                        <xsl:attribute name="xml:lang">deu</xsl:attribute>
                        <xsl:copy-of select="normalize-space($long-regest)"/>
                    </xsl:element>
                    <xsl:copy-of select="$metadata"/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>