<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs tei ti dct cpt dc"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/"
    xmlns:cpt="http://purl.org/capitains/ns/1.0#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    version="2.0">
    
    <xsl:output method="xml" omit-xml-declaration="yes" indent="yes" exclude-result-prefixes="#all"/>
    <xsl:param name="metadataFile"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '__capitains__.xml')"/></xsl:param>
    <xsl:param name="urn"><xsl:value-of select="/tei:TEI/tei:text/tei:body/tei:div/@n"/></xsl:param>
    <xsl:param name="teiBase" select="/tei:TEI"/>
    
    <xsl:template match="/">
        <xsl:variable name="theText">
            <xsl:call-template name="extractText">
                <xsl:with-param name="text" select="//tei:w[not(@type='no-search')]"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="theLems">
            <xsl:call-template name="extractLem">
                <xsl:with-param name="text" select="//tei:w[not(@type='no-search')]"/>
            </xsl:call-template>                        
        </xsl:variable>
        <xsl:variable name="dates">
            <xsl:call-template name="extractDates">
                <xsl:with-param name="date_tags" select="/tei:TEI/tei:text/tei:front/tei:dateline/tei:date"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="theRegest">
            <xsl:call-template name="extractRegest">
                <xsl:with-param name="shortRegest" select="document($metadataFile)/cpt:collection/cpt:members/cpt:collection[child::cpt:identifier/text()=$urn]/cpt:structured-metadata/dct:abstract/text()"/>
                <xsl:with-param name="fullRegest" select="document($metadataFile)/cpt:collection/cpt:members/cpt:collection[child::cpt:identifier/text()=$urn]/dc:description/text()"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="keywords">
            <xsl:value-of select="string-join(//tei:seg[@type='lex-keyword'], ' ')"/>
        </xsl:variable>
        <xsl:variable name="partTags"></xsl:variable>
        <xml>
            <title><xsl:value-of select="normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text())"/></title>
            <keywords><xsl:value-of select="$keywords"/></keywords>
            <dateStr><xsl:value-of select="document($metadataFile)/cpt:collection/cpt:members/cpt:collection[child::cpt:identifier/text()=$urn]/cpt:structured-metadata/dct:temporal/text()"/></dateStr>
            <compositionPlace><xsl:value-of select="document($metadataFile)/cpt:collection/cpt:members/cpt:collection[child::cpt:identifier/text()=$urn]/cpt:structured-metadata/dct:spatial/text()"/></compositionPlace>
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
            <inflected><xsl:value-of select="translate(normalize-space(replace(replace(replace(replace(replace(replace($theText, 'Æ|æ|Ę|ę', 'ae'), 'Œ|œ', 'oe'), '> ([\.,:;”])', '>$1'), '(\[|&lt;)\s+', ''), '\s+(\]|&gt;)', ''), '\[|&lt;|\]|&gt;|…', '$2')), 'ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ', 'AaAaAaEeEeEeIiIiIiOoOoOoUuUuUuCcOo')"/></inflected>
            <lemmatized><xsl:value-of select="normalize-space(replace($theLems, '\s+', ' '))"/></lemmatized>
            <regest><xsl:value-of select="$theRegest"/></regest>
            <forgery><xsl:value-of select="boolean(/tei:TEI/tei:text/tei:front/tei:note[@type='echtheit']/@n = 'forgery')"/></forgery>
            <!-- A tag for each formulaic part -->
<!--            <xsl:for-each select="distinct-values(//tei:seg/@function)">
                <xsl:element name="part">
                    <xsl:attribute name="type"><xsl:value-of select="."/></xsl:attribute>
                    <xsl:for-each select="$teiBase//tei:seg[@function=current()]">
                        <xsl:value-of select="."/>
                        <xsl:if test="position()!=last()">
                            <xsl:text> ... </xsl:text>
                        </xsl:if>
                    </xsl:for-each>
                </xsl:element>
                <xsl:element name="part">
                    <xsl:attribute name="type"><xsl:value-of select="."/><xsl:text>-lems</xsl:text></xsl:attribute>
                    <xsl:value-of select="string-join($teiBase//tei:seg[@function=current()]//tei:w/@lemma, ' ')"/>
                </xsl:element>
            </xsl:for-each>-->
        </xml>
    </xsl:template>
    
    <xsl:template name="extractText">
        <xsl:param name="text"/>
        <xsl:for-each select="$text">
            <xsl:variable name="tail"><xsl:value-of select="following-sibling::text()[1]"/></xsl:variable>
            <!--<xsl:value-of select="concat(./text(), normalize-space($tail), ' ')"/>-->
            <xsl:choose>
                <xsl:when test="not(contains($tail, ' '))">
                    <xsl:value-of select="concat(string-join(.//text(), ''), $tail, ' ')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat(string-join(.//text(), ''), $tail)"/>
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
                                        <xsl:value-of select="format-number(number(./@notAfter), '0000')"/>
                                        <xsl:text>-12-31</xsl:text>
                                    </xsl:when>
                                    <xsl:when test="string-length(./@notAfter) = 7">
                                        <xsl:value-of select="xs:date(concat(./@notAfter, '-01')) + xs:yearMonthDuration('P1M') - xs:dayTimeDuration('P1D')"/>
                                        <!--<xsl:choose>
                                            <xsl:when test="substring-after(./@notAfter, '-') != '12'">
                                                <xsl:value-of select="substring-before(./@notAfter, '-')"/>
                                                <xsl:text>-</xsl:text>
                                                <xsl:value-of select="format-number(number(substring-after(./@notAfter, '-')) + 1, '00')"/>
                                            </xsl:when>
                                            <xsl:otherwise><xsl:value-of select="format-number(number(substring-before(./@notAfter, '-')), '0000')"/><xsl:text>-12-31</xsl:text></xsl:otherwise>
                                        </xsl:choose>-->
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
