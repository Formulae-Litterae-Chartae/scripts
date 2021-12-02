<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:t="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs t"
    version="2.0">
    
    <xsl:template name="buildBibEntry">
        <xsl:param name="entry"/>
        <xsl:choose>
            <xsl:when test="$entry[@type='book' or @type='phdthesis']">
                <!-- Skip "Der Neue Pauly" as a book -->
                <xsl:if test="$entry/t:monogr/t:title[1]/text() != 'Der neue Pauly (Onlineversion)'">
                    <!-- THE AUTHOR(S) -->
                    <xsl:choose>
                        <xsl:when test="$entry/t:monogr/t:author">
                            <xsl:call-template name="makeAuthors">
                                <xsl:with-param name="pubElement" select="$entry/t:monogr/t:author"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:call-template name="makeAuthors">
                                <xsl:with-param name="pubElement" select="$entry/t:monogr/t:editor"/>
                            </xsl:call-template>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:if test="$entry/t:monogr/t:author or $entry/t:monogr/t:editor">
                        <xsl:text>: </xsl:text>
                    </xsl:if>
                    <!-- THE TITLE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">bookTitle</xsl:attribute>
                        <xsl:value-of select="normalize-space($entry/t:monogr/t:title[not(@type='short')])"/>
                    </xsl:element>
                    <xsl:text>, </xsl:text>
                    <!-- THE EDITION -->
                    <xsl:if test="$entry/t:monogr/t:edition">
                        <xsl:element name="span">
                            <xsl:attribute name="class">bookEdition</xsl:attribute>
                            <xsl:variable name="edition" select="$entry/t:monogr/t:edition"/>
                            <xsl:choose>
                                <xsl:when test="matches($edition, '^\d+$')">
                                    <xsl:value-of select="$edition"/><xsl:text>. Aufl.</xsl:text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="$edition"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:element>
                        <xsl:text>, </xsl:text>
                    </xsl:if>
                    <!-- THE PLACE OF PUBLICATION -->
                    <xsl:call-template name="makePubPlace">
                        <xsl:with-param name="pubElement" select="$entry"/>
                    </xsl:call-template>
                    <!-- THE PUBLICATION DATE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">publicationYear</xsl:attribute>
                        <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='publicationDate']"/>
                    </xsl:element>
                    <!-- THE PUBLICATION SERIES -->
                    <xsl:call-template name="makeSeries">
                        <xsl:with-param name="pubElement" select="$entry"/>
                    </xsl:call-template>
                    <xsl:text>.</xsl:text>
                </xsl:if>
            </xsl:when>
            <xsl:when test="$entry[@type='incollection']">
                    <!-- THE AUTHOR(S) -->
                <xsl:if test="$entry/t:analytic/t:author">
                    <xsl:call-template name="makeAuthors">
                        <xsl:with-param name="pubElement" select="$entry/t:analytic/t:author"/>
                    </xsl:call-template>
                    <xsl:text>: </xsl:text>
                </xsl:if>
                    <!-- THE ARTICLE TITLE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">sectionTitle</xsl:attribute>
                        <xsl:value-of select="normalize-space($entry/t:analytic/t:title[not(@type='short')])"/>
                    </xsl:element>
                    <xsl:text>, in: </xsl:text>
                    <!-- THE EDITOR(S) -->
                    <xsl:call-template name="makeAuthors">
                        <xsl:with-param name="pubElement" select="$entry/t:monogr/t:editor"/>
                        <xsl:with-param name="makeFirstAuthor" select="false()"/>
                    </xsl:call-template>
                    <xsl:choose>
                        <xsl:when test="count($entry/t:monogr/t:editor) = 1"><xsl:text> (Hg.), </xsl:text></xsl:when>
                        <xsl:when test="count($entry/t:monogr/t:editor) > 1"><xsl:text> (Hgg.), </xsl:text></xsl:when>
                    </xsl:choose>
                    <!-- THE COLLECTION TITLE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">bookTitle</xsl:attribute>
                        <xsl:value-of select="normalize-space($entry/t:monogr/t:title[@level='m'])"/>
                        <xsl:if test="$entry/t:monogr/t:biblScope[@unit='volume']">
                            <xsl:text> Bd. </xsl:text>
                            <xsl:value-of select="$entry/t:monogr/t:biblScope[@unit='volume']"/>
                        </xsl:if>
                    </xsl:element>
                    <xsl:text>, </xsl:text>
                    <xsl:choose>
                        <xsl:when test="$entry/t:monogr/t:title != 'Der neue Pauly (Onlineversion)'">
                            <!-- THE PLACE OF PUBLICATION -->
                            <xsl:call-template name="makePubPlace">
                                <xsl:with-param name="pubElement" select="$entry"/>
                            </xsl:call-template>
                            <xsl:element name="span">
                                <xsl:attribute name="class">publicationYear</xsl:attribute>
                                <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='publicationDate']"/>
                            </xsl:element>
                            <!-- THE PUBLICATION SERIES -->
                            <xsl:if test="$entry/t:series">
                                <xsl:text>, </xsl:text>
                                <xsl:call-template name="makeSeries">
                                    <xsl:with-param name="pubElement" select="$entry"/>
                                </xsl:call-template>
                            </xsl:if>
                            <!-- THE PAGES -->
                            <xsl:if test="$entry/t:monogr/t:biblScope[@unit='column' or @unit='page']">
                                <xsl:text>, </xsl:text>
                                <xsl:element name="span">
                                    <xsl:attribute name="class">pubPages</xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when test="$entry/t:monogr/t:biblScope[@unit='column']">
                                            <xsl:text>Sp. </xsl:text>
                                            <xsl:value-of select="replace($entry/t:monogr/t:biblScope[@unit='column'], '--', '–')"/>
                                        </xsl:when>
                                        <xsl:when test="$entry/t:monogr/t:biblScope[@unit='page']">
                                            <xsl:text>S. </xsl:text>
                                            <xsl:value-of select="replace($entry/t:monogr/t:biblScope[@unit='page'], '--', '–')"/>
                                        </xsl:when>
                                    </xsl:choose>
                                </xsl:element>
                            </xsl:if>
                            <xsl:text>.</xsl:text>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>URL: </xsl:text>
                            <xsl:value-of select="$entry/t:ref[@type='url']"/>
                            <xsl:text> (letzter Aufruf: </xsl:text>
                            <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='urldate']"/>
                            <xsl:text>).</xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
            </xsl:when>
            <xsl:when test="$entry[@type='article']">
                    <!-- THE AUTHOR(S) -->
                    <xsl:call-template name="makeAuthors">
                        <xsl:with-param name="pubElement" select="$entry/t:analytic/t:author"/>
                    </xsl:call-template>
                    <xsl:text>: </xsl:text>
                    <!-- THE ARTICLE TITLE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">articleTitle</xsl:attribute>
                        <xsl:value-of select="normalize-space($entry/t:analytic/t:title[not(@type='short')])"/>
                    </xsl:element>
                    <xsl:text>, in: </xsl:text>
                    <!-- THE JOURNAL TITLE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">bookTitle</xsl:attribute>
                        <xsl:value-of select="normalize-space($entry/t:monogr/t:title[@level='j'])"/>
                        <xsl:if test="$entry/t:monogr/t:biblScope[@unit='volume']">
                            <xsl:text> </xsl:text>
                            <xsl:value-of select="$entry/t:monogr/t:biblScope[@unit='volume']"/>
                        </xsl:if>
                    </xsl:element>
                    <xsl:text> (</xsl:text>
                    <xsl:element name="span">
                        <xsl:attribute name="class">publicationYear</xsl:attribute>
                        <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='publicationDate']"/>
                    </xsl:element>
                    <xsl:text>), </xsl:text>
                    <!-- THE PAGES -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">pubPages</xsl:attribute>
                        <xsl:choose>
                            <xsl:when test="$entry/t:monogr/t:biblScope[@unit='column']">
                                <xsl:text>Sp. </xsl:text>
                                <xsl:value-of select="replace($entry/t:monogr/t:biblScope[@unit='column'], '--', '–')"/>
                            </xsl:when>
                            <xsl:when test="$entry/t:monogr/t:biblScope[@unit='page']">
                                <xsl:text>S. </xsl:text>
                                <xsl:value-of select="replace($entry/t:monogr/t:biblScope[@unit='page'], '--', '–')"/>
                            </xsl:when>
                        </xsl:choose>
                    </xsl:element>
                    <xsl:text>.</xsl:text>
            </xsl:when>
            <xsl:when test="$entry[@type='misc']">
                    <!-- THE AUTHOR(S) -->
                    <xsl:call-template name="makeAuthors">
                        <xsl:with-param name="pubElement" select="$entry/t:analytic/t:author"/>
                    </xsl:call-template>
                    <xsl:if test="$entry/t:analytic/t:author">
                        <xsl:text>: </xsl:text>
                    </xsl:if>
                    <!-- THE ARTICLE TITLE -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">articleTitle</xsl:attribute>
                        <xsl:value-of select="normalize-space($entry/t:analytic/t:title[not(@type='short')])"/>
                    </xsl:element>
                    <xsl:text>, URL: </xsl:text>
                    <!-- THE URL -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">pubURL</xsl:attribute>
                        <xsl:value-of select="$entry/t:ref[@type='url']"/>
                    </xsl:element>
                    <!-- The URL Date -->
                    <xsl:text> (letzter Aufruf: </xsl:text>
                    <xsl:element name="span">
                        <xsl:attribute name="class">pubURLDate</xsl:attribute>
                        <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='urldate']"/>
                    </xsl:element>
                    <xsl:text>).</xsl:text>
            </xsl:when>
            <xsl:when test="$entry[@type='formula']">
                <!-- THE URL -->
                <xsl:value-of select="$entry/t:ref[@type='url']"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- THE AUTHOR(S) -->
                <xsl:call-template name="makeAuthors">
                    <xsl:with-param name="pubElement" select="$entry/t:analytic/t:author"/>
                </xsl:call-template>
                <xsl:if test="$entry/t:analytic/t:author">
                    <xsl:text>: </xsl:text>
                </xsl:if>
                <!-- THE ARTICLE TITLE -->
                <xsl:element name="span">
                    <xsl:attribute name="class">articleTitle</xsl:attribute>
                    <xsl:value-of select="normalize-space($entry/t:analytic/t:title[not(@type='short')])"/>
                </xsl:element>
                <xsl:text>, </xsl:text>
                <!-- THE PUBLICATION DATE -->
                <xsl:element name="span">
                    <xsl:attribute name="class">publicationYear</xsl:attribute>
                    <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='publicationDate']"/>
                </xsl:element>
                <xsl:if test="$entry/t:ref[@type='url']">                    
                    <xsl:text>, URL: </xsl:text>
                    <!-- THE URL -->
                    <xsl:element name="span">
                        <xsl:attribute name="class">pubURL</xsl:attribute>
                        <xsl:value-of select="$entry/t:ref[@type='url']"/>
                    </xsl:element>
                    <!-- The URL Date -->
                    <xsl:text> (letzter Aufruf: </xsl:text>
                    <xsl:element name="span">
                        <xsl:attribute name="class">pubURLDate</xsl:attribute>
                        <xsl:value-of select="$entry/t:monogr/t:imprint/t:date[@type='urldate']"/>
                    </xsl:element>
                    <xsl:text>).</xsl:text>
                </xsl:if>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="makeAuthors">
        <xsl:param name="pubElement"/>
        <xsl:param name="makeFirstAuthor" select="true()"/>
        <xsl:choose>
            <xsl:when test="count($pubElement) = 1">
                <xsl:call-template name="makeNames">
                    <xsl:with-param name="nameElement" select="$pubElement"/>
                    <xsl:with-param name="firstAuthor" select="$makeFirstAuthor"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="count($pubElement) = 2">
                <xsl:call-template name="makeNames">
                    <xsl:with-param name="nameElement" select="$pubElement[position() = 1]"/>
                    <xsl:with-param name="firstAuthor" select="$makeFirstAuthor"/>
                </xsl:call-template>
                <xsl:text> und </xsl:text>
                <xsl:call-template name="makeNames">
                    <xsl:with-param name="nameElement" select="$pubElement[position() = 2]"/>
                    <xsl:with-param name="firstAuthor" select="false()"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="count($pubElement) > 2">
                <xsl:call-template name="makeNames">
                    <xsl:with-param name="nameElement" select="$pubElement[position() = 1]"/>
                    <xsl:with-param name="firstAuthor" select="$makeFirstAuthor"/>
                </xsl:call-template>
                <xsl:for-each select="$pubElement[position() > 1 and position() &lt; last()]">
                    <xsl:text>, </xsl:text>
                    <xsl:call-template name="makeNames">
                        <xsl:with-param name="nameElement" select="."/>
                        <xsl:with-param name="firstAuthor" select="false()"/>
                    </xsl:call-template>
                </xsl:for-each>
                <xsl:text> und </xsl:text>
                <xsl:call-template name="makeNames">
                    <xsl:with-param name="nameElement" select="$pubElement[last()]"/>
                    <xsl:with-param name="firstAuthor" select="false()"/>
                </xsl:call-template>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="makeSeries">
        <xsl:param name="pubElement"/>
        <xsl:param name="endPunct"/>
        <xsl:if test="$pubElement/t:series">
            <xsl:text> (</xsl:text>
            <xsl:element name="span">
                <xsl:attribute name="class">publicationSeries</xsl:attribute>
                <xsl:value-of select="$pubElement/t:series/t:title[@level='s']"/>
                <xsl:if test="$pubElement/t:series/t:biblScope[@unit='volume']">
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="$pubElement/t:series/t:biblScope[@unit='volume']"/>
                </xsl:if>
            </xsl:element>
            <xsl:text>)</xsl:text>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="makePubPlace">
        <xsl:param name="pubElement"/>
        <xsl:if test="$pubElement/t:monogr/t:imprint/t:pubPlace">
            <xsl:element name="span">
                <xsl:attribute name="class">publicationPlace</xsl:attribute>
                <xsl:value-of select="$pubElement/t:monogr/t:imprint/t:pubPlace"/>
            </xsl:element>
            <xsl:text> </xsl:text>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="makeNames">
        <xsl:param name="nameElement"/>
        <xsl:param name="firstAuthor"/>
        <xsl:choose>
            <xsl:when test="$nameElement/t:surname">
                <xsl:choose>
                    <xsl:when test="$firstAuthor"> 
                        <xsl:element name="span">
                            <xsl:attribute name="class">surname</xsl:attribute>
                            <xsl:value-of select="$nameElement/t:surname/text()"/>
                        </xsl:element>
                        <xsl:text>, </xsl:text>
                        <xsl:element name="span">
                            <xsl:attribute name="class">forename</xsl:attribute>
                            <xsl:value-of select="$nameElement/t:forename/text()"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="span">
                            <xsl:attribute name="class">forename</xsl:attribute>
                            <xsl:value-of select="$nameElement/t:forename/text()"/>
                        </xsl:element>
                        <xsl:text> </xsl:text>
                        <xsl:element name="span">
                            <xsl:attribute name="class">surname</xsl:attribute>
                            <xsl:value-of select="$nameElement/t:surname/text()"/>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="span">
                    <xsl:attribute name="class">fullname</xsl:attribute>
                    <xsl:value-of select="$nameElement/text()"/>
                    <xsl:value-of select="$nameElement/t:surname/text()"/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>