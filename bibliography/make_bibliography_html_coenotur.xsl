<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:t="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs t"
    version="2.0">
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    
    <xsl:template match="/">
        <xsl:text>{% extends "container.html" %}
            
{%block body%}
</xsl:text>
        <xsl:element name="div">
            <xsl:attribute name="class">container</xsl:attribute>
            <xsl:element name="header">
                <xsl:element name="h1">
                    <xsl:attribute name="class">text-center</xsl:attribute>
                    <xsl:text>{{ _('Bibliographie') }}</xsl:text>
                </xsl:element>
            </xsl:element>
            <xsl:apply-templates/>
        </xsl:element>
        <xsl:text>
{%endblock%}</xsl:text>
    </xsl:template>
    
    <xsl:template match="/t:TEI/t:teiHeader"></xsl:template>
    
    <xsl:template match="/t:TEI/t:text/t:body/t:listBibl/t:biblStruct">
        <xsl:element name="p">
            <xsl:attribute name="class">biblEntry</xsl:attribute>
            <xsl:attribute name="id"><xsl:value-of select="upper-case(replace(current()//t:title[@type='short']/text(), ' ', '_'))"/></xsl:attribute>
                <xsl:call-template name="buildBibEntry">
                    <xsl:with-param name="entry" select="current()"/>
                </xsl:call-template>
        </xsl:element>
    </xsl:template>
    
    <xsl:include href="make_bib_entry.xsl"/>
    
</xsl:stylesheet>