<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs tei ti dct cpt"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/"
    xmlns:cpt="http://purl.org/capitains/ns/1.0#"
    version="2.0">
    
    <xsl:output method="xml" omit-xml-declaration="yes" indent="yes" exclude-result-prefixes="#all"/>
    <xsl:param name="metadataFile"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '__cts__.xml')"/></xsl:param>
    <xsl:param name="urn"><xsl:value-of select="/tei:TEI/tei:text/tei:body/tei:div/@n"/></xsl:param>
    
    <xsl:template match="/">
        <xsl:variable name="theText">
            <xsl:call-template name="extractText">
                <xsl:with-param name="text" select="//tei:w"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="theLems">
            <xsl:call-template name="extractLem">
                <xsl:with-param name="text" select="//tei:w"/>
            </xsl:call-template>                        
        </xsl:variable>
        <xsl:variable name="dates">
            <xsl:call-template name="extractDates">
                <xsl:with-param name="date_tags" select="/tei:TEI/tei:text/tei:front/tei:dateline/tei:date"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="theRegest">
            <xsl:call-template name="extractRegest">
                <xsl:with-param name="shortRegest" select="document($metadataFile)/ti:work/*[@urn=$urn]/cpt:structured-metadata/dct:abstract/text()"/>
                <xsl:with-param name="fullRegest" select="document($metadataFile)/ti:work/*[@urn=$urn]/ti:description/text()"/>
            </xsl:call-template>
        </xsl:variable>
        <xml>
            <title><xsl:value-of select="normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text())"/></title>
            <dateStr><xsl:value-of select="document($metadataFile)/ti:work/ti:edition[@urn=$urn]/cpt:structured-metadata/dct:temporal/text()"/></dateStr>
            <compositionPlace><xsl:value-of select="document($metadataFile)/ti:work/ti:edition[@urn=$urn]/cpt:structured-metadata/dct:spatial/text()"/></compositionPlace>
            <urn><xsl:value-of select="$urn"/></urn>
            <xsl:choose>
                <xsl:when test="contains(lower-case(normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text())), 'formula')">
                    <dating>
                        <date>
                            <gte/>
                            <lte/>
                            <when/>
                        </date>
                    </dating>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="extractDates">
                        <xsl:with-param name="date_tags" select="/tei:TEI/tei:text/tei:front/tei:dateline/tei:date"/>
                    </xsl:call-template>
                </xsl:otherwise>
            </xsl:choose>
            <!-- The outer replace function should include other text critical marks that should not get in the way of the search. -->
            <inflected><xsl:value-of select="normalize-space(replace(replace(replace(replace($theText, ' ([\.,:;”])', '$1'), '(\[|&lt;)\s+', ''), '\s+(\]|&gt;)', ''), '\[|&lt;|\]|&gt;|…', '$2'))"/></inflected>
            <lemmatized><xsl:value-of select="normalize-space(replace($theLems, '\s+', ' '))"/></lemmatized>
            <regest><xsl:value-of select="$theRegest"/></regest>
            <forgery><xsl:value-of select="boolean(/tei:TEI/tei:text/tei:front/tei:note[@type='echtheit'])"/></forgery>
        </xml>
    </xsl:template>
    
    <xsl:template name="extractText">
        <xsl:param name="text"/>
        <xsl:for-each select="$text">
            <xsl:variable name="tail"><xsl:value-of select="following-sibling::text()[1]"/></xsl:variable>
            <xsl:choose>
                <xsl:when test="not(contains($tail, ' '))">
                    <xsl:value-of select="concat(./text(), $tail, ' ')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat(./text(), $tail)"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>
    
    <xsl:template name="extractLem">
        <xsl:param name="text"/>
        <xsl:for-each select="$text">
            <xsl:value-of select="./@lemma"/><xsl:text> </xsl:text>
        </xsl:for-each>
    </xsl:template>
    
    <xsl:template name="extractDates">
        <xsl:param name="date_tags"/>
        <dating>
            <xsl:choose>
                <xsl:when test="$date_tags">
                    <xsl:for-each select="$date_tags">
                        <date><xsl:element name="gte"><xsl:value-of select="./@notBefore"/></xsl:element>
                            <lte>
                                <xsl:choose>
                                    <xsl:when test="string-length(./@notAfter) = 4">
                                        <xsl:value-of select="format-number(number(./@notAfter) + 1, '0000')"/>
                                    </xsl:when>
                                    <xsl:when test="string-length(./@notAfter) = 7">
                                        <xsl:choose>
                                            <xsl:when test="substring-after(./@notAfter, '-') != '12'">
                                                <xsl:value-of select="substring-before(./@notAfter, '-')"/>
                                                <xsl:text>-</xsl:text>
                                                <xsl:value-of select="format-number(number(substring-after(./@notAfter, '-')) + 1, '00')"/>
                                            </xsl:when>
                                            <xsl:otherwise><xsl:value-of select="format-number(number(substring-before(./@notAfter, '-')) + 1, '0000')"/></xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="./@notAfter"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </lte>
                            <when>
                                <xsl:choose>
                                    <xsl:when test="./tei:date">
                                        <xsl:for-each select="./tei:date"> 
                                            <xsl:variable name="year_range" select="./@notBefore to ./@notAfter"/>
                                            <xsl:variable name="date_when" select="./@when"/>
                                            <xsl:for-each select="$year_range"><xsl:number format="0001" value="."/><xsl:text>-</xsl:text><xsl:value-of select="substring-after($date_when, '--')"/><xsl:text>,</xsl:text></xsl:for-each>
                                        </xsl:for-each>
                                    </xsl:when>
                                    <xsl:otherwise><xsl:value-of select="./@when"/></xsl:otherwise>
                                </xsl:choose>
                            </when>
                        </date>
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                    <gte/>
                    <lte/>
                    <when/>
                </xsl:otherwise>
            </xsl:choose>
        </dating>
    </xsl:template>
    
    <xsl:template name="extractRegest">
        <xsl:param name="shortRegest"/>
        <xsl:param name="fullRegest"/>
        <xsl:if test="$shortRegest"><xsl:value-of select="$shortRegest"/> : </xsl:if><xsl:value-of select="$fullRegest"/>
    </xsl:template>
    
    <!--<xsl:template match="tei:teiHeader"></xsl:template>-->
    
</xsl:stylesheet>
