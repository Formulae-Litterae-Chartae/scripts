<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    
    <xsl:param name="pSeparators">&#xA;&#x9;&#x20;,.;:?!()'"</xsl:param>
    <xsl:param name="entryTitle"><xsl:value-of select="normalize-space(/tei:TEI/tei:text/tei:body/tei:p[1]/tei:hi[1]/text())"/></xsl:param>
    <xsl:param name="urn"><xsl:value-of select="lower-case(replace(replace(substring-before(tokenize(base-uri(), '/')[last()], '.xml'), '[%20\-\s]+', '_'), '\s+', ''))"/></xsl:param>
    <xsl:param name="authorMapping">
        <abbr full="Bart Quintilier">BQ</abbr>
        <abbr full="Horst Lößlein">HL</abbr>
        <abbr full="Alexander Mueller">AM</abbr>
        <abbr full="BQ &amp; AJ">BQ &amp; AJ</abbr>
    </xsl:param>
    <xsl:param name="authorTags">
        <xsl:variable name="authorAbbr" select="normalize-space(/tei:TEI/tei:text/tei:body/tei:p[last()]//text())"/>
        <xsl:choose>
            <xsl:when test="$authorAbbr = 'BQ'">
                <author>Bart Quintelier</author>
            </xsl:when>
            <xsl:when test="$authorAbbr = 'HL'">
                <author>Horst Lößlein</author>
            </xsl:when>
            <xsl:when test="$authorAbbr = 'AM'">
                <author>Alexander Mueller</author>
            </xsl:when>
            <xsl:when test="$authorAbbr = 'BQ &amp; AJ'">
                <author>Alexandre Jeannin</author>
                <author>Bart Quintelier</author>
            </xsl:when>
        </xsl:choose>
    </xsl:param>
    <xsl:param name="biblFile">/home/matt/results/Bibliographie_E-Lexikon.xml</xsl:param>
    
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-model">href="https://digitallatin.github.io/guidelines/critical-editions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
        <xsl:apply-templates select="node()|comment()"/>
    </xsl:template>
    
    <!-- Create teiHeader -->
    <xsl:template match="tei:teiHeader">
        <xsl:copy>
            <xsl:element name="fileDesc" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:element name="titleStmt" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="$entryTitle"/></xsl:element>
                    <xsl:copy-of select="$authorTags"/>
                </xsl:element>
                <!--<xsl:element name="editionStmt" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="edition" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="tei:fileDesc/tei:editionStmt/tei:edition"/></xsl:element>
                    </xsl:element>-->
                <xsl:element name="publicationStmt" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="publisher" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">mul</xsl:attribute>Formulae-Litterae-Chartae Projekt</xsl:element>
                    <xsl:element name="pubPlace" namespace="http://www.tei-c.org/ns/1.0">Hamburg</xsl:element>
                    <xsl:element name="date" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="when"><xsl:value-of select="replace(string(current-date()), '(\d+\-\d+\-\d+).*', '$1')"/></xsl:attribute><xsl:value-of select="replace(string(current-date()), '(\d+\-\d+\-\d+).*', '$1')"/></xsl:element>
                    <xsl:element name="availability" namespace="http://www.tei-c.org/ns/1.0">
                        <!-- This should be filled in once we decide on our license -->
                        <xsl:element name="licence" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:attribute name="target">https://creativecommons.org/licenses/by/4.0/</xsl:attribute>
                            Distributed under a Creative Commons Attribution 4.0 International License.
                        </xsl:element>
                    </xsl:element>
                </xsl:element>
                <!--<xsl:element name="seriesStmt" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="level">s</xsl:attribute>
                        <xsl:value-of select="tei:fileDesc/tei:seriesStmt/tei:title"/>
                    </xsl:element>
                    <xsl:element name="biblScope" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="unit">vol</xsl:attribute>
                        <xsl:value-of select="tei:fileDesc/tei:seriesStmt/tei:biblScope"/>
                    </xsl:element>
                </xsl:element>-->
                <xsl:element name="sourceDesc" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="tei:fileDesc/tei:notesStmt/tei:note"/></xsl:element>
                </xsl:element>
            </xsl:element>
            <xsl:element name="encodingDesc" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:element name="refsDecl" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="n">CTS</xsl:attribute>
                    <xsl:element name="cRefPattern" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="n">formula</xsl:attribute>
                        <xsl:attribute name="matchPattern">(.+)</xsl:attribute>
                        <xsl:attribute name="replacementPattern">#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1'])</xsl:attribute>
                        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">This pattern extracts the whole formula</xsl:element>
                    </xsl:element>
                </xsl:element>
            </xsl:element>
        </xsl:copy>
    </xsl:template>
    
    <!-- Create correct attributes for the <body> element -->
    <xsl:template match="tei:body">
        <xsl:copy>
            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="type">edition</xsl:attribute>
                <xsl:attribute name="xml:lang">deu</xsl:attribute>
                <xsl:attribute name="n"><xsl:value-of select="concat('urn:cts:formulae:elexicon.', $urn, '.deu001')"/></xsl:attribute>
                <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">textpart</xsl:attribute>
                    <xsl:attribute name="n">1</xsl:attribute>
                    <xsl:apply-templates select="@*|node()|comment()"/>
                </xsl:element>
            </xsl:element>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="tei:note">
        <xsl:element name="note" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:apply-templates select="node()|comment()"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="tei:p">
        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:space">preserve</xsl:attribute>
            <xsl:apply-templates select="node()|comment()"/>
        </xsl:element>
    </xsl:template>
    
    <!-- Replace all <hi> elements with <seg> and transfer the @rendition attribute to @type -->
    <xsl:template match="tei:hi">
        <xsl:param name="punct">[„“"'’.,]</xsl:param>
        <xsl:choose>
            <xsl:when test="starts-with(@rend, 'Überschrift')">
                <xsl:element name="seg" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">lex-title</xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:when>
            <xsl:when test="@rend = 'Book_Title'">
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
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="seg" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:if test="@rend">
                            <xsl:attribute name="type"><xsl:value-of select="lower-case(translate(@rend, ' ', '_'))"/></xsl:attribute>
                        </xsl:if>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
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
    
    <xsl:include href="../make_bib_entry.xsl"/>
    
    <!-- DLL schema uses @rend instead of @rendition -->
    <!--<xsl:template match="@rendition">
        <xsl:choose>
            <xsl:when test=". ='#rd-Text'"/>
            <xsl:otherwise>
                <xsl:attribute name="rend" select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>-->
    
    <xsl:template match="@*|node()|comment()">
        <xsl:copy>
            <!--<xsl:apply-templates select="./@*"/>-->
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>