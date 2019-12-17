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
    xpath-default-namespace="http://purl.org/ns/capitains"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:template match="/">
        <xsl:param name="folderName"><xsl:value-of select="replace(base-uri(), concat('/', tokenize(base-uri(), '/')[last()]), '')"/></xsl:param>
        <xsl:param name="finalPart"><xsl:value-of select="tokenize($folderName, '/')[last()]"/></xsl:param>
        <xsl:param name="collection">
            <xsl:choose>
                <xsl:when test="/ti:textgroup/ti:groupname">
                    <xsl:for-each select="/ti:textgroup/ti:groupname">
                        <dc:title>
                            <xsl:attribute name="xml:lang"><xsl:value-of select="./@xml:lang"/></xsl:attribute>
                            <xsl:value-of select="string-join(./text(), '')"/>
                        </dc:title>
                    </xsl:for-each>
                </xsl:when>
                <xsl:when test="/collection/dc:title">
                    <xsl:for-each select="/collection/dc:title">
                        <xsl:copy-of select="current()"/>
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                    <dc:title xml:lang="deu"><xsl:value-of select="$finalPart"/></dc:title>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="urn">
            <xsl:choose>
                <xsl:when test="/ti:textgroup"><xsl:value-of select="/ti:textgroup/@urn"/></xsl:when>
                <xsl:when test="/collection/identifier"><xsl:value-of select="/collection/identifier"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="concat('urn:cts:formulae:', $finalPart)"/></xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="shortTitle"><xsl:value-of select="string-join(//bib:AbbreviatedTitle, '')"/></xsl:param>
        <xsl:processing-instruction name="xml-model">href="../../capitains.rng" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
        <collection>
            <xsl:namespace name="cts">http://chs.harvard.edu/xmlns/cts</xsl:namespace>
            <xsl:namespace name="dct">http://purl.org/dc/terms/</xsl:namespace>
            <xsl:namespace name="dc">http://purl.org/dc/elements/1.1/</xsl:namespace>
            <xsl:namespace name="foaf">http://xmlns.com/foaf/0.1/</xsl:namespace>
            <xsl:namespace name="bib">http://bibliotek-o.org/1.0/ontology/</xsl:namespace>
            <identifier><xsl:value-of select="$urn"/></identifier>
            <xsl:copy-of select="$collection"/>
            <dc:type>cts:textgroup</dc:type>
            <structured-metadata>
                <bib:AbbreviatedTitle><xsl:value-of select="$shortTitle"/></bib:AbbreviatedTitle>
            </structured-metadata>
            <members>
                <xsl:for-each select="collection(concat($folderName, '?select=__capitains__.xml;on-error=ignore;recurse=yes'))">
                    <xsl:sort select="document-uri(.)"></xsl:sort>
                    <xsl:variable name="docuri" select="document-uri(.)"/>
                    <xsl:variable name="subcoll" select="tokenize(replace($docuri, '/__capitains__.xml', ''), '/')[last()]"/>
                    <xsl:if test="not($subcoll = $finalPart)">
                        <collection>
                            <xsl:attribute name="path">
                                <xsl:text>./</xsl:text>
                                <xsl:value-of select="$subcoll"/>
                                <xsl:text>/__capitains__.xml</xsl:text>
                            </xsl:attribute>
                            <xsl:attribute name="identifier"><xsl:value-of select="concat($urn, '.', $subcoll)"/></xsl:attribute>
                        </collection>
                    </xsl:if>
                </xsl:for-each>
            </members>
        </collection>
    </xsl:template>
    
</xsl:stylesheet>