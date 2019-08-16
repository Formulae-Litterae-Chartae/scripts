<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/"
    xmlns:cpt="http://purl.org/capitains/ns/1.0#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:output
        name="general"
        method="xml"
        encoding="UTF-8"
        indent="yes"/>
    
    <xsl:template match="/">
        
        <!-- VARIABLES: identify the tables, only a way to make the paths shorter later. -->
        <xsl:variable name="editors" select="(/tei:TEI/tei:text/tei:body/tei:table)[1]"/>
        <xsl:variable name="sourceD" select="(/tei:TEI/tei:text/tei:body/tei:table)[2]"/>
        <xsl:variable name="charters" select="(/tei:TEI/tei:text/tei:body/tei:table)[3]"/>
        <!-- VARIABLES: extracting the text used for the TextGroup name and the Work name. -->
        <xsl:variable name="textgroup">
            <xsl:choose>
                <xsl:when test="$sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Corpus']/tei:cell[position()=3]/tei:hi">
                    <!-- MATT: 'ß' should be replaced with 'ss' -->
                    <xsl:value-of select="$sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Corpus']/tei:cell[position()=3]/tei:hi/replace(replace(replace(replace(lower-case(text()),'ä','ae'),'ü','ue'),'ö','oe'),'ß','ss')"/>
                </xsl:when>
                <xsl:when test="$sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Corpus']/tei:cell[position()=3]/text()">
                    <xsl:value-of select="$sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Corpus']/tei:cell[position()=3]/replace(replace(replace(replace(lower-case(text()),'ä','ae'),'ü','ue'),'ö','oe'),'ß','ss')"/>
                </xsl:when>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="work">
            <xsl:choose>
                <xsl:when test="$sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Editor']/tei:cell[position()=3]/tei:hi">
                    <xsl:value-of select="normalize-space(($sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Editor']/tei:cell[position()=3]/tei:hi/replace(replace(replace(replace(lower-case(tokenize(text(),'\s+')[last()]),'ä','ae'),'ü','ue'),'ö','oe'),'ß','ss'))[1])"/>
                </xsl:when>
                <xsl:when test="$sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Editor']/tei:cell[position()=3]/text()">
                    <xsl:value-of select="normalize-space(($sourceD/tei:row[child::tei:cell[position()=1]/descendant::text()='Editor']/tei:cell[position()=3]/replace(replace(replace(replace(lower-case(tokenize(text(),'\s+')[last()]),'ä','ae'),'ü','ue'),'ö','oe'),'ß','ss'))[1])"/>
                </xsl:when>
            </xsl:choose>
        </xsl:variable>
        
        <xsl:result-document format="general" href="{$textgroup}.xml">
            
            <xsl:processing-instruction name="xml-model">href="https://digitallatin.github.io/guidelines/critical-editions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
            
            <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
                
                <!-- CREATING THE TEIHEADER FROM THE FIRST TWO TABLES. -->
                <xsl:element name="teiHeader" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="xml:lang">deu</xsl:attribute>
                    <xsl:element name="fileDesc" namespace="http://www.tei-c.org/ns/1.0">
                        
                        <!-- The titleStmt contains empty elements because the real files are the split version files which are to be produced with another XSLT
                            and their titles will be made from their particular Urkundennummer. As the scribes are anonym, the author element is also empty. -->
                        <xsl:element name="titleStmt" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0"/>
                            <xsl:element name="author" namespace="http://www.tei-c.org/ns/1.0"/>
                        </xsl:element>
                        
                        <!-- CREATING THE EDITION STATEMENT FROM THE FIRST TABLE -->
                        <xsl:element name="editionStmt" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="edition" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:value-of select="$sourceD/tei:row[descendant::text()='Title']/tei:cell[position()=3]/descendant::text()"/>
                                <xsl:text> (Ed. INSERT EDITOR(S) LAST NAME(S) HERE)</xsl:text>
                            </xsl:element>
                            
                            <!-- Creating the respStmt for the project director. -->
                            <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Projektleiter</xsl:text>
                                </xsl:element>
                                <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:attribute name="xml:lang">eng</xsl:attribute>
                                    <xsl:text>Principal investigator</xsl:text>
                                </xsl:element>
                                <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Prof. Dr. Philippe Depreux (Universität Hamburg)</xsl:text>
                                </xsl:element>
                            </xsl:element>
                            
                            <!-- Creating the respStmt for the correction supervisor. -->
                            <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Korrektur</xsl:text>
                                </xsl:element><xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:attribute name="xml:lang">eng</xsl:attribute>
                                    <xsl:text>Proofreading</xsl:text>
                                </xsl:element>
                                <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Franziska Quaas (Universität Hamburg)</xsl:text>
                                </xsl:element>
                            </xsl:element>
                            
                            <!-- Creating a respStmt for each Hiwi (=line) in the fisrt table (=$editors). -->
                            <xsl:for-each select="$editors/tei:row[position()>1]">
                                <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:value-of select="child::tei:cell[position()=2]"/>
                                    </xsl:element>
                                    <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:attribute name="xml:lang">eng</xsl:attribute>
                                        <xsl:value-of select="child::tei:cell[position()=3]"/>
                                    </xsl:element>
                                    <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:value-of select="child::tei:cell[position()=1]"/>
                                    </xsl:element>
                                </xsl:element>
                            </xsl:for-each>
                            
                            <!-- Creating the respStmt for the encoders. -->
                            <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Hauptentwickler</xsl:text>
                                </xsl:element><xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:attribute name="xml:lang">eng</xsl:attribute>
                                    <xsl:text>Lead developer</xsl:text>
                                </xsl:element>
                                <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Dr. Matthew Munson (Universität Hamburg)</xsl:text>
                                </xsl:element>
                            </xsl:element>
                            <xsl:element name="respStmt" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:text>Umwandlung in XML/TEI</xsl:text>
                                </xsl:element><xsl:element name="resp" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:attribute name="xml:lang">eng</xsl:attribute>
                                    <xsl:text>Conversion into XML</xsl:text>
                                </xsl:element>
                                <xsl:element name="persName" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:attribute name="xml:lang">mul</xsl:attribute>
                                    <xsl:text>Morgane Pica (Praktikantin, Ecole nationale des Chartes, Paris, Frankreich)</xsl:text>
                                </xsl:element>
                            </xsl:element>
                        </xsl:element>
                        
                        
                        
                        <!-- WRITING THE PUBLICATION STATEMENT -->
                        <xsl:element name="publicationStmt" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="publisher" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:attribute name="xml:lang">mul</xsl:attribute>
                                <xsl:text>Formulae-Litterae-Chartae Projekt</xsl:text>
                            </xsl:element>
                            <xsl:element name="pubPlace" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:text>Hamburg</xsl:text>
                            </xsl:element>
                            <xsl:element name="date" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:attribute name="when"><xsl:value-of select="year-from-date(current-date())"/></xsl:attribute>
                            </xsl:element>
                            <xsl:element name="availability" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:comment> To be filled in when a decision is made by the team. </xsl:comment>
                                </xsl:element>
                            </xsl:element>
                        </xsl:element>
                        
                        <!-- CREATING THE SOURCE DESCRIPTION FROM THE SECOND TABLE, only creating elements if the information is given in the table. -->
                        <xsl:element name="sourceDesc" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:element name="biblStruct" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="monogr" namespace="http://www.tei-c.org/ns/1.0">
                                    
                                    <!-- Book URI. -->
                                    <xsl:if test="$sourceD/tei:row[descendant::text()='DNB URI']/tei:cell[position()=3]/descendant::text()">
                                        <xsl:element name="idno" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:attribute name="type">URI</xsl:attribute>
                                            <xsl:value-of select="$sourceD/tei:row[descendant::text()='DNB URI']/tei:cell[position()=3]/descendant::text()"/>
                                        </xsl:element>
                                    </xsl:if>
                                    <!-- Book ISBN. -->
                                    <xsl:if test="$sourceD/tei:row[descendant::text()='ISBN']/tei:cell[position()=3]/descendant::text()">
                                        <xsl:element name="idno" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:attribute name="type">ISBN</xsl:attribute>
                                            <xsl:value-of select="$sourceD/tei:row[descendant::text()='ISBN']/tei:cell[position()=3]/descendant::text()"/>
                                        </xsl:element>
                                    </xsl:if>
                                    <!-- Book title. -->
                                    <xsl:if test="$sourceD/tei:row[descendant::text()='Title']/tei:cell[position()=3]/descendant::text()">
                                        <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:value-of select="$sourceD/tei:row[descendant::text()='Title']/tei:cell[position()=3]/descendant::text()"/>
                                        </xsl:element>
                                    </xsl:if>
                                    <!-- Text editors, one element for each. -->
                                    <xsl:for-each select="$sourceD/tei:row[descendant::text()='Editor' and descendant::tei:cell[position()=3]/descendant::text()]">
                                        <xsl:element name="editor" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:value-of select="current()/tei:cell[position()=3]/descendant::text()"/>
                                        </xsl:element>
                                    </xsl:for-each>
                                    
                                    <xsl:element name="imprint" namespace="http://www.tei-c.org/ns/1.0">
                                        
                                        <!-- Book publisher. -->
                                        <xsl:if test="$sourceD/tei:row[descendant::text()='Publisher']/tei:cell[position()=3]/descendant::text()">
                                            <xsl:element name="publisher" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:value-of select="$sourceD/tei:row[descendant::text()='Publisher']/tei:cell[position()=3]/descendant::text()"/>
                                            </xsl:element>
                                        </xsl:if>
                                        <!-- Publication place. -->
                                        <xsl:if test="$sourceD/tei:row[descendant::text()='Place of publication']/tei:cell[position()=3]/descendant::text()">
                                            <xsl:element name="pubPlace" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:value-of select="$sourceD/tei:row[descendant::text()='Place of publication']/tei:cell[position()=3]/descendant::text()"/>
                                            </xsl:element>
                                        </xsl:if>
                                        <!-- First print date. -->
                                        <xsl:if test="$sourceD/tei:row[descendant::text()='Originalausgabe']/tei:cell[position()=3]/descendant::text()">
                                            <xsl:element name="date" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:attribute name="when"><xsl:value-of select="$sourceD/tei:row[descendant::text()='Originalausgabe']/tei:cell[position()=3]/descendant::tei:hi"/></xsl:attribute>
                                                <xsl:attribute name="n">originalAusgabe</xsl:attribute>
                                                <xsl:value-of select="$sourceD/tei:row[descendant::text()='Originalausgabe']/tei:cell[position()=3]/descendant::text()"/>
                                            </xsl:element>
                                        </xsl:if>
                                        <!-- The digitized print. -->
                                        <xsl:if test="$sourceD/tei:row[descendant::text()='Neudrück']/tei:cell[position()=3]/descendant::text()">
                                            <xsl:element name="date" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:attribute name="when"><xsl:value-of select="$sourceD/tei:row[descendant::text()='Neudrück']/tei:cell[position()=3]/descendant::tei:hi"/></xsl:attribute>
                                                <xsl:attribute name="n">neudruck</xsl:attribute>
                                                <xsl:value-of select="$sourceD/tei:row[descendant::text()='Neudrück']/tei:cell[position()=3]/descendant::text()"/>
                                            </xsl:element>
                                        </xsl:if>
                                    </xsl:element>
                                    
                                </xsl:element>
                                
                                <xsl:if test="$sourceD/tei:row[descendant::text()='Series title']/tei:cell[position()=3]/descendant::text() or $sourceD/tei:row[descendant::text()='Series volume number']/tei:cell[position()=3]/descendant::text()">
                                    <!-- The series the book was published in. For complex series information, one element for each (=for each line). -->
                                    <xsl:element name="series" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:if test="$sourceD/tei:row[descendant::text()='Series title']/descendant::tei:cell[position()=3]/descendant::text()">
                                            <xsl:for-each select="$sourceD/tei:row[descendant::text()='Series title']">
                                                <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
                                                    <xsl:attribute name="level">s</xsl:attribute>
                                                    <xsl:value-of select="current()/tei:cell[position()=3]/descendant::text()"/>
                                                </xsl:element>
                                            </xsl:for-each>
                                        </xsl:if>
                                        <!-- Book volume number within the series. -->
                                        <xsl:if test="$sourceD/tei:row[descendant::text()='Series volume number']/tei:cell[position()=3]/descendant::text()">
                                            <xsl:element name="biblScope" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:attribute name="unit">volume</xsl:attribute>
                                                <xsl:value-of select="$sourceD/tei:row[descendant::text()='Series volume number']/tei:cell[position()=3]/descendant::text()"/>
                                            </xsl:element>
                                        </xsl:if>
                                        
                                    </xsl:element>
                                </xsl:if>
                                
                            </xsl:element>
                        </xsl:element>
                    </xsl:element>
                    
                    <xsl:element name="encodingDesc" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:text>Bei dieser Datei handelt es sich um eine OCR-bearbeitete Transkription von </xsl:text>
                            <xsl:value-of select="$sourceD/tei:row[descendant::text()='Title']/tei:cell[position()=3]/descendant::text()"/>
                            <xsl:text>, welches </xsl:text>
                            <xsl:value-of select="$sourceD/tei:row[descendant::text()='Originalausgabe']/tei:cell[position()=3]/descendant::text()"/>
                            <xsl:text> von </xsl:text>
                            <xsl:value-of select="$sourceD/tei:row[descendant::text()='Editor' and descendant::tei:cell[position()=3]/descendant::text()][1]/tei:cell[position()=3]/descendant::text()"/>
                            <xsl:text> herausgegeben worden ist. Die OCR-Texte wurden korrigiert und in gemäß TEI-P5-Vorgaben in einzelne XML-TEI-Dateien, umgewandelt. Auf dieser Grundlage und unter Einhaltung der CapiTainS-Vorgaben wurde die Formulae-Litterae-Chartae-Projektdatenbank erstellt.</xsl:text>
                            </xsl:element>
                        
                        <xsl:element name="refsDecl" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:attribute name="n">CTS</xsl:attribute>
                            <xsl:element name="cRefPattern" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:attribute name="matchPattern">(.+)</xsl:attribute>
                                <xsl:attribute name="n">charta</xsl:attribute>
                                <xsl:attribute name="replacementPattern">#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1'])</xsl:attribute>
                            </xsl:element>
                        </xsl:element>
                        
                    </xsl:element>
                </xsl:element>
                
                <!-- CREATING THE TEXT ELEMENT TO CONTAIN THE CHARTERS. -->
                <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                    <!-- Since I'm going to loop on the charters, I recreate a group element to contain the different charters as <text> elements. -->
                    <xsl:element name="group" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="xml:id">
                            <xsl:value-of select="$textgroup"/>
                        </xsl:attribute>
                        
                        <xsl:for-each select="$charters/tei:row[position()>1]">
                            <xsl:variable name="urkundennummer"><xsl:value-of select="normalize-space(child::tei:cell[position()=1]/descendant::text())"/></xsl:variable>
                            
                            <xsl:choose>
                                <!-- DO NOTHING WHEN CURRENT ROW IS ANOTHER VERSION OF PREVIOUS ROW. -->
                                <xsl:when test="current()/tei:cell[position()=1]/text()=preceding-sibling::tei:row/tei:cell[position()=1]/text()"></xsl:when>
                                
                                <!-- DO NOTHING WHEN CURRENT ROW IS ANOTHER TEXTPART OF PREVIOUS ROW. -->
                                <xsl:when test="current()/tei:cell[position()=1]/not(text())"></xsl:when>
                                
                                <!-- WHEN CURRENT ROW HAS MORE VERSIONS FOLLOWING. -->
                                <xsl:when test="current()/tei:cell[position()=1]/text()=following-sibling::tei:row/tei:cell[position()=1]/text() and current()/tei:cell[position()=1]/not(contains(text(),'**'))">
                                    
                                    <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:attribute name="type">charta</xsl:attribute>
                                        <xsl:attribute name="xml:space">preserve</xsl:attribute>
                                        <xsl:attribute name="xml:id">
                                            <xsl:value-of select="$textgroup"/><xsl:text>.</xsl:text><xsl:value-of select="normalize-space($work)"/><xsl:value-of select="format-number(number($urkundennummer),'0000')"/>
                                        </xsl:attribute>
                                        
                                        <xsl:call-template name="createFront">
                                            <xsl:with-param name="urkundennummer" select="$urkundennummer"/>
                                            <xsl:with-param name="currentNode" select="current()"/>
                                        </xsl:call-template>
                                        
                                        <xsl:element name="group" namespace="http://www.tei-c.org/ns/1.0">
                                            
                                            <!-- Create a text element for the first version (=current row). -->
                                            <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:element name="body" namespace="http://www.tei-c.org/ns/1.0">
                                                    <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                        <xsl:attribute name="type">edition</xsl:attribute>
                                                        <xsl:attribute name="xml:lang">lat</xsl:attribute>
                                                        <xsl:attribute name="n">
                                                            <xsl:text>urn:cts:formulae:</xsl:text>
                                                            <xsl:value-of select="$textgroup"/>
                                                            <xsl:text>.</xsl:text>
                                                            <xsl:value-of select="normalize-space($work)"/>
                                                            <xsl:value-of select="format-number(number($urkundennummer),'0000')"/>
                                                            <xsl:text>.lat</xsl:text>
                                                            <xsl:value-of select="format-number(count(preceding-sibling::tei:row[descendant::text()=current()/tei:cell[position()=1]/text()])+1,'000')"/>
                                                        </xsl:attribute>
                                                        
                                                        <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                            <xsl:attribute name="type">textpart</xsl:attribute>
                                                            <xsl:attribute name="subtype">charta</xsl:attribute>
                                                            <xsl:attribute name="n">1</xsl:attribute>
                                                            
                                                            <!-- Sort the paragraphs between titles and regular paragraphs. -->
                                                            <xsl:call-template name="extractText"><xsl:with-param name="currentNode" select="current()"></xsl:with-param></xsl:call-template>
                                                            
                                                        </xsl:element>
                                                    </xsl:element>
                                                </xsl:element>
                                            </xsl:element>
                                            
                                            <!-- Create a text element for each following version. -->
                                            <xsl:for-each select="following-sibling::tei:row[tei:cell[position()=1] = current()/tei:cell[position()=1]]">
                                                
                                                <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                                                    <xsl:element name="body" namespace="http://www.tei-c.org/ns/1.0">
                                                        <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                            <xsl:attribute name="type">edition</xsl:attribute>
                                                            <xsl:attribute name="xml:lang">lat</xsl:attribute>
                                                            <xsl:attribute name="n">
                                                                <xsl:text>urn:cts:formulae:</xsl:text>
                                                                <xsl:value-of select="$textgroup"/>
                                                                <xsl:text>.</xsl:text>
                                                                <xsl:value-of select="normalize-space($work)"/>
                                                                <xsl:value-of select="format-number(number($urkundennummer),'0000')"/>
                                                                <xsl:text>.lat</xsl:text>
                                                                <xsl:value-of select="format-number(count(preceding-sibling::tei:row[descendant::text()=current()/tei:cell[position()=1]/text()])+1,'000')"/>
                                                            </xsl:attribute>
                                                            
                                                            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                                <xsl:attribute name="type">textpart</xsl:attribute>
                                                                <xsl:attribute name="subtype">charta</xsl:attribute>
                                                                <xsl:attribute name="n">1</xsl:attribute>
                                                                
                                                                <!--<xsl:for-each select="current()/child::tei:cell[position()=6]/*">
                                                                    <xsl:choose>
                                                                    <xsl:when test="self::tei:p">
                                                                    <xsl:choose>
                                                                    <xsl:when test="self::tei:p[contains(.,'***')]">
                                                                    <xsl:element name="head" namespace="http://www.tei-c.org/ns/1.0">
                                                                    <xsl:copy select="replace(self::tei:p[contains(text(),'***')]/text(),'\*','')"/>
                                                                    </xsl:element>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>
                                                                    <xsl:copy-of select="self::tei:p"/>
                                                                    </xsl:otherwise>
                                                                    </xsl:choose>
                                                                    </xsl:when>
                                                                    <xsl:when test="not(self::tei:p)">
                                                                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                                                                    <xsl:value-of select="parent::tei:cell"/>
                                                                    </xsl:element>
                                                                    </xsl:when>
                                                                    </xsl:choose>
                                                                    </xsl:for-each>-->
                                                                
                                                                <!-- Sort the paragraphs between titles and regular paragraphs. -->
                                                                <xsl:call-template name="extractText"><xsl:with-param name="currentNode" select="current()"></xsl:with-param></xsl:call-template>
                                                                
                                                                <!--<xsl:choose>
                                                                    <xsl:when test="child::tei:cell[position()=6]/tei:p">
                                                                    <xsl:choose>
                                                                    <xsl:when test="child::tei:cell[position()=6]/tei:p[contains(text(),'***')]">
                                                                    <xsl:element name="head" namespace="http://www.tei-c.org/ns/1.0">
                                                                    <xsl:copy select="replace(child::tei:cell[position()=6]/tei:p[contains(text(),'***')]/text(),'\*','')"/>
                                                                    </xsl:element>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>
                                                                    <xsl:copy-of select="child::tei:cell[position()=6]/*"/>
                                                                    </xsl:otherwise>
                                                                    </xsl:choose>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>
                                                                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                                                                    <xsl:value-of select="child::tei:cell[position()=6]"/>
                                                                    </xsl:element>
                                                                    </xsl:otherwise>
                                                                    </xsl:choose>-->
                                                                
                                                            </xsl:element>
                                                        </xsl:element>
                                                    </xsl:element>
                                                </xsl:element>
                                            </xsl:for-each>
                                        </xsl:element>
                                    </xsl:element>
                                </xsl:when>
                                
                                <!-- WHEN CURRENT ROW HAS MORE TEXTPARTS FOLLOWING. -->
                                <xsl:when test="current()/tei:cell[position()=1]/text()=following-sibling::tei:row/tei:cell[position()=1]/text() and current()/tei:cell[position()=1]/contains(text(),'**')">
                                    <xsl:variable name="charter-number"><xsl:value-of select="format-number(number(normalize-space(replace(current()/tei:cell[position()=1]/descendant::text(), '\*+', ''))),'0000')"/></xsl:variable>
                                    <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:attribute name="type">charta</xsl:attribute>
                                        <xsl:attribute name="xml:space">preserve</xsl:attribute>
                                        <xsl:attribute name="xml:id">
                                            <xsl:value-of select="$textgroup"/><xsl:text>.</xsl:text><xsl:value-of select="normalize-space($work)"/>
                                            <xsl:value-of select="$charter-number"/>
                                        </xsl:attribute>
                                        
                                        <xsl:call-template name="createFront">
                                            <xsl:with-param name="urkundennummer" select="number($charter-number)"/>
                                            <xsl:with-param name="currentNode" select="current()"/>
                                        </xsl:call-template>
                                        
                                        <xsl:element name="body" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:attribute name="type">edition</xsl:attribute>
                                                <xsl:attribute name="xml:lang">lat</xsl:attribute>
                                                <xsl:attribute name="n">
                                                    <xsl:text>urn:cts:formulae:</xsl:text>
                                                    <xsl:value-of select="$textgroup"/>
                                                    <xsl:text>.</xsl:text>
                                                    <xsl:value-of select="normalize-space($work)"/>
                                                    <xsl:value-of select="$charter-number"/>
                                                    <xsl:text>.lat001</xsl:text>
                                                </xsl:attribute>
                                                
                                                <!-- Create a textpart for the first part (=current row). -->
                                                <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                    <xsl:attribute name="type">textpart</xsl:attribute>
                                                    <xsl:attribute name="subtype">charta</xsl:attribute>
                                                    <xsl:attribute name="n">1</xsl:attribute>
                                                    
                                                    <!-- TEXT = sixth column (=sixth cell in row). -->
                                                    <xsl:call-template name="extractText"><xsl:with-param name="currentNode" select="current()"></xsl:with-param></xsl:call-template>
                                                </xsl:element>
                                                
                                                <!-- Create a textpart for each following one. -->
                                                <xsl:for-each select="following-sibling::tei:row[tei:cell[position()=1]/text() = current()/tei:cell[position()=1]/text() and following-sibling::tei:row[tei:cell[position()=1 and text()]]/position() > current()/position()]">
