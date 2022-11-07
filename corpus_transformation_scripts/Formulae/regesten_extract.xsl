<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:template match="/">
        <xml><xsl:for-each select="/tei:TEI/tei:text/tei:body/tei:table/tei:row">
            <regest>
                <xsl:attribute name="docId">
                    <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/>
                    <xsl:choose>
                        <xsl:when test="contains(child::tei:cell[1]/., ',')">
                            <xsl:value-of select="replace(child::tei:cell[1]/., '.*(\d),.*', '$1')"/><xsl:text>_</xsl:text><xsl:number value="replace(child::tei:cell[1]/., '.*,(\d).*', '$1')" format="001"/>
                        </xsl:when>
                        <xsl:when test="contains(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text(), 'tours')">
                            <xsl:choose>
                                <xsl:when test="contains(child::tei:cell[1]/., 'Ergänzung')">
                                    <xsl:text>2_</xsl:text><xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,2})$', '$1')" format="001"/><xsl:if test="matches(child::tei:cell[1]/., '.*?(\D{1,2})$')"><xsl:text>_</xsl:text><xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)(\D{1,2})$', '$2')"/></xsl:if>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,3})$', '$1')" format="001"/><xsl:if test="matches(child::tei:cell[1]/., '\([a-z]\)$')"><xsl:text>_</xsl:text><xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)\(([a-z])\)$', '$2')"/></xsl:if>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,2})$', '$1')" format="001"/><xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,2})$', '$2')"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
                <shortDesc><xsl:apply-templates select="child::tei:cell[2]/node()"></xsl:apply-templates></shortDesc>
                <longDesc><xsl:apply-templates select="child::tei:cell[3]/node()"></xsl:apply-templates></longDesc>
            </regest>
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
    
    <xsl:template match="tei:hi[@rend='italic']">
        <xsl:text>&lt;seg class="latin-word"&gt;</xsl:text><xsl:value-of select="."/><xsl:text>&lt;/seg&gt;</xsl:text>
    </xsl:template>
    
</xsl:stylesheet>