<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:template match="/">
        <xml><xsl:for-each select="/tei:TEI/tei:text/tei:body/tei:table/tei:row">
            <regest><xsl:attribute name="docId"><xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/><xsl:number value="normalize-space(child::tei:cell[1]/.)" format="001"/></xsl:attribute>
            <shortDesc><xsl:value-of select="normalize-space(child::tei:cell[2]/.)"/></shortDesc>
            <longDesc><xsl:value-of select="normalize-space(child::tei:cell[3]/.)"/></longDesc></regest>
        </xsl:for-each></xml>
    </xsl:template>
    
    <xsl:template name="extract">
        <xsl:param name="docNum"/>
        <xsl:param name="long"/>
        <xsl:param name="short"/>
        <p><xsl:value-of select="$docNum"/><xsl:text>&#13;</xsl:text>
        <xsl:value-of select="$short"/><xsl:text>&#13;</xsl:text>
        <xsl:value-of select="$long"/><xsl:text>&#13;</xsl:text></p>
    </xsl:template>
    
</xsl:stylesheet>