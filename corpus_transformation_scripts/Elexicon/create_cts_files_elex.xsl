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
    
    <xsl:param name="urn" select="tokenize(/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
    <xsl:param name="title" select="normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text())"/>
    <xsl:param name="author">
        <xsl:variable name="authors" select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author"/>
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
        <xsl:for-each select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author/text()">
            <dc:creator><xsl:value-of select="."/></dc:creator>
        </xsl:for-each>
    </xsl:param>
    <xsl:param name="date"><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/text()"/></xsl:param>
    <xsl:param name="metadata">
        <cpt:structured-metadata xml:lang="deu">
            <dc:title><xsl:value-of select="$title"/></dc:title>
            <xsl:copy-of select="$creatorTags"/>
            <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
            <dc:language>Deutsch</dc:language>
            <dc:format>application/tei+xml</dc:format>
            <dct:bibliographicCitation>
                <xsl:value-of select="$author"/>
                <xsl:text>, "</xsl:text><xsl:copy-of select="$title"/>
                <xsl:text>", in: Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg (</xsl:text>
                <xsl:value-of select="$date"/>
                <xsl:text>), [URL: https://werkstatt.formulae.uni-hamburg.de/texts/</xsl:text><xsl:value-of select="string-join($urn, '.')"/><xsl:text>/passage/all]</xsl:text>
            </dct:bibliographicCitation>
            <dct:created><xsl:value-of select="$date"/></dct:created>
        </cpt:structured-metadata>
    </xsl:param>
    
    <xsl:template match="/">
        <xsl:element name="ti:work" namespace="http://chs.harvard.edu/xmlns/cts">
            <xsl:attribute name="groupUrn"><xsl:value-of select="$urn[1]"/></xsl:attribute>
            <xsl:attribute name="xml:lang"><xsl:value-of select="/tei:TEI/tei:text/tei:body/tei:div/@xml:lang"/></xsl:attribute>
            <xsl:attribute name="urn"><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></xsl:attribute>
            <xsl:element name="ti:title" namespace="http://chs.harvard.edu/xmlns/cts">
                <xsl:attribute name="xml:lang">lat</xsl:attribute>
                <xsl:value-of select="$title"/>
            </xsl:element>
            <xsl:element name="ti:edition" namespace="http://chs.harvard.edu/xmlns/cts">
                <xsl:attribute name="urn"><xsl:value-of select="string-join($urn, '.')"/></xsl:attribute>
                <xsl:attribute name="workUrn"><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></xsl:attribute>
                <xsl:element name="ti:label" namespace="http://chs.harvard.edu/xmlns/cts">
                    <xsl:attribute name="xml:lang">lat</xsl:attribute>
                    <xsl:value-of select="$title"/>
                </xsl:element>
                <xsl:element name="ti:description" namespace="http://chs.harvard.edu/xmlns/cts">
                    <xsl:attribute name="xml:lang">mul</xsl:attribute>
                    <xsl:value-of select="replace($metadata/cpt:structured-metadata/dct:bibliographicCitation/text(), ', $', '')"/>
                </xsl:element>
                <xsl:copy-of select="$metadata"/>
            </xsl:element>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>