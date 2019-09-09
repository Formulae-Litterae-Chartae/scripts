<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:output doctype-public="-//TEI//DTD TEI P5//EN"
        doctype-system="https://www.tei-c.org/release/xml/tei/custom/schema/dtd/tei_all.dtd"/>
    
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/css" href="format.css"</xsl:processing-instruction>
        <xsl:apply-templates select="node()|comment()"/>
    </xsl:template>
    
    <!-- Check the @rend attribute on each hi element.
            If it is "italic", then change it to @rendition="#rf-Latin" 
            If it is "underline"(?), then change it to "#rf-Lexicon" 
            If it is "bold", then change it to "#rf-Placeholder" -->
    <!--<xsl:template match="tei:hi">
        <xsl:choose>
            <xsl:when test="@rend='italic'">
                <xsl:copy>
                    <xsl:attribute name="rendition" select="'#rf-Latin'"/>
                    <xsl:apply-templates select="@*|node()|comment()"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                    <xsl:value-of select="text()"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>-->
    
    <!-- Transform <head> elements to <p rendition="#rd-Title"> -->
    <xsl:template match="tei:head">
        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="rend" select="'font-size:16pt;text-indent:0mm;'"/>
            <xsl:apply-templates/>
        </xsl:element>
        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0"> </xsl:element>
    </xsl:template>
    
    <!-- Deal with the different possible @rend values -->
    <xsl:template match="@rend[. !='color(FF0000)']">
        <xsl:choose>
            <xsl:when test=". ='bold'">
                <xsl:attribute name="rendition" select="'font-style:bold;'"/>
            </xsl:when>
            <xsl:when test=". ='underline'">
                <xsl:attribute name="rendition" select="'font-style:underline;'"/>
            </xsl:when>
            <xsl:when test="matches(., 'italic')">
                <xsl:attribute name="rend" select="'font-style:italic;'"/>
            </xsl:when>
            <xsl:when test=". ='Title'">
                <xsl:attribute name="rend" select="'font-size:16pt;text-indent:0mm;'"/>
            </xsl:when>
            <xsl:when test=". ='allcaps'">
                <xsl:attribute name="rend" select="'text-transform:uppercase;'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:attribute name="rendition">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Change the indentation of a <p> tag that only has a child element with @rend="allcaps" -->
    <xsl:template match="tei:p">
        <xsl:choose>
            <xsl:when test="count(./*[@rend='allcaps']) = count(./*)">
                <xsl:copy>
                    <xsl:attribute name="rend" select="'text-indent:0mm;'"/>
                    <xsl:apply-templates/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Tranform red notes (@rend="color(FF0000)") to @type="n2" on the ancestor note node -->
    <xsl:template match="tei:note">
        <xsl:choose>
            <xsl:when test="tei:p/tei:hi[@rend='color(FF0000)']">
                <xsl:variable name="n_id" select="replace(@xml:id, 't', '')"/>
                <xsl:element name="anchor" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">N1</xsl:attribute>
                    <xsl:attribute name="xml:id">
                        <xsl:value-of select="$n_id"/>
                    </xsl:attribute>
                </xsl:element>
                <xsl:copy>
                    <xsl:attribute name="type" select="'n1'"/>
                    <xsl:attribute name="target" select="concat('#', $n_id)"/>
                    <xsl:attribute name="targetEnd" select="concat('#', $n_id)"/>
                    <xsl:attribute name="place" select="'foot'"/>
                    <xsl:attribute name="n" select="@n"/>
                    <xsl:apply-templates select="node()|comment()"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <!-- A space needs to be added before the note so that CTE will identify the correct word as the target of the note -->
                <xsl:text> </xsl:text>
                <xsl:copy>
                    <xsl:attribute name="type" select="'a1'"/>
                    <xsl:apply-templates select="@*|node()|comment()"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!--<!-\- Remove div element while saving their children -\->
    <xsl:template match="tei:div">
        <xsl:apply-templates select="@*|node()|comment()"/>
    </xsl:template>
    
    <!-\- Add @xml:space="preserve" to text element -\->
    <xsl:template match="tei:text">
        <xsl:copy>
            <xsl:attribute name="xml:space" select="'preserve'"/>
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:copy>
    </xsl:template>-->
    
    <xsl:template match="@*|node()|comment()">
        <xsl:copy>
            <!--<xsl:apply-templates select="./@*"/>-->
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>