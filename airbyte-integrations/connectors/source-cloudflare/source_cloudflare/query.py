# NOTE: THis here's a beefy query, so I decided to give it a file all it's own.

the_query = """
{
  viewer {
    zones(filter: { zoneTag: $tag }) {
      events: firewallEventsAdaptive(
        filter: {
          datetime_gt: $start
          datetime_lt: $end
        }
        limit: 10000
        orderBy: [
          datetime_DESC
        ]
      ) {
        action
        datetime
        apiGatewayMatchedEndpoint
        host: clientRequestHTTPHost
        path: clientRequestPath
        clientCountryName
        clientIP
        clientIPClass
        clientAsn
        clientASNDescription
        contentScanHasFailed
        contentScanNumObj
        contentScanNumMaliciousObj
        ref
        ruleId
        rulesetId
        wafAttackScore
        edgeResponseStatus
        source
        userAgent
        wafRceAttackScore
        wafSqliAttackScore
        wafXssAttackScore
      }
    }
  }
}
"""
