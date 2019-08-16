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
    <xsl:param name="thisFile" select="base-uri()"/>
    
    <xsl:template match="/">
        <xsl:element name="ti:work" namespace="http://chs.harvard.edu/xmlns/cts">
            <xsl:attribute name="groupUrn"><xsl:value-of select="/ti:work/@groupUrn"/></xsl:attribute>
            <xsl:attribute name="xml:lang"><xsl:value-of select="/ti:work/@xml:lang"/></xsl:attribute>
            <xsl:attribute name="urn"><xsl:value-of select="ti:work/@urn"/></xsl:attribute>
            <xsl:element name="ti:title" namespace="http://chs.harvard.edu/xmlns/cts">
                <xsl:attribute name="xml:lang">lat</xsl:attribute>
                <xsl:value-of select="/ti:work/ti:title/text()"/>
            </xsl:element>
            <xsl:for-each select="/ti:work/ti:edition|/ti:work/ti:translation">
                <xsl:variable name="textFile" select="document(replace($thisFile, '__cts__', tokenize(./@urn, ':')[4]))"/>
                <xsl:variable name="urn" select="tokenize($textFile/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
                <xsl:variable name="title">
                    <xsl:choose>
                        <xsl:when test="contains(lower-case($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()), 'formula andeca')">
                            Formula Andecavensis <xsl:value-of select="tokenize($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text(), '\s+')[3]"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <xsl:variable name="short-regest">
                    <xsl:value-of select="./cpt:structured-metadata/dct:abstract/text()"/>
                </xsl:variable>
                <xsl:variable name="long-regest">
                    <xsl:value-of select="./ti:description/text()"/>
                </xsl:variable>
                <xsl:variable name="dateCopyrighted"><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date[1]/@when"/></xsl:variable>
                <xsl:variable name="formEds" select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:editor"/>
                <xsl:variable name="otherEds" select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:editor"/>
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
                    <xsl:value-of select="string-join($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:title/text(), ': ')"/>
                    <xsl:if test="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']">
                        <xsl:text> Bd. </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']/text()"/>
                    </xsl:if>
                    <xsl:text>, </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:pubPlace/text()"/>
                    <xsl:text> </xsl:text><xsl:value-of select="$dateCopyrighted"/>
                    <xsl:if test="$textFile//tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']">
                        <xsl:text>, [URI: &lt;a target="_blank" href="</xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']/text()"/>
                        <xsl:text>"&gt;</xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']/text()"/>
                        <xsl:text>&lt;/a&gt;]</xsl:text>
                    </xsl:if>
                    <xsl:text>, S. </xsl:text>
                    <xsl:value-of select="normalize-space($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pp']/text())"/><xsl:text>.</xsl:text>
                </xsl:variable>
                <xsl:variable name="metadata">
                    <cpt:structured-metadata xml:lang="deu">
                        <dc:title><xsl:value-of select="$title"/></dc:title>
                        <dct:abstract><xsl:value-of select="$short-regest"/></dct:abstract>
                        <xsl:for-each select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:editionStmt/tei:respStmt/tei:persName/text()">
                            <dc:contributor><xsl:value-of select="."/></dc:contributor>
                        </xsl:for-each>
                        <xsl:choose>
                            <xsl:when test="not(contains(string-join($urn, '.'), 'andecavensis'))">
                                <xsl:for-each select="$otherEds">
                                    <dc:editor><xsl:value-of select="."/></dc:editor>
                                </xsl:for-each>
                                <dct:dateCopyrighted><xsl:value-of select="$dateCopyrighted"/></dct:dateCopyrighted>
                                <dct:bibliographicCitation><xsl:value-of select="$bibliographicCitation"/></dct:bibliographicCitation>
                                <xsl:element name="dct:temporal"><xsl:value-of select="normalize-space(string-join($textFile/tei:TEI/tei:text/tei:front/tei:dateline//text(), ' '))"/></xsl:element>
                                <xsl:element name="dct:spatial"><xsl:value-of select="$textFile/tei:TEI/tei:text/tei:front/tei:div[@subtype='ausstellungsort']/tei:p/text()"/></xsl:element>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:for-each select="$formEds">
                                    <dc:editor><xsl:value-of select="."/></dc:editor>
                                </xsl:for-each>
                            </xsl:otherwise>
                        </xsl:choose>
                        <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae Projekt</dc:publisher>
                        <dc:format>application/tei+xml</dc:format>
                        <dct:created><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/@when"/></dct:created>
                    </cpt:structured-metadata>
                </xsl:variable>
                <xsl:copy>
                    <xsl:attribute name="urn"><xsl:value-of select="string-join($urn, '.')"/></xsl:attribute>
                    <xsl:attribute name="workUrn"><xsl:value-of select="concat($urn[1], '.', $urn[2])"/></xsl:attribute>
                    <xsl:if test="string(node-name(.)) = 'ti:translation'"><xsl:attribute name="xml:lang"><xsl:value-of select="./@xml:lang"/></xsl:attribute></xsl:if>
                    <xsl:element name="ti:label" namespace="http://chs.harvard.edu/xmlns/cts">
                        <xsl:attribute name="xml:lang">lat</xsl:attribute>
                        <xsl:value-of select="normalize-space($title)"/>
                    </xsl:element>
                    <xsl:element name="ti:description" namespace="http://chs.harvard.edu/xmlns/cts">
                        <xsl:attribute name="xml:lang">deu</xsl:attribute>
                        <xsl:copy-of select="normalize-space($long-regest)"/>
                    </xsl:element>
                    <xsl:copy-of select="$metadata"/>
                </xsl:copy>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>