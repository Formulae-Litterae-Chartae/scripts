<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs tei"
    version="2.0">
    
    <xsl:output omit-xml-declaration="no" indent="yes"/>
    
    <xsl:variable name="titleNode" select="normalize-space(/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title)"/>
    <!-- Raw filename without extension -->
    <xsl:variable name="filenameRaw"
        select="tokenize(tokenize(base-uri(), '/')[last()], '\.')[1]"/>
    
    <!-- Normalize URL encoding a bit (add more replaces if needed) -->
    <xsl:variable name="filename" select="
        replace(
            replace(
                replace($filenameRaw, '%20', ' '),
                '%C3%9C', 'Ue'
            ),
            '%C3%BC', 'ue'
        )
                    "/>
    
    <xsl:variable name="titleParts" select="tokenize($filenameRaw, '%20')"/>
    <xsl:variable name="mainTitle" select="string-join($titleParts, ' ')"/>

    
    <xsl:variable name="resolvedTitle">
        <xsl:choose>
            <xsl:when test="$titleNode">
                <xsl:value-of select="$titleNode"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:message terminate="no">
                    Warning: TEI title is empty for this file (<xsl:value-of select="base-uri()" />). 
                    The filename (<xsl:value-of select="$titleParts[1]"/>) is used instead.
                </xsl:message>
                <xsl:value-of select="$mainTitle"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    

    
    <xsl:template match="/">
        <!-- Validate title format -->
        <xsl:if test="not(matches($resolvedTitle, '^Regesten [A-Za-z]+( [A-Za-z]+)?$'))">
            <xsl:message terminate="no">
                ⚠️ Warning: Resolved title '<xsl:value-of select="$resolvedTitle"/>' does not match expected format: Regesten [A-z]+ [A-z]?
            </xsl:message>
        </xsl:if>
        <xml><xsl:for-each select="/tei:TEI/tei:text/tei:body/tei:table/tei:row">
            <regest>
                <xsl:attribute name="docId">
