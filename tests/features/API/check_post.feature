@MCC
@MCC_Check
@POST
@API
@ANY_ENV
Feature: Check API POST calls

  @TRID_C2396864
  Scenario: Endpoint: POST Check with all newest Checkers for JSON response - 200
    When POST "nc" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":"1.7","GDS2-parameter":"L4"
  
  @TRID_C2489167
  Scenario: Endpoint: POST Check with all newest Checkers for PDF response - 200
    When POST "nc" file by MCC /check endpoint with Checkers "All:newest" for "pdf" response
    Then the response status code is "200"
    Then the response contains "%PDF-"

  @TRID_C2489168
  Scenario: Endpoint: POST Check with all newest Checkers for HTML response - 200
    When POST "nc" file by MCC /check endpoint with Checkers "All:newest" for "html" response
    Then the response status code is "200"
    Then the response contains "<h1 style="margin-top:0px;">Results for"
    Then the response contains "ACDD-1.3 Check"
    Then the response contains "CF-1.7 Check"
    Then the response contains "GDS2-L4 Check"

  @TRID_C2489169
  Scenario: Endpoint: POST Check with ACDD v1.1 Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD:1.1" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":"1.1","CF-version":null,"GDS2-parameter":null},""

  @TRID_C2489170
  Scenario: Endpoint: POST Check with ACDD v1.3 Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD:1.3" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":null,"GDS2-parameter":null},""

  @TRID_C2489171
  Scenario: Endpoint: POST Check with CF v1.6 Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "CF:1.6" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":"1.6","GDS2-parameter":null},""

  @TRID_C2489172
  Scenario: Endpoint: POST Check with CF v1.7 Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "CF:1.7" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":"1.7","GDS2-parameter":null},""

  @TRID_C2489173
  Scenario: Endpoint: POST Check with GDS2 L2P Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2:L2P" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":null,"GDS2-parameter":"L2P"

  @TRID_C2489174
  Scenario: Endpoint: POST Check with GDS2 L3 Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2:L3" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":null,"GDS2-parameter":"L3"

  @TRID_C2489175
  Scenario: Endpoint: POST Check with GDS2 L4 Checker - 200
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2:L4" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":null,"GDS2-parameter":"L4"

  @TRID_C2489176
  Scenario: Endpoint: POST Check with only ACDD version, but no ACDD Checker parameter - 400
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD-None:1.3" for "json" response
    Then the response status code is "400"
    Then the response contains "You need to choose at least one metadata convention to test your file against.","error":"There was a problem with your request."
  
  @TRID_C2489177
  Scenario: Endpoint: POST Check with only CF version, but no CF Checker parameter - 400
    When POST "nc" file by MCC /check endpoint with Checkers "CF-None:1.7" for "json" response
    Then the response status code is "400"
    Then the response contains "You need to choose at least one metadata convention to test your file against.","error":"There was a problem with your request."

  @TRID_C2489178
  Scenario: Endpoint: POST Check with only GDS2 version, but no GDS2 Checker parameter - 400
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2-None:L4" for "json" response
    Then the response status code is "400"
    Then the response contains "You need to choose at least one metadata convention to test your file against.","error":"There was a problem with your request."

  @TRID_C2489179
  Scenario: Endpoint: POST Check with no Checkers - 400
    When POST "nc" file by MCC /check endpoint with Checkers " " for "json" response
    Then the response status code is "400"
    Then the response contains "You need to choose at least one metadata convention to test your file against.","error":"There was a problem with your request."

  @TRID_C2489180
  Scenario: Endpoint: POST Check with no version of ACDD Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.1, 1.3)"
  
  @TRID_C2489181
  Scenario: Endpoint: POST Check with empty version of ACDD Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD: " for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.1, 1.3)"
  
  @TRID_C2489182
  Scenario: Endpoint: POST Check with wrong version of ACDD Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD:asd" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.1, 1.3)"
  
  @TRID_C2489183
  Scenario: Endpoint: POST Check with no version of CF Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "CF" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.6, 1.7)"

  @TRID_C2489184
  Scenario: Endpoint: POST Check with empty version of CF Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "CF: " for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.6, 1.7)"

  @TRID_C2489185
  Scenario: Endpoint: POST Check with wrong version of CF Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "CF:asd" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.6, 1.7)"

  @TRID_C2489186
  Scenario: Endpoint: POST Check with no version of GDS2 Checker switch to default L2P - 200
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":null,"GDS2-parameter":"L2P"

  @TRID_C2489187
  Scenario: Endpoint: POST Check with empty version of GDS2 Checker switch to default L2P - 200
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2: " for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains "selected_checkers":{"ACDD-version":null,"CF-version":null,"GDS2-parameter":"L2P"

  @TRID_C2489188
  Scenario: Endpoint: POST Check with wrong version of GDS2 Checker switch to default L2P - 400
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2:asd" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify a GDS2 level in the format \"GDS2-parameter:xxx\". Available levels are ('L2P', 'L3', 'L4')""
  
  @TRID_C2489189
  Scenario: Endpoint: POST Check with wrong version of GDS2 and ACDD v1.3 Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "GDS2:asd, ACDD:1.3" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify a GDS2 level in the format \"GDS2-parameter:xxx\". Available levels are ('L2P', 'L3', 'L4')""
  
  @TRID_C2489190
  Scenario: Endpoint: POST Check with wrong version of ACDD and CF v1.7 Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "ACDD:asd, CF:1.7" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.1, 1.3)"
  
  @TRID_C2489191
  Scenario: Endpoint: POST Check with wrong version of CF and GDS2 L4 Checker - 400
    When POST "nc" file by MCC /check endpoint with Checkers "CF:asd, GDS2:L4" for "json" response
    Then the response status code is "400"
    Then the response contains "Must specify version in the format"
    Then the response contains "Available versions are (1.6, 1.7)"

  @TRID_C2489192
  Scenario: Endpoint: POST Check with no file parameter- 400
    When POST "None" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "400"
    Then the response contains "The browser (or proxy) sent a request that this server could not understand.","error":"There was a problem with your request."

  @TRID_C2489193
  Scenario: Endpoint: POST Check with empty file parameter - 400
    When POST " " file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "400"
    Then the response contains "The browser (or proxy) sent a request that this server could not understand.","error":"There was a problem with your request."
  
  @TRID_C2489194
  Scenario: Endpoint: POST Check with wrong file - 500
    Given create file "./tempdata/asd.nc" with content "{'qwerty':'123'}"
    When POST "./tempdata/asd.nc" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "500"
    Then the response contains "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.","error":"Unable to read file"
  
  @TRID_C2489195
  Scenario: Endpoint: POST Check with no responseType parameter - 400
    When POST "nc" file by MCC /check endpoint with Checkers "All:newest" for "None" response
    Then the response status code is "400"
    Then the response contains "You need to include"
    Then the response contains "in request body and choose response type (html, json, or pdf).","error":"There was a problem with your request."
  
  @TRID_C2489196
  Scenario: Endpoint: POST Check with empty responseType parameter - 400
    When POST "nc" file by MCC /check endpoint with Checkers "All:newest" for " " response
    Then the response status code is "400"
    Then the response contains "Invalid value for"
    Then the response contains "Accepted response types are html, json, and pdf.","error":"There was a problem with your request."
  
  @TRID_C2489197
  Scenario: Endpoint: POST Check with wrong responseType parameter - 400
    When POST "nc" file by MCC /check endpoint with Checkers "All:newest" for "asd" response
    Then the response status code is "400"
    Then the response contains "Invalid value for"
    Then the response contains "Accepted response types are html, json, and pdf.","error":"There was a problem with your request."

  @TRID_C4342782
  Scenario: Endpoint: POST Check with oversized file - 400
    Given create file "./tempdata/oversized.nc" that is equal to "1.5 gb"
    When POST "./tempdata/oversized.nc" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "400"
    Then the response contains "asdasd"
  
  @TRID_C4342783
  Scenario: Endpoint: POST Check with wrong file type - 500
    Given create file "./tempdata/asd.exe" with content "{'qwerty':'123'}"
    When POST "./tempdata/asd.exe" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "500"
    Then the response contains "Your file must be in an accepted data format - .gz, .bz2, .nc, .h5, .nc4 or .hdf. Filename: asd.exe","error":"Unable to read file"
  
  @TRID_C4342784
  Scenario: Endpoint: POST Check .gz file type with all newest Checkers - 200
    When POST "gz" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains ".gz"
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":"1.7","GDS2-parameter":"L4"
  
  @TRID_C4342785
  Scenario: Endpoint: POST Check .bz2 file type with all newest Checkers - 200
    When POST "bz2" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains ".bz2"
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":"1.7","GDS2-parameter":"L4"

  @TRID_C4342786
  Scenario: Endpoint: POST Check .h5 file type with all newest Checkers - 200
    When POST "h5" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains ".h5"
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":"1.7","GDS2-parameter":"L4"
    
  @TRID_C4342787
  Scenario: Endpoint: POST Check .nc4 file type with all newest Checkers - 200
    When POST "nc4" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains ".nc4"
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":"1.7","GDS2-parameter":"L4"
    
  @TRID_C4342788
  Scenario: Endpoint: POST Check .hdf file type with all newest Checkers - 200
    When POST "hdf" file by MCC /check endpoint with Checkers "All:newest" for "json" response
    Then the response status code is "200"
    Then the response contains "{"fn":""
    Then the response contains ".hdf"
    Then the response contains "selected_checkers":{"ACDD-version":"1.3","CF-version":"1.7","GDS2-parameter":"L4"