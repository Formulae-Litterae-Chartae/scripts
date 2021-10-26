<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output
        name="general"
        method="xml"
        encoding="UTF-8"
        indent="yes"/>
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    <xsl:param name="biblFile">/home/matt/results/Bibliographie_E-Lexikon.xml</xsl:param>
    <!-- Brings in the bibliographic information from the bibliography -->
    <xsl:template match="tei:bibl">
        <xsl:param name="punct">[„“"'’]</xsl:param>
        <xsl:element name="bibl" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="n">
                <xsl:call-template name="buildNValue">
                    <xsl:with-param name="xmlNodes">
                        <xsl:call-template name="buildBibEntry">
                            <xsl:with-param name="entry" select="document($biblFile)/tei:TEI/tei:text/tei:body/tei:listBibl/tei:biblStruct[*/tei:title[@type='short']/replace(normalize-space(text()), $punct, '') = replace(normalize-space(string-join(current()//text(), '')), $punct, '')]"/>
                        </xsl:call-template>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template name="buildNValue">
        <xsl:param name="xmlNodes"/>
        <xsl:for-each select="$xmlNodes/node()">
            <xsl:choose>
                <xsl:when test="current()[@class='surname']">
                    <xsl:text>&lt;span class="surname"&gt;</xsl:text><xsl:value-of select="current()"/><xsl:text>&lt;/span&gt;</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="current()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>
    
    <xsl:include href="../../bibliography/make_bib_entry.xsl"/>
    
    <xsl:template match="@*|node()|comment()">
        <xsl:copy>
            <!--<xsl:apply-templates select="./@*"/>-->
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>