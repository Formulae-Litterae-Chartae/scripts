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
    xpath-default-namespace="http://purl.org/capitains/ns/1.0#"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:param name="folderName"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '')"/></xsl:param>
    <xsl:param name="urn"><xsl:value-of select="/collection/identifier"/></xsl:param>
    <xsl:param name="finalPart">
        <xsl:value-of select="tokenize($urn, ':')[last()]"/>
    </xsl:param>
    
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="/collection/members" >
        <xsl:element name="members" namespace="http://purl.org/capitains/ns/1.0#">
            <xsl:for-each select="collection(concat($folderName, '?select=__capitains__.xml;on-error=ignore;recurse=yes'))">
                <xsl:sort select="document-uri(.)"></xsl:sort>
                <xsl:variable name="docuri" select="document-uri(.)"/>
                <xsl:variable name="subcoll" select="tokenize(replace($docuri, '/__capitains__.xml', ''), '/')[last()]"/>
                <xsl:if test="not($finalPart = $subcoll)">
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
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>