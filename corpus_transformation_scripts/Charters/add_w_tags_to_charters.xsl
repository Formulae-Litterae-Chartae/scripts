<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    
    <xsl:param name="pSeparators">&#xA;&#x9;&#x20;,.;:?!()'"„“‚‘+«»…</xsl:param>
    
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-model">href="https://digitallatin.github.io/guidelines/critical-editions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
        <xsl:apply-templates select="node()|comment()"/>
    </xsl:template>
    
    <!-- Surround every token in the body that is not in a <note> element with a <w> tag -->
    <xsl:template match="tei:body//*[not(ancestor-or-self::tei:note)]/text()" name="tokenize">
        <xsl:param name="pString" select="."/>
        <xsl:param name="pMask"
            select="translate(.,translate(.,$pSeparators,''),'')"/>
        <!--        <xsl:param name="pCount" select="1"/>-->
        <xsl:choose>
            <xsl:when test="not($pString)"/>
            <xsl:when test="$pMask">
                <xsl:variable name="vSeparator"
                    select="substring($pMask,1,1)"/>
                <xsl:variable name="vString"
                    select="substring-before($pString,$vSeparator)"/>
                <xsl:call-template name="tokenize">
                    <xsl:with-param name="pString" select="$vString"/>
                    <xsl:with-param name="pMask"/>
                    <!--                    <xsl:with-param name="pCount" select="$pCount"/>-->
                </xsl:call-template>
                <xsl:value-of select="$vSeparator"/>
                <xsl:call-template name="tokenize">
                    <xsl:with-param name="pString"
                        select="substring-after($pString,$vSeparator)"/>
                    <xsl:with-param name="pMask"
                        select="substring($pMask,2)"/>
                    <!--<xsl:with-param name="pCount"
                        select="$pCount + number(boolean($vString))"/>-->
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="ancestor::tei:hi[contains(@rend, 'text-transform:uppercase;')]">
                        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="upper-case($pString)"/></xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="$pString"/></xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:div[@type='textpart']/*">
        <xsl:copy>
            <xsl:attribute name="xml:space">preserve</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="@*|node()|comment()">
        <xsl:copy>
            <!--<xsl:apply-templates select="./@*"/>-->
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>