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
    
    <xsl:param name="pSeparators">&#xA;&#x9;&#x20;&#8230;&#8221;,.;:?!()'"„“‚‘</xsl:param>
    <xsl:param name="formTitle">
        <xsl:variable name="tempTitle"><xsl:value-of select="normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text())"/></xsl:variable>
        <xsl:choose>
            <xsl:when test="contains($tempTitle, '(')">
                <xsl:variable name="folia" select="/tei:TEI/tei:text/tei:body/tei:p[starts-with(., '[fol.')]"/>
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">form-name</xsl:attribute>
                    <xsl:choose>
                        <xsl:when test="matches($tempTitle, 'Weltzeitalter|Capitula')">
                            <xsl:value-of select="normalize-space(substring-before($tempTitle, '('))"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="replace(string-join(subsequence(tokenize($tempTitle, '\s+'), 1, 2), ' '), ',$', '')"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:element>
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">siglum</xsl:attribute>
                    <xsl:value-of select="replace($tempTitle, '.*\((\w+)\)$', '$1')"/>
                </xsl:element>
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">manuscript-desc</xsl:attribute>
                    <xsl:choose>
                        <xsl:when test="contains($tempTitle, 'Fu2')">
                            <xsl:text>Fulda, Hessische Landesbibliothek, D1</xsl:text>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="normalize-space(string-join(subsequence(tokenize(substring-before($tempTitle, '('), '\s+'), 3), ' '))"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:element>
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">folia</xsl:attribute>
                    <xsl:value-of select="normalize-space(translate(string-join($folia[1], ' '), '[]', ''))"/>
                    <xsl:if test="count($folia) > 1">
                        <xsl:text>-</xsl:text><xsl:value-of select="normalize-space(translate(string-join($folia[last()], ' '), '[]', ''))"/>
                    </xsl:if>
                </xsl:element>
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:variable name="firstFolio"><xsl:value-of select="normalize-space(translate(string-join($folia[1], ' '), '[]', ''))"/></xsl:variable>
                    <xsl:variable name="lastFolio"><xsl:value-of select="normalize-space(translate(string-join($folia[last()], ' '), '[]', ''))"/></xsl:variable>
                    <xsl:attribute name="type">markedUpFolia</xsl:attribute>
                    <xsl:text>fol.</xsl:text>
                    <xsl:value-of select="replace($firstFolio, '\D+(\d+)([rvab]+)', '$1')"/>
                    <xsl:text>&lt;span class="verso-recto"&gt;</xsl:text>
                    <xsl:value-of select="replace($firstFolio, '\D+(\d+)([rvab]+)', '$2')"/>
                    <xsl:text>&lt;/span&gt;</xsl:text>
                    <xsl:if test="count($folia) > 1">
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="replace($lastFolio, '\D+(\d+)([rvab]+)', '$1')"/>
                        <xsl:text>&lt;span class="verso-recto"&gt;</xsl:text>
                        <xsl:value-of select="replace($lastFolio, '\D+(\d+)([rvab]+)', '$2')"/>
                        <xsl:text>&lt;/span&gt;</xsl:text>
                    </xsl:if>
                </xsl:element>
            </xsl:when>
            <xsl:when test="contains($tempTitle, 'Deutsch')">
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">form-name</xsl:attribute>
                    <xsl:choose>
                        <xsl:when test="matches($tempTitle, 'Weltzeitalter|Capitula')">
                            <xsl:value-of select="replace($tempTitle, ' Deutsch', '')"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="replace(string-join(subsequence(tokenize($tempTitle, '\s+'), 1, 2), ' '), ',$', '')"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:element>
                <xsl:element name="xml:lang">deu</xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">form-name</xsl:attribute>
                    <xsl:choose>
                        <xsl:when test="matches($tempTitle, 'Weltzeitalter|Capitula')">
                            <xsl:value-of select="$tempTitle"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="replace(string-join(subsequence(tokenize($tempTitle, '\s+'), 1, 2), ' '), ',$', '')"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:element>
                <xsl:element name="xml:lang">lat</xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:param>
    <xsl:param name="formNumber">
        <xsl:choose>
            <xsl:when test="$formTitle/tei:ref[@type='folia']">
                <xsl:value-of select="normalize-space(replace($formTitle/tei:ref[@type='folia'], 'fol\.\s*|-', ''))"/>
            </xsl:when>
            <xsl:when test="contains($formTitle, 'Weltzeitalter')">
                <xsl:text>computus</xsl:text>
            </xsl:when>
            <xsl:when test="contains($formTitle, 'Capitula')">
                <xsl:if test="contains($formTitle/tei:ref[@type='form-name'], 'II')"><xsl:text>2_</xsl:text></xsl:if><xsl:text>capitula</xsl:text>
            </xsl:when>
            <xsl:when test="matches(lower-case($formTitle/tei:ref[@type='form-name']), 'marculf|markulf')">
                <xsl:choose>
                    <xsl:when test="contains($formTitle/tei:ref[@type='form-name'], ',')">
                        <xsl:text>form</xsl:text><xsl:if test="contains($formTitle/tei:ref[@type='form-name'], 'II')"><xsl:text>2_</xsl:text></xsl:if><xsl:number value="substring-after($formTitle/tei:ref[@type='form-name'], ',')" format="001"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>form</xsl:text><xsl:number value="subsequence(tokenize($formTitle/tei:ref[@type='form-name'], '\s+'), 2, 1)" format="001"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>form</xsl:text><xsl:number value="subsequence(tokenize($formTitle/tei:ref[@type='form-name'], '\s+'), 2, 1)" format="001"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:param>
    <xsl:param name="manuscript">
        <xsl:choose>
            <xsl:when test="$formTitle/xml:lang = 'deu'">
                <xsl:text>deu001</xsl:text>
            </xsl:when>
            <xsl:otherwise><xsl:text>lat001</xsl:text></xsl:otherwise>
        </xsl:choose>
    </xsl:param>
    <!--<xsl:param name="formNumber">1</xsl:param>-->
    <xsl:param name="biblFile">/home/matt/results/Bibliographie_E-Lexikon.xml</xsl:param>
    <xsl:param name="collection">
        <xsl:choose>
            <xsl:when test="$formTitle/tei:ref[@type='siglum']">
                <xsl:value-of select="lower-case($formTitle/tei:ref[@type='siglum'])"/>
            </xsl:when>
            <xsl:when test="matches(lower-case($formTitle/tei:ref[@type='form-name']), 'marculf|markulf')">
                <xsl:text>marculf</xsl:text>
            </xsl:when>
            <xsl:when test="matches(lower-case($formTitle/tei:ref[@type='form-name']), 'angers|andecavensis')">
                <xsl:text>andecavensis</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="tokenize(lower-case($formTitle/tei:ref[@type='form-name']), '\s+')[1]"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:param>
    <xsl:param name="urnStart">
        <xsl:choose>
            <xsl:when test="$formTitle/tei:ref[@type='siglum']">
                <xsl:text>urn:cts:formulae:</xsl:text><xsl:value-of select="lower-case($formTitle/tei:ref[@type='siglum'])"/><xsl:text>.</xsl:text>
            </xsl:when>
            <xsl:when test="matches(lower-case($formTitle/tei:ref[@type='form-name']), 'marculf|markulf')">
                <xsl:text>urn:cts:formulae:marculf.</xsl:text>
            </xsl:when>
            <xsl:when test="matches(lower-case($formTitle/tei:ref[@type='form-name']), 'angers|andecavensis')">
                <xsl:text>urn:cts:formulae:andecavensis.</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>urn:cts:formulae:</xsl:text><xsl:value-of select="tokenize(lower-case($formTitle/tei:ref[@type='form-name']), '\s+')[1]"/><xsl:text>.</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:param>
    
    <xsl:template match="/">
        <xsl:choose>
            <xsl:when test="$formTitle/tei:ref[@type='folia']">
                <xsl:result-document format="general" href="./temp/{$collection}.{$formNumber}.{$manuscript}.xml" validation="strip">
                    <xsl:processing-instruction name="xml-model">href="https://digitallatin.github.io/guidelines/critical-editions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
                    <xsl:apply-templates select="node()|comment()"/>
                </xsl:result-document>
            </xsl:when>
            <xsl:otherwise>
                <xsl:result-document format="general" href="./data/{$collection}/{$formNumber}/{$collection}.{$formNumber}.{$manuscript}.xml" validation="strip">
                    <xsl:processing-instruction name="xml-model">href="https://digitallatin.github.io/guidelines/critical-editions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
                    <xsl:apply-templates select="node()|comment()"/>
                </xsl:result-document>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Create teiHeader -->
    <xsl:template match="tei:teiHeader">
            <xsl:copy>
                <xsl:attribute name="xml:lang">deu</xsl:attribute>
                <xsl:element name="fileDesc" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="titleStmt" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:choose>
                            <xsl:when test="$formTitle/tei:ref[@type='manuscript-desc']">
                                <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:value-of select="$formTitle/tei:ref[@type='manuscript-desc']"/>
                                    <xsl:text> </xsl:text>
                                    <xsl:text>[</xsl:text>
                                    <xsl:value-of select="$formTitle/tei:ref[@type='markedUpFolia']"/>
                                    <xsl:text>]</xsl:text>
                                </xsl:element>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:value-of select="$formTitle/tei:ref[@type='form-name']"/>
                                </xsl:element>
                            </xsl:otherwise>
                        </xsl:choose>
                    <xsl:element name="author" namespace="http://www.tei-c.org/ns/1.0"></xsl:element>
                    <xsl:element name="editor" namespace="http://www.tei-c.org/ns/1.0">Christoph Walther</xsl:element>
                </xsl:element>
                    <xsl:element name="editionStmt" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:choose>
                            <xsl:when test="$formTitle/tei:ref[@type='manuscript-desc']">
                                <xsl:element name="edition" namespace="http://www.tei-c.org/ns/1.0">Digitale Transkription von <xsl:value-of select="$formTitle/tei:ref[@type='manuscript-desc']"/> [<xsl:value-of select="$formTitle/tei:ref[@type='markedUpFolia']"/>]</xsl:element>
                            </xsl:when>
                            <xsl:when test="$manuscript = 'lat001'">
                                <xsl:element name="edition" namespace="http://www.tei-c.org/ns/1.0">Digitale Edition von <xsl:value-of select="$formTitle/tei:ref[@type='form-name']"/></xsl:element>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:element name="edition" namespace="http://www.tei-c.org/ns/1.0">Digitale deutsche Übersetzung von <xsl:value-of select="$formTitle/tei:ref[@type='form-name']"/></xsl:element>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">Projektleiter</xsl:element>
                            <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">eng</xsl:attribute>Principal investigator</xsl:element>
                            <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">Prof. Dr. Philippe Depreux (Universität Hamburg)</xsl:element>
                        </xsl:element>
                        <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">Editor/Übersetzer</xsl:element>
                            <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">eng</xsl:attribute>Editor/Translator</xsl:element>
                            <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">Dr. Christoph Walther (Universität Hamburg)</xsl:element>
                        </xsl:element>
                        <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">Hauptentwickler</xsl:element>
                            <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">eng</xsl:attribute>Lead developer</xsl:element>
                            <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">Dr. Matthew Munson (Universität Hamburg)</xsl:element>
                        </xsl:element>
                        <xsl:element name="sponsor" namespace="http://www.tei-c.org/ns/1.0">Akademie der Wissenschaften in Hamburg</xsl:element>
                        <xsl:element name="sponsor" namespace="http://www.tei-c.org/ns/1.0">Universität Hamburg</xsl:element>
                    </xsl:element>
                    <xsl:element name="publicationStmt" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:element name="publisher" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">mul</xsl:attribute>Formulae-Litterae-Chartae Projekt</xsl:element>
                        <xsl:element name="pubPlace" namespace="http://www.tei-c.org/ns/1.0">Hamburg</xsl:element>
                        <xsl:element name="date" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="when"><xsl:value-of select="replace(string(current-date()), '(\d+\-\d+\-\d+).*', '$1')"/></xsl:attribute><xsl:value-of select="substring-before(string(current-date()), 'Z')"/></xsl:element>
                        <xsl:element name="availability" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="licence" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:attribute name="target">https://creativecommons.org/licenses/by-nc-nd/4.0/</xsl:attribute>
                                Distributed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
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
                    <xsl:choose>
                        <xsl:when test="$formTitle/tei:ref[@type='siglum']">
                            <xsl:element name="msDesc" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="msIdentifier" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:element name="idno" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:value-of select="$formTitle/tei:ref[@type='siglum']"/>
                                    </xsl:element>
                                    <xsl:element name="msName" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:value-of select="$formTitle/tei:ref[@type='manuscript-desc']"/>
                                    </xsl:element>
                                </xsl:element>
                            </xsl:element>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">Digitales Original: mit Classical Text Editor erstellt</xsl:element>
                            <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">eng</xsl:attribute>Born Digital: created with the Classical Text Editor</xsl:element>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:element>
                </xsl:element>
                <xsl:element name="encodingDesc" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">Exportiert von <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="target">http://cte.oeaw.ac.at/</xsl:attribute>Classical Text Editor</xsl:element> als TEI-P5 Dokument. Automatische XSLT-Umwandlung ins <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="target">https://digitallatin.github.io/guidelines/</xsl:attribute>Digital-Latin-Library-Format</xsl:element> nach <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="target">http://capitains.org/pages/guidelines</xsl:attribute>CapiTainS-Vorgaben</xsl:element>.</xsl:element>
                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">eng</xsl:attribute>Exported from the <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="target">http://cte.oeaw.ac.at/</xsl:attribute>Classical Text Editor</xsl:element> as TEI-P5. Automatically transformed with XSLT to the <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="target">https://digitallatin.github.io/guidelines/</xsl:attribute>Digital Latin Library Format</xsl:element> according to the <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="target">http://capitains.org/pages/guidelines</xsl:attribute>CapiTainS Guidelines</xsl:element>.</xsl:element>
                    <xsl:element name="refsDecl" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="n">CTS</xsl:attribute>
                        <xsl:element name="cRefPattern" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:attribute name="n">formula</xsl:attribute>
                            <xsl:attribute name="matchPattern">(.+)</xsl:attribute>
                            <xsl:attribute name="replacementPattern">#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1'])</xsl:attribute>
                            <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0"><xsl:attribute name="xml:lang">eng</xsl:attribute>This pattern extracts the whole formula</xsl:element>
                        </xsl:element>
                    </xsl:element>
                </xsl:element>
            </xsl:copy>
    </xsl:template>
    
    <!-- Remove unnecessary attributes from the <text> element -->
    <xsl:template match="tei:text">
        <xsl:copy>
            <xsl:apply-templates select="node()|comment()"/>
        </xsl:copy>
    </xsl:template>
    
    <!-- Create correct attributes for the <body> element -->
    <xsl:template match="tei:body">
        <xsl:copy>
            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:choose>
                    <xsl:when test="contains($manuscript, 'deu0')">
                        <xsl:attribute name="type">translation</xsl:attribute>
                        <xsl:attribute name="xml:lang">deu</xsl:attribute>
                        <xsl:attribute name="n"><xsl:value-of select="concat($urnStart, $formNumber, '.', $manuscript)"/></xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:attribute name="type">edition</xsl:attribute>
                        <xsl:attribute name="xml:lang">lat</xsl:attribute>
                        <xsl:choose>
                            <xsl:when test="lower-case($formTitle/tei:ref[@type='siglum']) = 'fu2'">
                                <xsl:attribute name="n">
                                    <xsl:text>urn:cts:formulae:andecavensis.</xsl:text>
                                    <xsl:choose>
                                        <xsl:when test="contains($formTitle/tei:ref[@type='form-name']/text(), 'Weltzeitalter')">
                                            <xsl:text>computus</xsl:text>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:text>form</xsl:text><xsl:number value="subsequence(tokenize($formTitle/tei:ref[@type='form-name'], '\s+'), 2, 1)" format="001"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:text>.fu2</xsl:text>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:attribute name="n"><xsl:value-of select="concat($urnStart, $formNumber, '.', lower-case($manuscript))"/></xsl:attribute>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:if test="$formTitle/tei:ref[@type='folia']"><xsl:attribute name="subtype">transcription</xsl:attribute></xsl:if>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">textpart</xsl:attribute>
                    <xsl:attribute name="subtype">formula</xsl:attribute>
                    <xsl:attribute name="n">1</xsl:attribute>
                    <xsl:apply-templates select="@*|node()|comment()"/>
                </xsl:element>
            </xsl:element>
        </xsl:copy>
    </xsl:template>
    
    <!-- Surround every token in the body that is not in a <note> element with a <w> tag -->
    <xsl:template match="tei:body//*[not(ancestor-or-self::tei:note) and not(ancestor-or-self::tei:locus) and not(ancestor-or-self::tei:title)]/text()" name="tokenize">
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
                    <xsl:when test="not(matches($pString, '\w'))"><xsl:value-of select="$pString"/></xsl:when>
                    <xsl:when test="ancestor::tei:hi[contains(@rend, 'text-transform:uppercase;')]">
                        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="upper-case($pString)"/></xsl:element>
                    </xsl:when>
                    <xsl:when test="ancestor::tei:label">
                        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="upper-case($pString)"/></xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0"><xsl:value-of select="$pString"/></xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- Clean up the unnecessary attributes on the note elements. -->
    <xsl:template match="tei:note">
        <xsl:variable name="previous_get_id" select="concat('#', preceding::tei:seg[position()=1]/@xml:id)"/>
        <xsl:choose>
            <xsl:when test="@targetEnd=$previous_get_id">
                <xsl:copy>
                    <xsl:attribute name="target" select="@targetEnd"/>
                    <xsl:attribute name="type" select="@type"/>
                    <xsl:if test="@n"><xsl:attribute name="n" select="@n"/></xsl:if>
                    <xsl:apply-templates select="node()|comment()"/>
                </xsl:copy>
            </xsl:when>
            <!-- The notes without @targetEnd are the marginal notes referring to sources. -->
            <xsl:when test="not(@targetEnd)">
                <xsl:copy>
                    <xsl:attribute name="type">n1</xsl:attribute>
                    <xsl:if test="@n"><xsl:attribute name="n" select="@n"/></xsl:if>
                    <xsl:apply-templates select="node()|comment()"/>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:attribute name="targetEnd" select="@targetEnd"/>
                    <xsl:attribute name="type" select="@type"/>
                    <xsl:if test="@n"><xsl:attribute name="n" select="@n"/></xsl:if>
                    <xsl:apply-templates select="node()|comment()"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- In the CTE output, when a note element immediately follows a hi element, the hi element is repeated and encloses the note -->
    <!--<xsl:template match="tei:hi[tei:note]">
        <xsl:choose>
            <xsl:when test="contains(@rend, 'font-style:italic;') or contains(@rendition, 'bold')">
                <xsl:element name="seg" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:if test="contains(@rendition, 'bold')">
                        <xsl:attribute name="type">platzhalter</xsl:attribute>
                    </xsl:if>
                    <xsl:choose>
                        <xsl:when test="contains(@rend, 'font-style:italic;vertical-align:sub')">
                            <xsl:attribute name="rend">italic-subscript</xsl:attribute>
                        </xsl:when>
                        <xsl:when test="contains(@rend, 'font-style:italic;')">
                            <xsl:attribute name="rend">italic</xsl:attribute>
                        </xsl:when>
                    </xsl:choose>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select="node()|comment()"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>-->
    
    <!-- In the CTE output, the anchors for notes when they are footnotes appear to be repeated after the note. This should remove the following anchor -->
    <xsl:template match="tei:anchor[preceding-sibling::*[1][self::tei:note]]">
        <xsl:apply-templates select="node()|comment()"/>
    </xsl:template>
    
    <!-- Replace all <hi> elements with <seg> and transfer the @rendition attribute to @type -->
    <xsl:template match="tei:hi">
        <xsl:variable name="rends" select="string-join((@style, @rendition, @rend), ' ')"/>
        <xsl:choose>
            <!--<xsl:when test="child::*[1] = tei:note">
                <xsl:apply-templates/>
            </xsl:when>-->
            <xsl:when test="not(parent::tei:locus) and (contains($rends, 'font-style:italic;') or contains($rends, 'bold') or contains($rends, 'font-variant:small-caps;') or contains($rends, 'vertical-align:super;') or contains($rends, 'vertical-align:sub;') or contains($rends, 'text-decoration:line-through;'))">
                <xsl:element name="seg" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">
                        <xsl:if test="contains($rends, 'bold')">
                            <xsl:text>platzhalter;</xsl:text>
                        </xsl:if>
                        <xsl:if test="contains($rends, 'font-style:italic;')">
                            <xsl:choose>
                                <xsl:when test="ancestor-or-self::tei:note">
                                    <xsl:text>italic;</xsl:text>
                                </xsl:when>
                                <xsl:when test="not(contains($manuscript,'deu0'))">
                                    <xsl:text>italic;</xsl:text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>latin-word;</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:if>
                        <xsl:if test="contains($rends, 'font-variant:small-caps;')">
                            <xsl:text>small-caps;</xsl:text>
                        </xsl:if>
                        <xsl:if test="contains($rends, 'vertical-align:super;')">
                            <xsl:text>superscript;</xsl:text>
                        </xsl:if>                        
                        <xsl:if test="contains($rends, 'vertical-align:sub;')">
                            <xsl:text>subscript;</xsl:text>
                        </xsl:if>
                        <xsl:if test="contains($rends, 'font-size:smaller;')">
                            <xsl:text>smaller-text;</xsl:text>
                        </xsl:if>
                        <xsl:if test="contains($rends, 'text-decoration:line-through;')">
                            <xsl:text>line-through;</xsl:text>
                        </xsl:if>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select="node()|comment()"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="fillTypes">
        <xsl:param name="types"/>
        <xsl:param name="stringType"/>
        <xsl:choose>
            <xsl:when test="empty($types)"></xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <!-- Transform text that has the text-transform:uppercase; styling to actual uppercase letters -->
    <!--<xsl:template match="tei:hi[contains(@rend, 'text-transform:uppercase;')]/text()">
        <xsl:value-of select="upper-case(.)"/>
    </xsl:template>-->
    
    <!-- Adds the correct attributes to the formulae divs -->
    <!--<xsl:template match="tei:div">
        <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="type">textpart</xsl:attribute>
            <xsl:attribute name="subtype">formula</xsl:attribute>
            <xsl:attribute name="n">1</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>-->
    
    <xsl:template match="tei:p">
        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:space">preserve</xsl:attribute>
            <xsl:if test="not($formTitle/tei:ref[@type='folia']) and matches($manuscript, 'deu0|lat0') and current()/parent::tei:body">
                <xsl:variable name="prevPars" select="count(current()/preceding-sibling::tei:p) + 1"/>
                <xsl:variable name="thisLang" select="$formTitle/xml:lang"/>
                <xsl:variable name="transformedUrn" select="replace(concat($urnStart, $formNumber, '.', $manuscript, '-', $prevPars), ':', '-')"/>
                <xsl:attribute name="xml:id"><xsl:value-of select="$transformedUrn"/></xsl:attribute>
                <xsl:choose>
                    <xsl:when test="$thisLang = 'deu'">
                        <xsl:attribute name="corresp"><xsl:value-of select="replace($transformedUrn, $thisLang, 'lat')"/></xsl:attribute>
                    </xsl:when>
                    <xsl:when test="$thisLang = 'lat'">
                        <xsl:attribute name="corresp"><xsl:value-of select="replace($transformedUrn, $thisLang, 'deu')"/></xsl:attribute>
                    </xsl:when>
                </xsl:choose>
            </xsl:if>
            <xsl:if test="contains(@style, 'margin-left:5mm;')"><xsl:attribute name="style">subparagraph</xsl:attribute></xsl:if>
            <xsl:apply-templates select="node()|comment()"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="tei:s">
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- Removes the @rend attribute from the <mentioned> elements in the apparatus notes. -->
    <xsl:template match="tei:mentioned">
        <xsl:copy>
            <xsl:apply-templates select="node()|comment()"/>
        </xsl:copy>
    </xsl:template>
    
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
    
    <xsl:template match="tei:caption">
        <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="type">caption</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    
    <!-- DLL schema uses @rend instead of @rendition -->
    <xsl:template match="@rendition">
        <xsl:choose>
            <xsl:when test=". ='#rd-Text'"/>
            <xsl:otherwise>
                <xsl:attribute name="rend" select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- name elements are used to enclose document names in the text in CTE that we don't want to bring into the XML -->
    <xsl:template match="tei:name"/>
    
    <!-- both the title and locus elements should be ignored -->
    <xsl:template match="/tei:TEI/tei:text/tei:body/tei:div/tei:div/tei:p/tei:title" />

    <xsl:template match="/tei:TEI/tei:text/tei:body/tei:div/tei:div/tei:p/tei:locus" />
    
    <!-- Remove the xml-stylesheet declaration that CTE sometimes has -->
    <xsl:template match="processing-instruction('xml-stylesheet')"/>
    
    <xsl:template match="@*|node()|comment()">
        <xsl:copy>
            <!--<xsl:apply-templates select="./@*"/>-->
            <xsl:apply-templates select="@*|node()|comment()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>