<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:ti="http://chs.harvard.edu/xmlns/cts"
    xmlns:dct="http://purl.org/dc/terms/" 
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns="http://purl.org/capitains/ns/1.0#"
    xmlns:owl="http://www.w3.org/2002/07/owl#" 
    xmlns:bib="http://bibliotek-o.org/1.0/ontology/"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:template match="/">
        <xsl:param name="folderName"><xsl:value-of select="replace(base-uri(), tokenize(base-uri(), '/')[last()], '')"/></xsl:param>
        <xsl:param name="urn" select="tokenize(/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
        <xsl:param name="title">
            <xsl:copy-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/>
        </xsl:param>
        <xsl:param name="parentUrn">
            <xsl:choose>
                <xsl:when test="matches(string-join($urn, '.'), 'andecavensis.form\d\d\d.fu2|andecavensis.computus.fu2')">
                    <xsl:text>urn:cts:formulae:fu2.</xsl:text><xsl:value-of select="normalize-space(replace(substring-before(substring-after($title, '['), ']'), 'fol\.\s*|-', ''))"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat($urn[1], '.', $urn[2])"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="pubLang">
            <xsl:choose>
                <xsl:when test="/tei:TEI/tei:text/tei:front[@xml:lang]">
                    <xsl:value-of select="/tei:TEI/tei:text/tei:front/@xml:lang"/>
                </xsl:when>
                <xsl:otherwise>deu</xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="short-regest">
            <xsl:value-of select="document(concat(replace($folderName, '/data/.*', '/regesten/'), $urn[1], '_regesten.xml'))/xml/regest[@docId=concat($urn[1], '.', $urn[2])]/shortDesc/text()"/>
        </xsl:param>
        <xsl:param name="long-regest">
            <xsl:choose>
                <xsl:when test="matches(string-join($urn, '.'), 'andecavensis|marculf')">
                    <xsl:value-of select="document(concat(replace($folderName, '/data/.*', '/regesten/'), $urn[1], '_regesten.xml'))/xml/regest[@docId=concat($urn[1], '.', $urn[2])]/longDesc/text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="/tei:TEI/tei:text/tei:front/tei:div[@subtype='regest']//text()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:processing-instruction name="xml-model">href="../../../capitains.rng" schematypens="http://relaxng.org/ns/structure/1.0"</xsl:processing-instruction>
        <collection>
            <identifier><xsl:value-of select="$parentUrn"/></identifier>
            <parent><xsl:value-of select="tokenize($parentUrn, '\.')[1]"/></parent>
            <dc:title>
                <xsl:attribute name="xml:lang"><xsl:value-of select="$pubLang"/></xsl:attribute>
                <xsl:value-of select="$title"/>
            </dc:title>
            <dc:type>cts:work</dc:type>
            <members>
                <xsl:for-each select="collection(concat($folderName, '?select=*.xml;on-error=ignore'))">
                    <xsl:if test="not(matches(document-uri(.), '__capitains__|__cts__'))">
                        <xsl:choose>
                            <xsl:when test="substring-before(tokenize(document-uri(.), '/')[last()], '.') != tokenize(tokenize($parentUrn, '\.')[1], ':')[last()]">
                                <xsl:variable name="childUrn" select="tokenize(tokenize(document-uri(.), '/')[last()], '\.')"/>
                                <xsl:element name="collection" namespace="http://purl.org/capitains/ns/1.0#">
                                    <xsl:attribute name="path">
                                        <xsl:text>../../</xsl:text>
                                        <xsl:value-of select="$childUrn[1]"/>
                                        <xsl:text>/</xsl:text>
                                        <xsl:value-of select="$childUrn[2]"/>
                                        <xsl:text>/__capitains__.xml</xsl:text>
                                    </xsl:attribute>
                                    <xsl:attribute name="identifier">
                                        <xsl:text>urn:cts:formulae:</xsl:text>
                                        <xsl:value-of select="$childUrn[1]"/>
                                        <xsl:text>.</xsl:text>
                                        <xsl:value-of select="$childUrn[2]"/>
                                    </xsl:attribute>
                                </xsl:element>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:call-template name="createCTS">
                                    <xsl:with-param name="textURI"><xsl:value-of select="document-uri(.)"/></xsl:with-param>
                                    <xsl:with-param name="pubLang"><xsl:value-of select="$pubLang"/></xsl:with-param>
                                    <xsl:with-param name="parentUrn"><xsl:value-of select="$parentUrn"/></xsl:with-param>
                                    <xsl:with-param name="shortRegest"><xsl:value-of select="$short-regest"/></xsl:with-param>
                                    <xsl:with-param name="longRegest"><xsl:value-of select="$long-regest"/></xsl:with-param>
                                </xsl:call-template>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:if>
                </xsl:for-each>
            </members>
        </collection>
    </xsl:template>
    
    <xsl:template name="createCTS">
        <xsl:param name="textURI"/>
        <xsl:param name="pubLang"/>
        <xsl:param name="parentUrn"/>
        <xsl:param name="longRegest"/>
        <xsl:param name="shortRegest"/>
        <xsl:param name="textFile" select="document($textURI)"/>
        <xsl:param name="urn" select="tokenize($textFile/tei:TEI/tei:text/tei:body/tei:div/@n, '\.')"/>
        <xsl:param name="lang" select="$textFile/tei:TEI/tei:text/tei:body/tei:div/@xml:lang"/>
        <xsl:param name="title">
            <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/>
        </xsl:param>
        <xsl:param name="isManuscript"><xsl:value-of select="boolean($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc)"/></xsl:param>
        <xsl:param name="docSource">
            <xsl:choose>
                <xsl:when test="$isManuscript = true()">
                    <xsl:value-of select="replace($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:idno, '\d+', '')"/>
                    <xsl:text>&lt;span class="manuscript-number"&gt;</xsl:text>
                    <xsl:value-of select="replace($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:idno, '\D+', '')"/>
                    <xsl:text>&lt;/span&gt; (</xsl:text>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:msDesc/tei:msIdentifier/tei:msName"/>
                    <xsl:text>)</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>Formulae - Litterae - Chartae Projekt, Hamburg</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="markedUpTitle">
            <xsl:choose>
                <xsl:when test="$isManuscript = true()">
                    <xsl:value-of select="$title"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="string-join($title//text(), '')"/>
                    <xsl:if test="matches($textURI, 'andecavensis|marculf')">
                        <xsl:text> (</xsl:text>
                        <xsl:value-of select="$lang"/>
                        <xsl:text>)</xsl:text>
                    </xsl:if>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        
        <xsl:param name="dateCopyrighted">
            <xsl:choose>
                <xsl:when test="matches($textURI, 'andecavensis|marculf') or $isManuscript = true()">
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/@when"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date/@when"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="allEds">
            <xsl:choose>
                <xsl:when test="matches($textURI, 'andecavensis|marculf') or $isManuscript = true()">
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:editor/text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:editor/text()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="bibliographicCitation">
            <xsl:choose>
                <xsl:when test="matches($textURI, 'andecavensis|marculf') or $isManuscript = true()">
                    <xsl:value-of select="$markedUpTitle"/>
                    <xsl:text>, </xsl:text>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:publisher/text()"/><xsl:text>. </xsl:text>
                    <xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:pubPlace/text()"/><xsl:text> </xsl:text>
                    <xsl:value-of select="$dateCopyrighted"/>
                    <xsl:text>, [URL: https://werkstatt.formulae.uni-hamburg.de/texts/</xsl:text><xsl:value-of select="string-join($urn, '.')"/><xsl:text>/passage/all]</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:variable name="editorStr">
                        <xsl:for-each select="$allEds">
                            <xsl:choose>
                                <xsl:when test="contains(., ',')">
                                    <xsl:value-of select="substring-after(., ', ')"/><xsl:text> </xsl:text><xsl:value-of select="substring-before(., ', ')"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="."/>
                                </xsl:otherwise>
                            </xsl:choose>
                            <xsl:if test="count($allEds) > 1 and count($allEds) != index-of($allEds, .)">
                                <xsl:choose>
                                    <xsl:when test="index-of($allEds, .) != count($allEds) - 1">
                                        <xsl:text>, </xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:text> und </xsl:text>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:if>
                        </xsl:for-each>
                    </xsl:variable>
                    <xsl:value-of select="replace($title, ' +\(.*\)', '')"/><xsl:text>, in: </xsl:text><xsl:value-of select="$editorStr"/><xsl:text>, </xsl:text>
                    <xsl:value-of select="string-join($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:title/text(), ': ')"/>
                    <xsl:if test="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']">
                        <xsl:text> Bd. </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='volume']/text()"/>
                    </xsl:if>
                    <xsl:text>, </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:pubPlace/text()"/>
                    <xsl:text> </xsl:text><xsl:value-of select="$dateCopyrighted"/>
                    <xsl:if test="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']">
                        <xsl:text>, [URI: </xsl:text><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type='URI']/text()"/><xsl:text>]</xsl:text>
                    </xsl:if>
                    <xsl:text>, S. </xsl:text>
                    <xsl:value-of select="normalize-space($textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:biblScope[@unit='pp']/text())"/>
                    <xsl:text>.</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:param>
        <xsl:param name="metadata">
            <dc:language><xsl:value-of select="$lang"/></dc:language>
            <dc:type>
                <xsl:choose>
                    <xsl:when test="$isManuscript = true()">transcription</xsl:when>
                    <xsl:when test="$lang = 'lat'">cts:edition</xsl:when>
                    <xsl:otherwise>cts:translation</xsl:otherwise>
                </xsl:choose>
            </dc:type>
            <xsl:for-each select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:editionStmt/tei:respStmt/tei:persName/text()">
                <dc:contributor><xsl:value-of select="."/></dc:contributor>
            </xsl:for-each>
            <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae Projekt</dc:publisher>
            <dc:format>application/tei+xml</dc:format>
            <dc:source>
                <xsl:choose>
                    <xsl:when test="matches($textURI, 'andecavensis|marculf')">
                        <xsl:value-of select="$docSource"/>
                    </xsl:when>
                    <xsl:when test="$isManuscript = true()">
                        <xsl:value-of select="$title"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$bibliographicCitation"/>
                    </xsl:otherwise>
                </xsl:choose>
            </dc:source>
            <dc:description>
                <xsl:attribute name="xml:lang"><xsl:value-of select="$pubLang"/></xsl:attribute>
                <xsl:value-of select="$longRegest"/>
            </dc:description>
            
            <structured-metadata>
                <xsl:for-each select="$allEds">
                    <bib:editor><xsl:value-of select="."/></bib:editor>
                </xsl:for-each>
                <xsl:choose>
                    <xsl:when test="not(matches($textURI, 'andecavensis|marculf') or $isManuscript = true())">
                        <dct:dateCopyrighted><xsl:value-of select="$dateCopyrighted"/></dct:dateCopyrighted>
                        <dct:created><xsl:value-of select="$textFile/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date/text()"/></dct:created>
                    </xsl:when>
                    <xsl:otherwise>
                        <dct:created><xsl:value-of select="$dateCopyrighted"/></dct:created>
                    </xsl:otherwise>
                </xsl:choose>
                <dct:bibliographicCitation><xsl:value-of select="$bibliographicCitation"/></dct:bibliographicCitation>
                <dct:abstract>
                    <xsl:attribute name="xml:lang"><xsl:value-of select="$pubLang"/></xsl:attribute>
                    <xsl:value-of select="$shortRegest"/>
                </dct:abstract>
            </structured-metadata>
        </xsl:param>
        
        <collection>
            <xsl:attribute name="readable">true</xsl:attribute>
            <xsl:attribute name="path"><xsl:text>./</xsl:text><xsl:value-of select="tokenize($textURI, '/')[last()]"/></xsl:attribute>
            <identifier><xsl:value-of select="string-join($urn, '.')"/></identifier>
            <parent><xsl:value-of select="$parentUrn"/></parent>
            <dc:title>
                <xsl:attribute name="xml:lang"><xsl:value-of select="$pubLang"/></xsl:attribute>
                <xsl:value-of select="$markedUpTitle"/>
            </dc:title>
            <xsl:copy-of select="$metadata"/>
        </collection>
            
        
    </xsl:template>
    
</xsl:stylesheet>