<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:t="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs t"
    version="2.0">
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    <xsl:param name="navLetters">
        <xsl:for-each select="//@xml:id">
            <xsl:value-of select="replace(., 'BL-', '')"/>
        </xsl:for-each>
    </xsl:param>
    
    <xsl:template match="/">
        <xsl:text>{% extends "main::container.html" %}
            {% block title %}{{ _('Liste der Formelhandschriften') }}{% endblock %}
{%block article%}
</xsl:text>
        <xsl:element name="div">
            <xsl:attribute name="class">container</xsl:attribute>
            <xsl:element name="h3">
                <xsl:text>{{ _('Liste der Formelhandschriften') }}</xsl:text>
            </xsl:element>            
            <xsl:element name="h3">
                <xsl:value-of select="//text()[contains(., '(Stand')]"/>
            </xsl:element>
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:element>
        <xsl:text>{% endblock %}</xsl:text>
    </xsl:template>
    
    <xsl:template match="/t:TEI/t:teiHeader"></xsl:template>
    
    <xsl:template match="/t:TEI/t:text/t:body/t:p">
        <xsl:choose>
            <xsl:when test="contains(string-join(.//text(), ''), 'Liste der Formelhandschriften')"></xsl:when>
            <xsl:when test="contains(string-join(.//text(), ''), '(Stand')"></xsl:when>
            <xsl:when test="contains(string-join(.//text(), ''), 'Lit.')">
                <p class="smallfont">
                    <xsl:apply-templates/>
                </p>
            </xsl:when>
            <xsl:otherwise>
                <p><xsl:apply-templates/></p>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="t:hi[@rend='smallcaps']">
        <span class="surname"><xsl:value-of select="."/></span>
    </xsl:template>
    
    <xsl:template match="t:hi[@rend='italic']">
        <span class="italic"><xsl:value-of select="."/></span>
    </xsl:template>
    
    <xsl:template match="t:hi[@rend='bold']">
        <strong><xsl:value-of select="."/></strong>
    </xsl:template>
    
    <xsl:template match="t:hi[@rend='bold subscript']" mode="siglen">
        <span class="manuscript-number"><xsl:value-of select="."/></span>
    </xsl:template>
    
    <xsl:template match="t:hi[@rend='superscript']">
        <span class="small superscript"><xsl:value-of select="."/></span>
    </xsl:template>
    
    <xsl:template match="t:table">
        <div class="card" id="manuscript-table" width="60%">
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    
    <xsl:template match="t:row">
        <xsl:choose>
            <xsl:when test="./t:cell[1]/t:hi[@rend='bold']">
                <div class="card-header"><xsl:value-of select="./t:cell[1]/t:hi[@rend='bold']"/></div>
            </xsl:when>
            <xsl:when test="not(./t:cell[1]/t:hi/text())"></xsl:when>
            <xsl:otherwise>
                <dl class="row">
                    <dt class="col-10"><xsl:apply-templates select="./t:cell[1]/t:hi"/></dt>
                    <dd class="col"><strong><xsl:apply-templates select="./t:cell[2]/t:hi" mode="siglen"/></strong></dd>
                </dl>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>