<!--                                                    <xsl:if test="following-sibling::tei:row[tei:cell[position()=1 and text()]]/position() > current()/position()">-->
                                                        <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                        <xsl:attribute name="type">textpart</xsl:attribute>
                                                        <xsl:attribute name="subtype">charta</xsl:attribute>
                                                        <xsl:attribute name="n">
                                                            <xsl:value-of select="count(preceding-sibling::tei:row[tei:cell[position()=1]/text() = current()/tei:cell[position()=1]/text()])+1"/>
                                                        </xsl:attribute>
                                                        
                                                        <xsl:call-template name="extractText"><xsl:with-param name="currentNode" select="current()"></xsl:with-param></xsl:call-template>
                                                        
                                                    </xsl:element>
                                                    <!--</xsl:if>-->
                                                </xsl:for-each>
                                                
                                            </xsl:element>
                                        </xsl:element>
                                    </xsl:element>
                                </xsl:when>
                                
                                <!-- WHEN CURRENT ROW IS THE ONLY VERSION AND TEXTPART OF THE TEXT. -->
                                <xsl:otherwise>
                                    
                                    <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:attribute name="type">charta</xsl:attribute>
                                        <xsl:attribute name="xml:space">preserve</xsl:attribute>
                                        <xsl:attribute name="xml:id">
                                            <xsl:value-of select="$textgroup"/><xsl:text>.</xsl:text><xsl:value-of select="normalize-space($work)"/>
                                            <xsl:value-of select="format-number(number(replace($urkundennummer, '\D', '')),'0000')"/><xsl:value-of select="replace($urkundennummer, '\d', '')"/>
                                        </xsl:attribute>
                                        
                                        <xsl:call-template name="createFront">
                                            <xsl:with-param name="urkundennummer" select="$urkundennummer"/>
                                            <xsl:with-param name="currentNode" select="current()"/>
                                        </xsl:call-template>
                                        
                                        <xsl:element name="body" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                <xsl:attribute name="type">edition</xsl:attribute>
                                                <xsl:attribute name="xml:lang">lat</xsl:attribute>
                                                <xsl:attribute name="n">
                                                    <xsl:text>urn:cts:formulae:</xsl:text>
                                                    <xsl:value-of select="$textgroup"/>
                                                    <xsl:text>.</xsl:text>
                                                    <xsl:value-of select="normalize-space($work)"/>
                                                    <xsl:value-of select="format-number(number(replace($urkundennummer, '\D', '')),'0000')"/><xsl:value-of select="replace($urkundennummer, '\d', '')"/>
                                                    <xsl:text>.lat001</xsl:text>
                                                </xsl:attribute>
                                                
                                                <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                                                    <xsl:attribute name="type">textpart</xsl:attribute>
                                                    <xsl:attribute name="subtype">charta</xsl:attribute>
                                                    <xsl:attribute name="n">1</xsl:attribute>
                                                    
                                                    <!-- TEXT = sixth column (=sixth cell in row). -->
                                                    
                                                    <!--<xsl:for-each select="current()/child::tei:cell[position()=6]/*">
                                                        <xsl:choose>
                                                        <xsl:when test="self::tei:p">
                                                        <xsl:choose>
                                                        <xsl:when test="self::tei:p[contains(.,'***')]">
                                                        <xsl:element name="head" namespace="http://www.tei-c.org/ns/1.0">
                                                        <xsl:copy select="replace(self::tei:p[contains(text(),'***')]/text(),'\*','')"/>
                                                        </xsl:element>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                        <xsl:copy-of select="self::tei:p"/>
                                                        </xsl:otherwise>
                                                        </xsl:choose>
                                                        </xsl:when>
                                                        <xsl:when test="not(self::tei:p)">
                                                        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                                                        <xsl:value-of select="parent::tei:cell"/>
                                                        </xsl:element>
                                                        </xsl:when>
                                                        </xsl:choose>
                                                        </xsl:for-each>-->
                                                    
                                                    <xsl:call-template name="extractText"><xsl:with-param name="currentNode" select="current()"></xsl:with-param></xsl:call-template>
                                                    
                                                    <!--<xsl:choose>
                                                        <xsl:when test="child::tei:cell[position()=6]/tei:p[contains(text(),'***')]">
                                                        <xsl:choose>
                                                        <xsl:when test="child::tei:cell[position()=6]/tei:p[contains(text(),'***')]">
                                                        <xsl:element name="head">
                                                        <xsl:copy select="child::tei:cell[position()=6]/tei:p[contains(text(),'***')]/replace(.,'\*','')"/>
                                                        </xsl:element>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                        <xsl:copy-of select="child::tei:cell[position()=6]/*"/>
                                                        </xsl:otherwise>
                                                        </xsl:choose>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                                                        <xsl:value-of select="child::tei:cell[position()=6]"/>
                                                        </xsl:element>
                                                        </xsl:otherwise>
                                                        </xsl:choose>-->
                                                </xsl:element>
                                            </xsl:element>
                                        </xsl:element>
                                        
                                    </xsl:element>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                        
                    </xsl:element>
                </xsl:element>
            </xsl:element>
            
        </xsl:result-document>
        
    </xsl:template>
    
    <xsl:template name="createFront">
        <xsl:param name="urkundennummer"/>
        <xsl:param name="currentNode"/>
        <xsl:element name="front" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:lang">deu</xsl:attribute>
            
            <!-- URKUNDENNUMMER = first column (first cell in row). -->
            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="type">section</xsl:attribute>
                <xsl:attribute name="subtype">urkundennummer</xsl:attribute>
                <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:value-of select="$urkundennummer"/>
                </xsl:element>
            </xsl:element>
            <!-- SEITEN = second column (second cell in row). -->
            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="type">section</xsl:attribute>
                <xsl:attribute name="subtype">seiten</xsl:attribute>
                <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:value-of select="$currentNode/child::tei:cell[position()=2]"/>
                </xsl:element>
            </xsl:element>
            <!-- REGEST = third column (third cell in row). -->
            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="type">section</xsl:attribute>
                <xsl:attribute name="subtype">regest</xsl:attribute>
                <xsl:if test="$currentNode/child::tei:cell[position()=3]/not(tei:p)">
                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:value-of select="$currentNode/child::tei:cell[position()=3]"/>
                    </xsl:element>
                </xsl:if>
                <xsl:if test="$currentNode/child::tei:cell[position()=3]/tei:p">
                    <xsl:for-each select="$currentNode/child::tei:cell[position()=3]/tei:p">
                        <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:value-of select="node()"/>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:if>
            </xsl:element>
            <!-- AUSTELLUNGSORT = fourth column (fourth cell in row). -->
            <xsl:if test="$currentNode/child::tei:cell[position()=4]/text()">
                <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">section</xsl:attribute>
                    <xsl:attribute name="subtype">ausstellungsort</xsl:attribute>
                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:value-of select="$currentNode/child::tei:cell[position()=4]"/>
                    </xsl:element>
                </xsl:element>
            </xsl:if>
            <!-- DATES = fifth column (fifth cell in row). -->
            <xsl:call-template name="addDateline">
                <xsl:with-param name="currentElement" select="$currentNode"/>
            </xsl:call-template>
            <!-- Echtheit = the seventh column (seventh cell in a row). Not all collections will have this. -->
            <xsl:if test="$currentNode/child::tei:cell[position()=7]//text()">
                <xsl:element name="note" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="type">echtheit</xsl:attribute>
                    <xsl:value-of select="$currentNode/child::tei:cell[position()=7]"/>
                </xsl:element>
            </xsl:if>
            
        </xsl:element>
    </xsl:template>
    
    <xsl:template name="addDateline">
        <xsl:param name="currentElement"/>
        <xsl:element name="dateline" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:variable name="datestring"><xsl:value-of select="$currentElement/child::tei:cell[position()=5]"/></xsl:variable>
            <xsl:value-of select="$datestring"/>
            <xsl:element name="date" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:if test="matches($datestring, '^\d{3,4}[\- ]\d{1,2}[\- ]\d{1,2}$')">
                    <xsl:attribute name="when"><xsl:number value="tokenize($datestring, '[ \-]')[1]" format="0001"/><xsl:text>-</xsl:text>
                        <xsl:number value="tokenize($datestring, '[ \-]')[2]" format="01"/><xsl:text>-</xsl:text>
                        <xsl:number value="tokenize($datestring, '[ \-]')[3]" format="01"/></xsl:attribute>
                </xsl:if>
            </xsl:element>
        </xsl:element>
    </xsl:template>
    
    <xsl:template name="extractText">
        <xsl:param name="currentNode"/>
        <xsl:for-each select="$currentNode/child::tei:cell[position()=6]//text()">
            <xsl:choose>
                <xsl:when test=".[contains(.,'***')]">
                    <xsl:element name="head" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="xml:space">preserve</xsl:attribute>
                        <xsl:value-of select="replace(.,'\*','')"/>
                    </xsl:element>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:element name="p" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="xml:space">preserve</xsl:attribute>
                        <xsl:value-of select="."/>
                    </xsl:element>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each> 
    </xsl:template>
    
</xsl:stylesheet>