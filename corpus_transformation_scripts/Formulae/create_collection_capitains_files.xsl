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
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:template match="/">
        <xsl:param name="folderName"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '')"/></xsl:param>
        <xsl:param name="collection"><xsl:value-of select="tokenize($folderName, '/')[last() - 1]"/></xsl:param>
        <xsl:param name="urn">
            <xsl:text>urn:cts:formulae:</xsl:text><xsl:value-of select="$collection"/>
        </xsl:param>
        <xsl:processing-instruction name="xml-model">href="../../capitains.rng" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
        <collection>
            <identifier><xsl:value-of select="$urn"/></identifier>
            <dc:title>
                <xsl:attribute name="xml:lang">deu</xsl:attribute>
                <xsl:value-of select="$collection"/>
            </dc:title>
            <dc:type>cts:textgroup</dc:type>
            <structured-metadata>
                <bib:AbbreviatedTitle><xsl:value-of select="$collection"/></bib:AbbreviatedTitle>
            </structured-metadata>
            <members>
                <xsl:for-each select="collection(concat($folderName, '?select=__capitains__.xml;recurse=yes'))">
                    <xsl:if test="document-uri(.) != concat($folderName, '__capitains__.xml')">
                        <xsl:variable name="metadata" select="document(document-uri(.))"/>
                        <xsl:variable name="childUrn" select="$metadata/*:collection/*:identifier[1]"/>
                        <xsl:element name="collection" namespace="http://purl.org/capitains/ns/1.0#">
                            <xsl:attribute name="path">
                                <xsl:text>./</xsl:text>
                                <xsl:value-of select="replace(document-uri(.), $folderName, '')"/>
                            </xsl:attribute>
                            <xsl:attribute name="identifier">
                                <xsl:value-of select="$childUrn"/>
                            </xsl:attribute>
                        </xsl:element>
                        </xsl:if>
                </xsl:for-each>
            </members>
        </collection>
    </xsl:template>
    
</xsl:stylesheet>