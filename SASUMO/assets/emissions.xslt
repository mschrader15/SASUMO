<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
   <xsl:output method="text" indent="yes" omit-xml-declaration="yes"/>
   <xsl:strip-space elements="*"/>
   
   <xsl:template match ="/emission-export">
       <xsl:apply-templates select="emissions-export"/>
   </xsl:template>
   
   <xsl:template match="emissions-export">
        <!-- COLUMN HEADERS -->
        <xsl:text>timestep_time,vehicle_CO,vehicle_CO2,vehicle_HC,vehicle_NOx,vehicle_PMx,vehicle_angle,vehicle_eclass,vehicle_electricity,vehicle_fuel,vehicle_id,vehicle_lane,vehicle_noise,vehicle_pos,vehicle_route,vehicle_speed,vehicle_type,vehicle_waiting,vehicle_x,vehicle_y&#xa;</xsl:text>
        <xsl:apply-templates select="timestep-time"/>      
   </xsl:template>
   
   <xsl:template match="timestep-time">
       <xsl:variable name="delim">,</xsl:variable>
       <xsl:variable name="quote">&quot;</xsl:variable>
       <xsl:value-of select="concat($quote, timestep/@time, $quote, $delim,
                                    $quote, timestep/vehicle/@CO, $quote, $delim,
                                    $quote, timestep/vehicle/@CO2, $quote, $delim,
                                    $quote, timestep/vehicle/@HC, $quote, $delim,
                                    $quote, timestep/vehicle/@NOx, $quote, $delim,
                                    $quote, timestep/vehicle/@PMx, $quote, $delim,
                                    $quote, timestep/vehicle/@angle, $quote, $delim,
                                    $quote, timestep/vehicle/@eclass, $quote, $delim,
                                    $quote, timestep/vehicle/@electricity, $quote, $delim,
                                    $quote, timestep/vehicle/@fuel, $quote, $delim,
                                    $quote, timestep/vehicle/@id, $quote, $delim,
                                    $quote, timestep/vehicle/@lane, $quote, $delim,
                                    $quote, timestep/vehicle/@noise, $quote, $delim,
                                    $quote, timestep/vehicle/@pos, $quote, $delim,
                                    $quote, timestep/vehicle/@route, $quote, $delim,
                                    $quote, timestep/vehicle/@speed, $quote, $delim,
                                    $quote, timestep/vehicle/@type, $quote, $delim,
                                    $quote, timestep/vehicle/@waiting, $quote, $delim,
                                    $quote, timestep/vehicle/@x, $quote, $delim,
                                    $quote, timestep/vehicle/@y, $quote, $delim
                                    &#xa;)"/>
   </xsl:template>
   
</xsl:stylesheet>