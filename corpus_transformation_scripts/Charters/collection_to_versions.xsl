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
    
    <!-- MAIN TEMPLATE -->
    <xsl:template match="/">
        <xsl:for-each select="/tei:TEI/tei:text/tei:group/tei:text/descendant::tei:div[@type='edition']">
            <xsl:variable name="edition" select="."/>
            <!-- The new documents will use the parameters of the xsl:output element. Each charter version file will be given the name of its @n value
                (location . ch.number . language + vs.number)
                and put into a folder named after the charter @xml:id (location . ch.number)
                (therefore if several versions of one charter exist, there will be several version files within one charter folder),
                which implies that the "Passau adding xmlid.xsl" transformation was already applied.
                Then comes the Digital Latin Library declaration.-->
            <xsl:result-document format="general" href="data/{ancestor::tei:group[@xml:id]/@xml:id}/{ancestor::tei:text[@xml:id]/substring-after(@xml:id,'.')}/{substring-after(@n,'ae:')}.xml" validation="strip">
                <xsl:processing-instruction name="xml-model">href="https://digitallatin.github.io/guidelines/critical-editions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
                                
                <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:element name="teiHeader" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="xml:lang">deu</xsl:attribute>
                        <xsl:element name="fileDesc" namespace="http://www.tei-c.org/ns/1.0">
                            
                            <!-- Creating the titleStmt so that each file has its Urkundennummer as a title. Since the charters are anonym, we need no other metadata in the titleStmt. -->
                            <xsl:element name="titleStmt" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="title" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/><xsl:text> Nr. </xsl:text><xsl:value-of select="node()/ancestor::tei:text[@xml:id]/tei:front/tei:div[@subtype='urkundennummer']"/>
                                </xsl:element>
                            </xsl:element>
                            
                            <!-- Identically copying the rest of the fileDesc except the titleStmt (which was just remade) and the sourceDesc (which needs to be completed). -->
                            <xsl:choose>
                                <xsl:when test="count(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:availability/tei:licence) = 1">
                                    <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/*[not(self::tei:titleStmt) and not(self::tei:sourceDesc)]"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/*[not(self::tei:titleStmt) and not(self::tei:sourceDesc) and not(self::tei:publicationStmt)]"/>
                                    <xsl:element name="publicationStmt" namespace="http://www.tei-c.org/ns/1.0">
                                        <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:publisher"/>
                                        <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:pubPlace"/>
                                        <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date"/>
                                        <xsl:element name="availability" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:for-each select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:availability/tei:licence">
                                                <xsl:element name="licence" namespace="http://www.tei-c.org/ns/1.0">
                                                    <xsl:choose>
                                                        <xsl:when test="starts-with(./@corresp, 'urn')">
                                                            <xsl:attribute name="corresp"><xsl:value-of select="$edition/@n"/></xsl:attribute>
                                                            <xsl:attribute name="target"><xsl:value-of select="./@target"/></xsl:attribute>
                                                            <xsl:value-of select="./text()"/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:attribute name="corresp"><xsl:text>#</xsl:text><xsl:copy-of select="$edition/ancestor::tei:text/@xml:id"/><xsl:value-of select="@corresp"/></xsl:attribute>
                                                            <xsl:value-of select="./text()"/>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </xsl:element>
                                            </xsl:for-each>
                                        </xsl:element>
                                    </xsl:element>
                                </xsl:otherwise>
                            </xsl:choose>
                            
                            <!-- Creating the sourceDesc. -->
                            <xsl:element name="sourceDesc" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:element name="biblStruct" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:element name="monogr" namespace="http://www.tei-c.org/ns/1.0">
                                        
                                        <!-- Copying the contents of the <monogr> element except the one to which I need another element added). -->
                                        <xsl:apply-templates select="/tei:TEI/tei:teiHeader/descendant::tei:monogr/*[not(self::tei:imprint)]"/>
                                        
                                        <xsl:element name="imprint" namespace="http://www.tei-c.org/ns/1.0">
                                            <xsl:apply-templates select="/tei:TEI/tei:teiHeader/descendant::tei:imprint/*"/>
                                            
                                            <!-- Fishing another information from the <front> element of whichever particular <text> the <xsl:for-each>
                                                element is currently focusing on and storing it in a parameter. -->
                                            <xsl:call-template name="seiten">
                                                <xsl:with-param name="snb">
                                                    <xsl:value-of select="node()/ancestor::tei:text[@xml:id]/descendant::tei:div[@subtype='seiten']"/>
                                                </xsl:with-param>
                                            </xsl:call-template>
                                            
                                        </xsl:element>
                                    </xsl:element>
                                    
                                    <!-- Copying what is left of the <biblStruct> element. -->
                                    <xsl:copy-of select="/tei:TEI/tei:teiHeader/descendant::tei:series"/>
                                    
                                </xsl:element>
                            </xsl:element>
                        </xsl:element>
                        
                        <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:encodingDesc"/>
                        
                    </xsl:element>
                    
                    <!-- Copy of the particular <text> element currently targetted by xsl:for-each). -->
                    <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="type">charta</xsl:attribute>    
                        <xsl:attribute name="xml:id"><xsl:copy-of select="node()/ancestor::tei:text/@xml:id"/></xsl:attribute>
                        
                        <!-- Copy of all possible parts of the tagetted <front> element which weren't moved into the teiHeader. -->
                        <xsl:element name="front" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:attribute name="xml:lang">deu</xsl:attribute>
                            <xsl:copy-of select="node()/ancestor::tei:text[@xml:id]/descendant::tei:div[@subtype='regest']"/>
                            <xsl:copy-of select="node()/ancestor::tei:text[@xml:id]/descendant::tei:div[@subtype='ausstellungsort']"/>
                            <xsl:copy-of select="node()/ancestor::tei:text[@xml:id]/descendant::tei:dateline"/>
                            <xsl:copy-of select="node()/ancestor::tei:text[@xml:id]/descendant::tei:note[@type='echtheit']"/>
                        </xsl:element>
                        
                        <!-- Copy of the rest of the current <body> target. -->
                        <xsl:copy-of select="node()/ancestor::tei:body"/>
                        
                    </xsl:element>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>
        
    </xsl:template>
    
    
    <!-- Template referred to when adding the page information to the sourceDesc. -->
    <xsl:template name="seiten">
        <xsl:param name="snb"/>
        <xsl:element name="biblScope" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="unit">pp</xsl:attribute>
            <xsl:value-of select="$snb"/>
        </xsl:element>
    </xsl:template>
    
    <!-- Template allowing copy of the <monogr> element (teiHeader/fileDesc/sourceDesc/biblStruct/monogr)
        except the <imprint> element inside which we want to add an element. -->
    <xsl:template match="/tei:TEI/tei:teiHeader/descendant::tei:monogr/*[not(self::tei:imprint)]">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()|text()"/>
        </xsl:copy>
    </xsl:template>
    
    <!-- Template copying the contents of the <imprint> element (teiHeader/fileDesc/sourceDesc/biblStruct/monogr/imprint) -->
    <xsl:template match="/tei:TEI/tei:teiHeader/descendant::tei:imprint/*">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()|text()"/>
        </xsl:copy>
    </xsl:template>
    
    <!-- Template allowing copy of the insides of targetted nodes. -->
    <xsl:template match="@*|node()|text()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()|text()"/>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>