<!--                    <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/>-->
                    <xsl:choose>
                            <xsl:when test="contains(lower-case($resolvedTitle), 'marculf')">
                                <xsl:choose>
                                    
                                    <!-- Marculf Ergänzungen: 1,1 -> 3_1_001 -->
                                    <xsl:when test="contains(lower-case($resolvedTitle), 'ergänzung') or contains(lower-case($resolvedTitle), 'ergaenzung')">
                                        <xsl:text>3_</xsl:text>
                                        <xsl:value-of select="replace(normalize-space(child::tei:cell[1]), '^(\d+),(\d+)$', '$1')"/>
                                        <xsl:text>_</xsl:text>
                                        <xsl:number value="replace(normalize-space(child::tei:cell[1]), '^(\d+),(\d+)$', '$2')" format="001"/>
                                    </xsl:when>
                                    
                                    <!-- Marculf II -> 2_001 / 2_002a -->
                                    <xsl:when test="matches($resolvedTitle, '(^| )II($| )')">
                                        <xsl:text>2_</xsl:text>
                                        <xsl:number value="replace(normalize-space(child::tei:cell[1]), '.*?(\d+).*', '$1')" format="001"/>
                                        <xsl:if test="matches(normalize-space(child::tei:cell[1]), '^\d+[a-z]$')">
                                            <xsl:value-of select="replace(normalize-space(child::tei:cell[1]), '^\d+([a-z])$', '$1')"/>
                                        </xsl:if>
                                    </xsl:when>
                                    
                                    <!-- Marculf I -> 1_001 -->
                                    <xsl:otherwise>
                                        <xsl:text>1_</xsl:text>
                                        <xsl:number value="replace(normalize-space(child::tei:cell[1]), '.*?(\d+).*', '$1')" format="001"/>
                                        <xsl:if test="matches(normalize-space(child::tei:cell[1]), '^\d+[a-z]$')">
                                            <xsl:value-of select="replace(normalize-space(child::tei:cell[1]), '^\d+([a-z])$', '$1')"/>
                                        </xsl:if>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:when>
                        <xsl:when test="contains(child::tei:cell[1]/., ',')">
                            <xsl:value-of select="replace(child::tei:cell[1]/., '.*(\d),.*', '$1')"/>
                                <xsl:text>_</xsl:text><xsl:number value="replace(child::tei:cell[1]/., '.*,(\d).*', '$1')" format="001"/>
                        </xsl:when>
                        <xsl:when test="contains(lower-case($resolvedTitle), 'tours_ueberarbeitung')">
                            <!-- <xsl:text>urn:cts:formulae:tours_ueberarbeitung.form</xsl:text> -->
                            <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,3})$', '$1')" format="001"/>
                            <xsl:if test="matches(child::tei:cell[1]/., '\([a-z]\)$')">
                                <xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)\(([a-z])\)$', '$2')"/>
                            </xsl:if>
                        </xsl:when>
                        <xsl:when test="contains(lower-case($resolvedTitle), 'tours')">
                            <xsl:text>urn:cts:formulae:tours.form</xsl:text>
                            <xsl:choose>
                                <xsl:when test="contains(child::tei:cell[1]/., 'Ergänzung')">
                                    <xsl:text>2_</xsl:text>
                                    <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,2})$', '$1')" format="001"/>
                                    <xsl:if test="matches(child::tei:cell[1]/., '.*?(\D{1,2})$')">
                                        <xsl:text>_</xsl:text>
                                        <xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)(\D{1,2})$', '$2')"/>
                                    </xsl:if>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,3})$', '$1')" format="001"/>
                                    <xsl:if test="matches(child::tei:cell[1]/., '\([a-z]\)$')">
                                        <xsl:text>_</xsl:text>
                                        <xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)\(([a-z])\)$', '$2')"/>
                                    </xsl:if>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:when>
                            <!-- urn:cts:formulae:bourges.form_c_001a -->
                            <xsl:when test="contains(lower-case($resolvedTitle), 'bourges') or 
                                            contains(lower-case($resolvedTitle), 'flavigny') or 
                                            contains(lower-case($resolvedTitle), 'fsb')">

                                <!-- 001 -->
                            <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,3})$', '$1')" format="001"/>
                                <!-- 001a -->
                                <xsl:if test="matches(child::tei:cell[1]/., '[a-z]$')">
                                    <xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)([a-z])$', '$2')"/>
                                </xsl:if>
                        </xsl:when>

                        <xsl:otherwise>
                            
                            <xsl:message terminate="yes">
                                Warning: There is no matching if-clause for (<xsl:value-of select="$titleParts[1]"/>). Need implementation. 
                            </xsl:message>
                            <xsl:comment>Entry in otherwise-style</xsl:comment>
                            <xsl:number value="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,2})$', '$1')" format="001"/><xsl:value-of select="replace(child::tei:cell[1]/., '.*?(\d+)(\D{0,2})$', '$2')"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
          
                
                <shortDesc><xsl:apply-templates select="child::tei:cell[2]/node()"></xsl:apply-templates></shortDesc>
                <longDesc><xsl:apply-templates select="child::tei:cell[3]/node()"></xsl:apply-templates></longDesc>

            </regest>
        </xsl:for-each></xml>
    </xsl:template>
    
    <xsl:template name="extract">
        <xsl:param name="docNum"/>
        <xsl:param name="long"/>
        <xsl:param name="short"/>
        <p><xsl:value-of select="$docNum"/><xsl:text>&#13;</xsl:text>
        <xsl:value-of select="$short"/><xsl:text>&#13;</xsl:text>
        <xsl:value-of select="$long"/><xsl:text>&#13;</xsl:text></p>
    </xsl:template>
    
    <xsl:template match="tei:hi[@rend='italic']">
        <xsl:text>&lt;seg class="latin-word"&gt;</xsl:text><xsl:value-of select="."/><xsl:text>&lt;/seg&gt;</xsl:text>
    </xsl:template>
    
</xsl:stylesheet>