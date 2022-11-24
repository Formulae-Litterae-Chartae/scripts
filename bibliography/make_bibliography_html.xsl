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
            
{%block article%}
</xsl:text>
        <xsl:element name="div">
            <xsl:attribute name="class">container</xsl:attribute>
            <xsl:element name="header">
                <xsl:element name="h1">
                    <xsl:attribute name="class">text-center</xsl:attribute>
                    <xsl:text>{{ _('Bibliographie') }}</xsl:text>
                </xsl:element>
            </xsl:element>
            <h4 class="text-center">{{ _('Gehe zu Buchstabe:') }}</h4>
            <div class="row" id="elex-letters">
                <div class="col text-center">
                    <xsl:for-each select="tokenize('nr A B C D E F G H I J K L M N O P Q R S T U V W X Y Z', '\s')">
                        <xsl:choose>
                            <xsl:when test="contains($navLetters, .)">
                                <xsl:element name="a">
                                    <xsl:attribute name="type">button</xsl:attribute>
                                    <xsl:attribute name="class">elex-letter btn btn-sm px-1 mx-0 btn-outline-primary</xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when test=". = 'nr'">
                                            <xsl:attribute name="href">#BL-nr</xsl:attribute>
                                            <xsl:text>#</xsl:text>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:attribute name="href">#BL-<xsl:value-of select="."/></xsl:attribute>
                                            <xsl:value-of select="."/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    
                                </xsl:element>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:element name="a">
                                    <xsl:attribute name="type">button</xsl:attribute>
                                    <xsl:attribute name="class">elex-letter btn btn-sm px-1 mx-0 btn-outline-secondary disabled</xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when test=". = 'nr'">
                                            <xsl:attribute name="href">#BL-nr</xsl:attribute>
                                            <xsl:text>#</xsl:text>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:attribute name="href">#BL-<xsl:value-of select="."/></xsl:attribute>
                                            <xsl:value-of select="."/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:element>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </div>
            </div>
            <xsl:apply-templates/>
        </xsl:element>
        <xsl:text>
{%endblock%}</xsl:text>
            {% block additionalscript %}
        <script>
        $(window).scroll(function(){
            var navbarHeight = $('#mainNavbar').height();
            var letterPos = $('#elex-letters').offset();
            var bodyHeight = $('body').height();
            $('#elex-letters').css('top', Math.min(Math.max(bodyHeight + navbarHeight - letterPos.top, 0), navbarHeight + 20));
        });
        </script>
{% endblock %}  
        
    </xsl:template>
    
    <xsl:template match="/t:TEI/t:teiHeader"></xsl:template>
    
    <xsl:template match="/t:TEI/t:text/t:body/t:listBibl/t:biblStruct">
        <xsl:if test="not(contains(./t:monogr/t:imprint/t:pubPlace/text(), 'Formulae-Litterae-Chartae'))">
            <xsl:element name="p">
                <xsl:attribute name="class">biblEntry</xsl:attribute>
                <xsl:if test="@xml:id">
                    <xsl:attribute name="id"><xsl:value-of select="@xml:id"/></xsl:attribute>
                </xsl:if>
                <xsl:element name="span">
                    <xsl:attribute name="id"><xsl:value-of select="lower-case(replace(replace(.//t:title[@type='short'], '\W', '-'), '-+', '-'))"/></xsl:attribute>
                    <xsl:attribute name="class">title-id</xsl:attribute>
                    <xsl:call-template name="buildBibEntry">
                        <xsl:with-param name="entry" select="current()"/>
                    </xsl:call-template>
                </xsl:element>
            </xsl:element>
        </xsl:if>
    </xsl:template>
    
    <xsl:include href="make_bib_entry.xsl"/>
    
</xsl:stylesheet>